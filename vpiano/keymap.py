"""Mapping between musical note names and the Virtual Piano keyboard layout.

The on-screen keyboard spans 61 keys, C2 -> C7:

    white keys : 1234567890 qwertyuiop asdfghjkl zxcvbnm   (36 keys)
    black keys : !@ $%^ *( QWE TY IOP SD GHJ LZ CVB        (25 keys)

A black key is simply the white key's character typed with Shift held down.
"""

from __future__ import annotations

WHITE_CHARS = "1234567890qwertyuiopasdfghjklzxcvbnm"
BLACK_CHARS = "!@$%^*(QWETYIOPSDGHJLZCVB"

WHITE_STEPS = ["C", "D", "E", "F", "G", "A", "B"]
SHARP_ROOTS = ["C", "D", "F", "G", "A"]  # white notes that own a black key

LOWEST_OCTAVE = 2
HIGHEST_OCTAVE = 7  # only C7 exists at the top

# Semitone offset of each note name inside an octave, used for ordering.
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Enharmonic spellings we accept in sheet files.
FLAT_TO_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "Cb": "B",
    "Fb": "E",
}


def _build_tables() -> tuple[dict[str, str], dict[str, int]]:
    """Return (note -> keyboard char) and (note -> midi-ish pitch index)."""
    notes_to_char: dict[str, str] = {}
    pitch: dict[str, int] = {}

    whites: list[str] = []
    blacks: list[str] = []
    for octave in range(LOWEST_OCTAVE, HIGHEST_OCTAVE + 1):
        for step in WHITE_STEPS:
            name = f"{step}{octave}"
            whites.append(name)
            if step in SHARP_ROOTS:
                blacks.append(f"{step}#{octave}")
            if name == f"C{HIGHEST_OCTAVE}":
                break
        if octave == HIGHEST_OCTAVE:
            break

    for name, char in zip(whites, WHITE_CHARS):
        notes_to_char[name] = char
    for name, char in zip(blacks, BLACK_CHARS):
        notes_to_char[name] = char

    for name in notes_to_char:
        step = name[0]
        sharp = "#" in name
        octave = int(name[-1])
        pitch[name] = 12 * octave + SEMITONES[step] + (1 if sharp else 0)

    return notes_to_char, pitch


NOTE_TO_CHAR, NOTE_PITCH = _build_tables()
PITCH_TO_NOTE = {v: k for k, v in sorted(NOTE_PITCH.items(), key=lambda kv: kv[1])}
CHAR_TO_NOTE = {v: k for k, v in NOTE_TO_CHAR.items()}

LOWEST_PITCH = min(NOTE_PITCH.values())
HIGHEST_PITCH = max(NOTE_PITCH.values())


class OutOfRange(ValueError):
    """Raised when a note falls outside the 61-key on-screen piano."""


def normalise(note: str) -> str:
    """Accept 'bb4', 'Bb4', 'A#4' and return the canonical 'A#4'."""
    note = note.strip()
    if len(note) < 2:
        raise ValueError(f"unreadable note: {note!r}")
    octave = note[-1]
    if not octave.isdigit():
        raise ValueError(f"note {note!r} is missing its octave number")
    body = note[:-1]
    body = body[0].upper() + body[1:].lower().replace("♯", "#").replace("♭", "b")
    if body in FLAT_TO_SHARP:
        body = FLAT_TO_SHARP[body]
    return f"{body}{octave}"


def note_to_char(note: str, transpose: int = 0) -> str:
    """Translate a note name into the keyboard character that plays it."""
    name = normalise(note)
    if name not in NOTE_PITCH:
        raise ValueError(f"unknown note: {note!r}")
    target = NOTE_PITCH[name] + transpose
    if target not in PITCH_TO_NOTE:
        raise OutOfRange(f"{name} transposed by {transpose} leaves the keyboard")
    return NOTE_TO_CHAR[PITCH_TO_NOTE[target]]


def needs_shift(char: str) -> bool:
    return char in BLACK_CHARS


def chromatic_between(low: str, high: str) -> list[str]:
    """Every note from `low` to `high` inclusive, ascending or descending."""
    a, b = NOTE_PITCH[normalise(low)], NOTE_PITCH[normalise(high)]
    step = 1 if b >= a else -1
    out = []
    for p in range(a, b + step, step):
        if p in PITCH_TO_NOTE:
            out.append(PITCH_TO_NOTE[p])
    return out


def white_between(low: str, high: str) -> list[str]:
    """Same as chromatic_between but white keys only — a real piano glissando."""
    return [n for n in chromatic_between(low, high) if "#" not in n]
