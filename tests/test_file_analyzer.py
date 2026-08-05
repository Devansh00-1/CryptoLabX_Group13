"""Unit tests for the FileAnalyzer class."""

from analysis.file_analyzer import FileAnalyzer


def test_character_count() -> None:
    assert FileAnalyzer.character_count("hello world") == 11


def test_word_count() -> None:
    assert FileAnalyzer.word_count("the quick brown fox") == 4


def test_line_count() -> None:
    assert FileAnalyzer.line_count("line1\nline2\nline3") == 3


def test_unique_character_count() -> None:
    assert FileAnalyzer.unique_character_count("abcabcabc") == 3


def test_letter_frequency() -> None:
    freq = FileAnalyzer.letter_frequency("AaBbCc")
    assert freq == {"a": 2, "b": 2, "c": 2}


def test_letter_frequency_ignores_non_letters() -> None:
    freq = FileAnalyzer.letter_frequency("a1 b2 c3!")
    assert freq == {"a": 1, "b": 1, "c": 1}
