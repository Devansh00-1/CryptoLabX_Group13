"""Text file analysis utilities for CryptoLabX.

Provides the FileAnalyzer class which reads a text file from the
datasets folder and produces statistics such as character count,
word count, line count, unique character count, and letter frequency.
"""

from collections import Counter
from pathlib import Path
from typing import Dict


class FileAnalyzer:
    """Read and analyze a text file."""

    def __init__(self, filepath: str) -> None:
        """Store the file path for later reading."""
        self.filepath = Path(filepath)

    def read(self) -> str:
        """Read the file contents as text."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")
        return self.filepath.read_text(encoding="utf-8")

    @staticmethod
    def character_count(text: str) -> int:
        """Return the total number of characters (including whitespace)."""
        return len(text)

    @staticmethod
    def word_count(text: str) -> int:
        """Return the number of words (space-separated tokens)."""
        return len(text.split())

    @staticmethod
    def line_count(text: str) -> int:
        """Return the number of lines."""
        return len(text.splitlines())

    @staticmethod
    def unique_character_count(text: str) -> int:
        """Return the number of distinct characters."""
        return len(set(text))

    @staticmethod
    def letter_frequency(text: str) -> Dict[str, int]:
        """Return the frequency of each letter (A-Z), case-insensitive."""
        letters = [ch.lower() for ch in text if ch.isalpha()]
        return dict(Counter(letters).most_common())

    def analyze(self) -> Dict[str, object]:
        """Perform a full analysis of the file and return the results."""
        text = self.read()
        return {
            "characters": self.character_count(text),
            "words": self.word_count(text),
            "lines": self.line_count(text),
            "unique_characters": self.unique_character_count(text),
            "letter_frequency": self.letter_frequency(text),
        }

    def print_report(self) -> None:
        """Print a human-readable analysis report."""
        results = self.analyze()
        print("\n--- File Analysis Report ---")
        print(f"File          : {self.filepath}")
        print(f"Characters    : {results['characters']}")
        print(f"Words         : {results['words']}")
        print(f"Lines         : {results['lines']}")
        print(f"Unique chars  : {results['unique_characters']}")
        print("\nLetter Frequency (A-Z):")
        for letter, count in results["letter_frequency"].items():
            print(f"  {letter.upper()}: {count}")
        print("----------------------------")
