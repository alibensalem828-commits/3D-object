"""Thin wrappers around the libraries that can actually type on your keyboard.

Two real backends (`pynput`, `pyautogui`) plus a `dry` one that prints the
keystrokes instead of sending them, so you can test a sheet safely.
"""

from __future__ import annotations

import sys
from typing import Protocol


class Keyboard(Protocol):
    name: str

    def press(self, char: str, shift: bool) -> None: ...

    def release(self, char: str, shift: bool) -> None: ...

    def panic(self) -> None:
        """Release anything that might still be held down."""


class DryKeyboard:
    """Prints what would be typed. Useful for checking a sheet without a game open."""

    name = "dry"

    def press(self, char: str, shift: bool) -> None:
        sys.stdout.write(char)
        sys.stdout.flush()

    def release(self, char: str, shift: bool) -> None:
        pass

    def panic(self) -> None:
        sys.stdout.write("\n")
        sys.stdout.flush()


class PynputKeyboard:
    """Preferred backend: fast, and it can hold Shift for the black keys."""

    name = "pynput"

    def __init__(self) -> None:
        from pynput.keyboard import Controller, Key, KeyCode

        self._controller = Controller()
        self._Key = Key
        self._KeyCode = KeyCode
        self._shift_depth = 0

    def _key(self, char: str):
        return self._KeyCode.from_char(char)

    def press(self, char: str, shift: bool) -> None:
        if shift:
            if self._shift_depth == 0:
                self._controller.press(self._Key.shift)
            self._shift_depth += 1
        self._controller.press(self._key(char))

    def release(self, char: str, shift: bool) -> None:
        self._controller.release(self._key(char))
        if shift and self._shift_depth > 0:
            self._shift_depth -= 1
            if self._shift_depth == 0:
                self._controller.release(self._Key.shift)

    def panic(self) -> None:
        if self._shift_depth:
            self._shift_depth = 0
        try:
            self._controller.release(self._Key.shift)
        except Exception:
            pass


class PyAutoGUIKeyboard:
    """Fallback backend. Works everywhere but is noticeably slower per key."""

    name = "pyautogui"

    def __init__(self) -> None:
        import pyautogui

        pyautogui.PAUSE = 0  # we do our own timing
        pyautogui.FAILSAFE = True  # slam the mouse into a corner to abort
        self._gui = pyautogui
        self._shift_depth = 0

    def press(self, char: str, shift: bool) -> None:
        if shift:
            if self._shift_depth == 0:
                self._gui.keyDown("shift")
            self._shift_depth += 1
        self._gui.keyDown(char.lower())

    def release(self, char: str, shift: bool) -> None:
        self._gui.keyUp(char.lower())
        if shift and self._shift_depth > 0:
            self._shift_depth -= 1
            if self._shift_depth == 0:
                self._gui.keyUp("shift")

    def panic(self) -> None:
        self._shift_depth = 0
        try:
            self._gui.keyUp("shift")
        except Exception:
            pass


BACKENDS = {"pynput": PynputKeyboard, "pyautogui": PyAutoGUIKeyboard, "dry": DryKeyboard}


def create(name: str = "auto") -> Keyboard:
    if name != "auto":
        if name not in BACKENDS:
            raise ValueError(f"unknown backend {name!r}; pick one of {sorted(BACKENDS)}")
        return BACKENDS[name]()

    errors = []
    for candidate in ("pynput", "pyautogui"):
        try:
            return BACKENDS[candidate]()
        except Exception as exc:  # ImportError, or no display available
            errors.append(f"  {candidate}: {exc}")
    raise RuntimeError(
        "No keyboard backend available. Install one with:\n"
        "  pip install pynput\n"
        "Details:\n" + "\n".join(errors)
    )
