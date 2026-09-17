"""Kasiski and frequency-analysis tools for Vigenere ciphertexts."""

from collections import Counter, defaultdict
from typing import DefaultDict, Dict, List, Sequence, Tuple

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ENGLISH_FREQUENCIES = (
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015,
    0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749,
    0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758,
    0.00978, 0.02360, 0.00150, 0.01974, 0.00074,
)


def clean_ciphertext(ciphertext: str) -> str:
    """Remove non-letters and normalize the ciphertext to uppercase."""
    return "".join(character for character in ciphertext.upper() if character in ALPHABET)


def find_repeated_patterns(
    ciphertext: str, min_length: int = 3, max_length: int = 5
) -> Dict[str, List[int]]:
    """Return repeated n-grams and their starting positions."""
    text = clean_ciphertext(ciphertext)
    if min_length < 2 or max_length < min_length:
        raise ValueError("pattern lengths must satisfy 2 <= min_length <= max_length")

    occurrences: DefaultDict[str, List[int]] = defaultdict(list)
    for length in range(min_length, max_length + 1):
        for position in range(len(text) - length + 1):
            occurrences[text[position:position + length]].append(position)
    return {
        pattern: positions
        for pattern, positions in occurrences.items()
        if len(positions) > 1
    }


def calculate_distances(repeated_patterns: Dict[str, Sequence[int]]) -> List[int]:
    """Calculate all pairwise distances between repeated pattern occurrences."""
    distances: List[int] = []
    for positions in repeated_patterns.values():
        for left in range(len(positions)):
            for right in range(left + 1, len(positions)):
                distance = positions[right] - positions[left]
                if distance > 0:
                    distances.append(distance)
    return distances


def find_factors(distances: Sequence[int], max_factor: int = 40) -> Counter[int]:
    """Count useful factors of repeated-pattern distances."""
    factors: Counter[int] = Counter()
    for distance in distances:
        for factor in range(2, min(max_factor, distance) + 1):
            if distance % factor == 0:
                factors[factor] += 1
    return factors


def calculate_ic(text: str) -> float:
    """Calculate the Index of Coincidence for letters in *text*."""
    cleaned = clean_ciphertext(text)
    length = len(cleaned)
    if length < 2:
        return 0.0
    counts = Counter(cleaned)
    return sum(count * (count - 1) for count in counts.values()) / (length * (length - 1))


def kasiski_analysis(
    ciphertext: str, min_key_length: int = 2, max_key_length: int = 20
) -> List[int]:
    """Suggest key lengths, ranked using Kasiski factors and average IC."""
    if min_key_length < 1 or max_key_length < min_key_length:
        raise ValueError("invalid key-length bounds")

    patterns = find_repeated_patterns(ciphertext)
    factors = find_factors(calculate_distances(patterns), max_factor=max_key_length)
    text = clean_ciphertext(ciphertext)
    ranked: List[Tuple[int, float]] = []
    for length in range(min_key_length, max_key_length + 1):
        groups = split_into_groups(text, length)
        average_ic = sum(calculate_ic(group) for group in groups) / length
        factor_score = factors.get(length, 0)
        # Repeated distances generate candidates, while column IC is the
        # stronger discriminator between a real period and an accidental factor.
        score = factor_score + max(0.0, average_ic - 0.035) * 1000.0
        ranked.append((length, score))
    ranked.sort(key=lambda item: item[1], reverse=True)
    return [length for length, _ in ranked]


def split_into_groups(ciphertext: str, key_length: int) -> List[str]:
    """Split ciphertext into key-position groups."""
    if key_length < 1:
        raise ValueError("key_length must be positive")
    text = clean_ciphertext(ciphertext)
    return [text[offset::key_length] for offset in range(key_length)]


def frequency_analysis(groups: Sequence[str]) -> List[Dict[str, int]]:
    """Return complete A-Z frequency tables for each group."""
    return [
        {letter: Counter(clean_ciphertext(group)).get(letter, 0) for letter in ALPHABET}
        for group in groups
    ]


def find_shift(group: str) -> int:
    """Estimate the Caesar encryption shift using chi-square scoring."""
    cleaned = clean_ciphertext(group)
    if not cleaned:
        raise ValueError("cannot estimate a shift from an empty group")

    counts = Counter(cleaned)
    best_shift = 0
    best_score = float("inf")
    for shift in range(26):
        score = 0.0
        for index, expected_frequency in enumerate(ENGLISH_FREQUENCIES):
            observed = counts[ALPHABET[(index + shift) % 26]]
            expected = len(cleaned) * expected_frequency
            score += (observed - expected) ** 2 / expected
        if score < best_score:
            best_score = score
            best_shift = shift
    return best_shift


def find_key(ciphertext: str, key_length: int) -> str:
    """Combine frequency-analysis shifts into a Vigenere key."""
    return "".join(ALPHABET[find_shift(group)] for group in split_into_groups(ciphertext, key_length))


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt letters while preserving non-letter formatting."""
    normalized_key = clean_ciphertext(key)
    if not normalized_key:
        raise ValueError("key must contain at least one letter")
    key_index = 0
    plaintext: List[str] = []
    for character in ciphertext:
        if character.upper() in ALPHABET:
            cipher_value = ord(character.upper()) - ord("A")
            key_value = ord(normalized_key[key_index % len(normalized_key)]) - ord("A")
            plaintext.append(chr((cipher_value - key_value) % 26 + ord("A")))
            key_index += 1
        else:
            plaintext.append(character)
    return "".join(plaintext)


def vigenere_encrypt(plaintext: str, key: str) -> str:
    """Encrypt letters while preserving non-letter formatting."""
    normalized_key = clean_ciphertext(key)
    if not normalized_key:
        raise ValueError("key must contain at least one letter")
    key_index = 0
    ciphertext: List[str] = []
    for character in plaintext:
        if character.upper() in ALPHABET:
            plain_value = ord(character.upper()) - ord("A")
            key_value = ord(normalized_key[key_index % len(normalized_key)]) - ord("A")
            ciphertext.append(chr((plain_value + key_value) % 26 + ord("A")))
            key_index += 1
        else:
            ciphertext.append(character)
    return "".join(ciphertext)


def verify(ciphertext: str, plaintext: str, key: str) -> bool:
    """Check whether re-encryption reproduces the normalized ciphertext."""
    return clean_ciphertext(vigenere_encrypt(plaintext, key)) == clean_ciphertext(ciphertext)


def analyze_vigenere(ciphertext: str, key_length: int | None = None) -> Tuple[int, List[Dict[str, int]], str, str, bool]:
    """Run the complete attack and return length, tables, key, plaintext, status."""
    cleaned = clean_ciphertext(ciphertext)
    if not cleaned:
        raise ValueError("ciphertext must contain at least one letter")
    selected_length = kasiski_analysis(cleaned)[0] if key_length is None else key_length
    if selected_length < 1:
        raise ValueError("key_length must be positive")
    key = find_key(cleaned, selected_length)
    plaintext = vigenere_decrypt(cleaned, key)
    return (
        selected_length,
        frequency_analysis(split_into_groups(cleaned, selected_length)),
        key,
        plaintext,
        verify(cleaned, plaintext, key),
    )
