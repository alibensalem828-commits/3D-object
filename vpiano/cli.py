"""Command line entry point: python -m vpiano <sheet>"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import backends, keymap, midifile
from .player import Options, Player, watch_for_stop
from .sheet import SheetError, load

SONGS_DIR = Path(__file__).parent / "songs"


def _list_songs() -> int:
    sheets = sorted(SONGS_DIR.glob("*.txt"))
    if not sheets:
        print("No sheets found in", SONGS_DIR)
        return 1
    print("Available sheets:")
    for path in sheets:
        try:
            sheet = load(path)
            print(f"  {path.stem:<24} {sheet.tempo:g} bpm, {sheet.duration:5.1f}s, {len(sheet.events)} events")
        except SheetError as exc:
            print(f"  {path.stem:<24} (broken: {exc})")
    return 0


def _resolve(name: str) -> Path:
    candidate = Path(name)
    if candidate.is_file():
        return candidate
    for guess in (SONGS_DIR / name, SONGS_DIR / f"{name}.txt"):
        if guess.is_file():
            return guess
    raise SystemExit(f"No sheet named {name!r}. Try --list.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vpiano",
        description="Play a sheet on an on-screen piano by driving the keyboard.",
        epilog="Press ESC at any time to stop. Focus the game window during the countdown.",
    )
    parser.add_argument("sheet", nargs="?", help="sheet name (see --list), a .txt sheet, or a .mid file")
    parser.add_argument("--list", action="store_true", help="list the bundled sheets and exit")
    parser.add_argument("--save", metavar="FILE", help="write the sheet out as editable text and exit")
    parser.add_argument("--midi-tempo", type=float, default=150.0, help="grid tempo used when converting a MIDI file")
    parser.add_argument("--midi-quantize", type=float, default=0.5, help="shortest note kept when converting (in units)")
    parser.add_argument("--midi-voices", type=int, default=6, help="max simultaneous notes kept from a MIDI chord")
    parser.add_argument("--backend", default="auto", choices=["auto", *backends.BACKENDS], help="how to send keystrokes")
    parser.add_argument("--dry-run", action="store_true", help="print the keystrokes instead of typing them")
    parser.add_argument("--speed", type=float, default=1.0, help="tempo multiplier (0.5 = half speed)")
    parser.add_argument("--tempo", type=float, help="override the sheet's bpm outright")
    parser.add_argument("--transpose", type=int, default=0, help="shift everything by N semitones")
    parser.add_argument("--hold", type=float, help="fraction of each slot a key stays down (0.1-1.0)")
    parser.add_argument("--countdown", type=int, default=5, help="seconds before the first note (0 to disable)")
    parser.add_argument(
        "--start-key",
        metavar="KEY",
        help="wait for this key (e.g. f9) instead of counting down — click the piano first, then press it",
    )
    parser.add_argument(
        "--no-focus-guard",
        action="store_true",
        help="play even if this terminal still has the focus (Windows only check)",
    )
    parser.add_argument("--loop", type=int, default=1, help="play the sheet N times")
    parser.add_argument("--quiet", action="store_true", help="do not print section names while playing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        return _list_songs()
    if not args.sheet:
        build_parser().print_help()
        return 2

    path = _resolve(args.sheet)
    try:
        if path.suffix.lower() in (".mid", ".midi"):
            sheet = midifile.convert(
                path,
                tempo=args.midi_tempo,
                quantize=args.midi_quantize,
                max_voices=args.midi_voices,
            )
            skipped = getattr(sheet, "skipped_notes", 0)
            print(f"Converted {path.name}: {len(sheet.events)} events" + (f", {skipped} note(s) dropped" if skipped else ""))
        else:
            sheet = load(path)
    except (SheetError, midifile.MidiError) as exc:
        print(f"Could not read {path}: {exc}", file=sys.stderr)
        return 1

    if args.tempo:
        sheet.tempo = args.tempo

    if args.save:
        out = Path(args.save)
        out.write_text(midifile.to_text(sheet), encoding="utf-8")
        print(f"Wrote {out} ({len(sheet.events)} events). Edit it, then play it with:")
        print(f"    python -m vpiano {out}")
        return 0

    backend_name = "dry" if args.dry_run else args.backend
    try:
        keyboard = backends.create(backend_name)
    except (RuntimeError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    options = Options(
        transpose=args.transpose,
        speed=args.speed,
        hold=args.hold,
        countdown=max(0, args.countdown),
        start_key=args.start_key,
        verbose=not args.quiet,
        guard_focus=not args.no_focus_guard,
    )
    if backend_name == "dry":
        # Nothing is actually typed, so neither the focus guard nor the start
        # key make sense here.
        options.guard_focus = False
        options.start_key = None
    player = Player(keyboard, options)

    out_of_range = [
        n for ev in sheet.events for n in ev.notes
        if keymap.NOTE_PITCH[n] + args.transpose not in keymap.PITCH_TO_NOTE
    ]
    if out_of_range:
        print(f"  note: {len(out_of_range)} note(s) fall outside the 61-key range and will be skipped")

    print(f"Sheet    : {sheet.title}  ({path})")
    print(f"Tempo    : {sheet.tempo:g} bpm x{args.speed:g}   Duration: {sheet.duration / max(args.speed, 0.01):.1f}s")
    print(f"Backend  : {keyboard.name}")
    if backend_name != "dry":
        if args.start_key:
            print("Keystrokes go to whatever window has the focus. Press ESC to stop.")
        else:
            print("Click on the game window NOW — keystrokes go to whatever has focus.")
            print("Press ESC to stop.")

    listener = watch_for_stop(player) if backend_name != "dry" else None

    finished = True
    try:
        for run in range(max(1, args.loop)):
            if args.loop > 1:
                print(f"--- pass {run + 1}/{args.loop} ---")
            finished = player.play(sheet)
            if not finished:
                break
            player.options.countdown = 0
            player.options.start_key = None
    except KeyboardInterrupt:
        finished = False
        player.stop_event.set()
    finally:
        player.release_all()
        if listener is not None:
            listener.stop()

    print("\nDone." if finished else "\nStopped.")
    return 0 if finished else 130


if __name__ == "__main__":
    raise SystemExit(main())
