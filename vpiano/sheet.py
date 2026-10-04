"""Parser for the little sheet-music language used by this project.

A sheet file is plain text. Blank lines and anything after `;` or `#` is ignored.

Directives (one per line, anywhere in the file):

    @tempo 160          beats per minute
    @unit 16            note values are 1/16th of a whole note (4 = quarter...)
    @hold 0.85          fraction of its slot a key stays pressed (0.1 - 1.0)

Sections are declared with `:name` and are purely cosmetic (they show up in
the playback log so you can see where you are in the piece).

Everything else is a stream of events:

    E4                  one note, one unit long
    E4:4                one note, four units long
    [E3 B3 E4]          a chord (all keys pressed together)
    [E3 B3 E4]:8        a chord held for eight units
    ~                   a rest of one unit
    ~:8                 a rest of eight units
    gliss(C4,C6,8)      a white-key run from C4 to C6 spread over 8 units
    gliss#(C4,C6,8)     the same run, but chromatic (uses black keys too)

Any line may end with `x3` to repeat that whole line three times.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import keymap


@dataclass
class Event:
    """One thing that happens at one moment: notes (possibly none) + a length."""

    notes: list[str]
    units: float
    section: str = ""

    @property
    def is_rest(self) -> bool:
        return not self.notes


@dataclass
class Sheet:
    title: str = "untitled"
    tempo: float = 120.0
    unit: int = 16
    hold: float = 0.85
    events: list[Event] = field(default_factory=list)

    @property
    def seconds_per_unit(self) -> float:
        # A beat is a quarter note; `unit` says how many of our units fit in a whole note.
        return (60.0 / self.tempo) * (4.0 / self.unit)

    @property
    def duration(self) -> float:
        return sum(e.units for e in self.events) * self.seconds_per_unit


_GLISS = re.compile(r"^gliss(#?)\(([^,]+),([^,]+),([0-9.]+)\)$", re.IGNORECASE)
_REPEAT = re.compile(r"\s+x(\d+)\s*$", re.IGNORECASE)
_TOKEN = re.compile(r"\[[^\]]*\](?::[0-9.]+)?|[^\s]+")


class SheetError(ValueError):
    pass


def _split_length(token: str) -> tuple[str, float]:
    """Pull the `:length` suffix off a token, defaulting to one unit."""
    head, sep, tail = token.rpartition(":")
    if not sep or not head:
        return token, 1.0
    try:
        return head, float(tail)
    except ValueError as exc:
        raise SheetError(f"bad note length in {token!r}") from exc


def _parse_token(token: str, section: str) -> list[Event]:
    body, units = _split_length(token)

    if body == "~":
        return [Event([], units, section)]

    gliss = _GLISS.match(body)
    if gliss:
        chromatic, low, high, span = gliss.groups()
        pick = keymap.chromatic_between if chromatic else keymap.white_between
        notes = pick(low.strip(), high.strip())
        if not notes:
            raise SheetError(f"empty glissando: {token!r}")
        each = float(span) / len(notes)
        return [Event([n], each, section) for n in notes]

    if body.startswith("["):
        if not body.endswith("]"):
            raise SheetError(f"unclosed chord: {token!r}")
        notes = body[1:-1].replace(",", " ").split()
        if not notes:
            raise SheetError(f"empty chord: {token!r}")
        return [Event([keymap.normalise(n) for n in notes], units, section)]

    return [Event([keymap.normalise(body)], units, section)]


def parse(text: str, title: str = "untitled") -> Sheet:
    sheet = Sheet(title=title)
    section = ""

    for lineno, raw in enumerate(text.splitlines(), start=1):
        # `;` always starts a comment; `#` only does at the start of a line,
        # because it is also the sharp sign inside note names like C#4.
        if raw.lstrip().startswith("#"):
            continue
        line = raw.split(";")[0].strip()
        if not line:
            continue

        if line.startswith("@"):
            parts = line[1:].split()
            if len(parts) != 2:
                raise SheetError(f"line {lineno}: directive needs one value: {line!r}")
            name, value = parts[0].lower(), parts[1]
            try:
                if name == "tempo":
                    sheet.tempo = float(value)
                elif name == "unit":
                    sheet.unit = int(value)
                elif name == "hold":
                    sheet.hold = min(1.0, max(0.05, float(value)))
                elif name == "title":
                    sheet.title = value
                else:
                    raise SheetError(f"line {lineno}: unknown directive @{name}")
            except ValueError as exc:
                raise SheetError(f"line {lineno}: bad value for @{name}: {value!r}") from exc
            continue

        if line.startswith(":"):
            section = line[1:].strip()
            continue

        repeat = 1
        match = _REPEAT.search(line)
        if match:
            repeat = int(match.group(1))
            line = line[: match.start()].strip()

        try:
            events: list[Event] = []
            for token in _TOKEN.findall(line):
                events.extend(_parse_token(token, section))
        except (SheetError, ValueError) as exc:
            raise SheetError(f"line {lineno}: {exc}") from exc

        sheet.events.extend(events * repeat)

    if not sheet.events:
        raise SheetError("this sheet contains no notes")
    return sheet


def load(path: str | Path) -> Sheet:
    path = Path(path)
    return parse(path.read_text(encoding="utf-8"), title=path.stem)
