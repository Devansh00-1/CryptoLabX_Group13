"""Brute-force and dictionary-based attacks against a shift cipher."""

from dataclasses import dataclass
from pathlib import Path
import re

from .shift_cipher import decrypt


@dataclass(frozen=True)
class Candidate:
	"""A possible plaintext produced by a shift."""

	shift: int
	plaintext: str
	score: int = 0


def load_dictionary(dictionary_path: str | Path) -> set[str]:
	"""Load one lowercase word per line from ``dictionary_path``."""
	path = Path(dictionary_path)
	words = set()

	with path.open(encoding="utf-8") as dictionary_file:
		for line in dictionary_file:
			word = line.strip().lower()
			if word and word.isalpha():
				words.add(word)

	return words


def _words(text: str) -> list[str]:
	"""Return alphabetic words from text without changing its content."""
	return re.findall(r"[A-Za-z]+", text.lower())


def dictionary_score(text: str, dictionary: set[str]) -> int:
	"""Count how many complete words in ``text`` occur in ``dictionary``."""
	return sum(word in dictionary for word in _words(text))


def brute_force_attack(ciphertext: str) -> list[Candidate]:
	"""Return all possible plaintexts, ordered by shift from 0 through 25."""
	return [
		Candidate(shift=shift, plaintext=decrypt(ciphertext, shift))
		for shift in range(26)
	]


def dictionary_attack(
	ciphertext: str,
	dictionary: set[str] | None = None,
	dictionary_path: str | Path | None = None,
) -> list[Candidate]:
	"""Rank all shift candidates by the number of dictionary word matches.

	Supply either an in-memory ``dictionary`` or a ``dictionary_path``. If
	neither is supplied, candidates are returned with a score of zero.
	Ties retain the normal shift order, making results deterministic.
	"""
	if dictionary is not None and dictionary_path is not None:
		raise ValueError("provide dictionary or dictionary_path, not both")

	words = dictionary
	if dictionary_path is not None:
		words = load_dictionary(dictionary_path)
	if words is None:
		words = set()

	candidates = [
		Candidate(
			shift=candidate.shift,
			plaintext=candidate.plaintext,
			score=dictionary_score(candidate.plaintext, words),
		)
		for candidate in brute_force_attack(ciphertext)
	]
	return sorted(candidates, key=lambda candidate: (-candidate.score, candidate.shift))
