"""Styled logging utilities for CryptoLabX.

Writes decorative, structured log entries to the execution log file
inside the ``outputs`` folder. Only the log file output is affected;
console output is left unchanged.

Example of a log entry written by :func:`log_menu_selection`::

    ┌──────────────────────────────┐
    │ Date   : 2026-08-05          │
    │ Time   : 23:10:09            │
    │ Action : Exit                │
    │ Option : 5                   │
    └──────────────────────────────┘
    ──────────────────────────────
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Default path to the execution log file, relative to the project root.
DEFAULT_LOG_FILE = Path(__file__).resolve().parent.parent / "outputs" / "execution_log.txt"

# Map numeric menu choices to descriptive action names.
MENU_ACTIONS = {
    "1": "Encrypt",
    "2": "Decrypt",
    "3": "Attack",
    "4": "Analyze",
    "5": "Exit",
}


def _timestamp() -> datetime:
    """Return the current local time."""
    return datetime.now()


def _action_name(option: str) -> str:
    """Return a descriptive action name for a raw menu option string."""
    return MENU_ACTIONS.get(option, "Unknown / Invalid")


def _inner_lines(lines: List[Tuple[str, str]]) -> List[str]:
    """Render label/value pairs into padded inner box lines."""
    return [f"{label} : {value}" for label, value in lines]


def _write(entry: str, log_file: Path = DEFAULT_LOG_FILE) -> None:
    """Append a formatted entry to the log file."""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as file:
        file.write(entry)


def log_session_start(log_file: Path = DEFAULT_LOG_FILE) -> None:
    """Write a decorative session-start banner to the log file."""
    now = _timestamp()
    entry = (
        "\n"
        "═══════════════════════════════════════════════════\n"
        "               CryptoLabX Session Started\n"
        f"       {now.strftime('%Y-%m-%d')}  |  {now.strftime('%H:%M:%S')}\n"
        "═══════════════════════════════════════════════════\n"
    )
    _write(entry, log_file)


def log_session_end(log_file: Path = DEFAULT_LOG_FILE) -> None:
    """Write a decorative session-closing banner to the log file."""
    now = _timestamp()
    entry = (
        "\n"
        "═══════════════════════════════════════════════════\n"
        "               CryptoLabX Session Ended\n"
        f"       {now.strftime('%Y-%m-%d')}  |  {now.strftime('%H:%M:%S')}\n"
        "═══════════════════════════════════════════════════\n"
    )
    _write(entry, log_file)


def log_menu_selection(option: str, log_file: Path = DEFAULT_LOG_FILE) -> None:
    """Write a boxed, structured log entry for the selected menu option.

    Parameters
    ----------
    option:
        The raw menu option entered by the user (e.g. ``"4"``).
    log_file:
        Path to the log file to append to.
    """
    now = _timestamp()
    lines = [
        ("Date", now.strftime("%Y-%m-%d")),
        ("Time", now.strftime("%H:%M:%S")),
        ("Action", _action_name(option)),
        ("Option", option),
    ]

    inner = _inner_lines(lines)
    inner_width = max(len(line) for line in inner)
    box_width = inner_width + 4

    box = ["┌" + "─" * (inner_width + 2) + "┐"]
    for line in inner:
        box.append("│ " + line.ljust(inner_width) + " │")
    box.append("└" + "─" * (inner_width + 2) + "┘")

    entry = "\n" + "\n".join(box) + "\n" + "─" * box_width + "\n"
    _write(entry, log_file)

