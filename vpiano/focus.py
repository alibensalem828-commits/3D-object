"""Detect whether our own console window is the one that has focus.

If it is, playing would type the whole piece into the terminal instead of the
piano. On Windows we can check this with the stdlib; elsewhere we just don't
know and say so.
"""

from __future__ import annotations

import sys


def console_has_focus() -> bool | None:
    """True/False on Windows, None when we cannot tell."""
    if sys.platform != "win32":
        return None
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        console = kernel32.GetConsoleWindow()
        if not console:
            return None
        foreground = user32.GetForegroundWindow()
        if not foreground:
            return None
        return bool(console == foreground)
    except Exception:
        return None
