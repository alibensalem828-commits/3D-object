"""Playback engine: turns a parsed Sheet into timed keystrokes."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from . import focus, keymap
from .backends import Keyboard
from .sheet import Sheet


@dataclass
class Options:
    transpose: int = 0
    speed: float = 1.0  # 1.0 = written tempo, 2.0 = twice as fast
    hold: float | None = None  # overrides the sheet's @hold
    countdown: int = 5
    start_key: str | None = None  # wait for this key instead of counting down
    verbose: bool = True
    skip_out_of_range: bool = True
    guard_focus: bool = True  # refuse to play into our own terminal


class Player:
    def __init__(self, keyboard: Keyboard, options: Options | None = None) -> None:
        self.keyboard = keyboard
        self.options = options or Options()
        self.stop_event = threading.Event()
        self._held: set[tuple[str, bool]] = set()

    # -- key handling ----------------------------------------------------

    def _chars_for(self, notes: list[str]) -> list[str]:
        chars = []
        for note in notes:
            try:
                chars.append(keymap.note_to_char(note, self.options.transpose))
            except keymap.OutOfRange:
                if not self.options.skip_out_of_range:
                    raise
        return chars

    def _press(self, chars: list[str]) -> None:
        for char in chars:
            shift = keymap.needs_shift(char)
            self.keyboard.press(char, shift)
            self._held.add((char, shift))

    def _release(self, chars: list[str]) -> None:
        for char in chars:
            shift = keymap.needs_shift(char)
            self.keyboard.release(char, shift)
            self._held.discard((char, shift))

    def release_all(self) -> None:
        for char, shift in list(self._held):
            try:
                self.keyboard.release(char, shift)
            except Exception:
                pass
        self._held.clear()
        self.keyboard.panic()

    # -- timing ----------------------------------------------------------

    def _sleep_until(self, deadline: float) -> bool:
        """Wait until `deadline`. Returns False if we were asked to stop."""
        while True:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                return not self.stop_event.is_set()
            # Short waits keep the stop key responsive; the last millisecond
            # is a busy-wait because sleep() is not precise enough at 16th
            # notes above ~200 bpm.
            if remaining > 0.002:
                if self.stop_event.wait(min(remaining - 0.001, 0.05)):
                    return False
            elif self.stop_event.is_set():
                return False

    # -- start trigger ---------------------------------------------------

    def _wait_for_start_key(self, key_name: str) -> bool:
        """Block until the user presses the trigger key anywhere on the system."""
        try:
            from pynput import keyboard as pk
        except Exception:
            print("  (pynput unavailable, falling back to a 5s countdown)")
            return self.stop_event.wait(5.0) is False

        target = getattr(pk.Key, key_name.lower(), None)
        if target is None:
            target = pk.KeyCode.from_char(key_name[0].lower())

        pressed = threading.Event()

        def on_press(key):
            if key == target:
                pressed.set()
                return False
            return True

        print(f"  Click on the piano window, then press {key_name.upper()} to start (ESC cancels).")
        with pk.Listener(on_press=on_press) as listener:
            while not pressed.is_set():
                if self.stop_event.wait(0.05):
                    listener.stop()
                    print("  cancelled.")
                    return False
        # Give the key time to come back up so it is not still down when we play.
        time.sleep(0.15)
        return True

    # -- main loop -------------------------------------------------------

    def play(self, sheet: Sheet) -> bool:
        """Play the sheet. Returns True if it finished, False if interrupted."""
        opts = self.options
        unit = sheet.seconds_per_unit / max(opts.speed, 0.01)
        hold_ratio = opts.hold if opts.hold is not None else sheet.hold

        if opts.start_key:
            if not self._wait_for_start_key(opts.start_key):
                return False
        elif opts.countdown:
            for remaining in range(opts.countdown, 0, -1):
                print(f"  starting in {remaining}...", end="\r", flush=True)
                if self.stop_event.wait(1.0):
                    print("\n  cancelled before the first note.")
                    return False
            print("  go!" + " " * 20)

        if opts.guard_focus and focus.console_has_focus():
            print(
                "\n  ABORTED: this terminal still has the focus, so the whole piece\n"
                "  would be typed in here instead of the piano.\n"
                "  Click on the piano window first, then start again.\n"
                "  Tip: --start-key f9 lets you click first and press F9 when ready."
            )
            return False

        section = None
        start = time.perf_counter()
        cursor = 0.0  # position in the piece, in units

        try:
            for event in sheet.events:
                if self.stop_event.is_set():
                    return False

                if opts.verbose and event.section != section:
                    section = event.section
                    if section:
                        print(f"  [{section}]")

                slot = event.units * unit
                note_on = start + cursor * unit
                note_off = note_on + slot * hold_ratio
                cursor += event.units

                if not self._sleep_until(note_on):
                    return False

                if event.is_rest:
                    continue

                chars = self._chars_for(event.notes)
                if not chars:
                    continue

                self._press(chars)
                if not self._sleep_until(note_off):
                    self._release(chars)
                    return False
                self._release(chars)

            self._sleep_until(start + cursor * unit)
            return not self.stop_event.is_set()
        finally:
            self.release_all()


def watch_for_stop(player: Player, key_name: str = "esc") -> threading.Thread | None:
    """Listen globally for the panic key so a runaway piece can be killed."""
    try:
        from pynput import keyboard as pk
    except Exception:
        return None

    target = getattr(pk.Key, key_name, pk.Key.esc)

    def on_press(key):
        if key == target:
            player.stop_event.set()
            return False
        return True

    listener = pk.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener
