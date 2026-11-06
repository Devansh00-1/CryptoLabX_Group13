"""MT19937-based stream cipher and a small known-plaintext seed attack demo.

This is intentionally insecure lab code. Python's random.Random is designed
for simulation, not cryptography, and a 16-bit seed is trivial to search.
"""

from __future__ import annotations

import random
import secrets
import string

SEED_BITS = 16
SEED_SPACE = 1 << SEED_BITS
KNOWN_SUFFIX = b"A" * 14


def xor_bytes(left: bytes, right: bytes) -> bytes:
    """XOR equal-length byte strings."""
    if len(left) != len(right):
        raise ValueError("inputs must have equal length")
    return bytes(a ^ b for a, b in zip(left, right))


def mt19937_stream(data: bytes, seed: int) -> bytes:
    """Encrypt or decrypt bytes by XORing with one MT19937 byte per byte."""
    if not 0 <= seed < SEED_SPACE:
        raise ValueError("seed must be between 0 and 65535")
    generator = random.Random(seed)  # Python's standard MT19937 implementation
    keystream = bytes(generator.getrandbits(8) for _ in data)
    return xor_bytes(data, keystream)


def make_known_plaintext(prefix: str | None = None) -> bytes:
    """Return a printable 5–20 character prefix followed by exactly 14 As."""
    if prefix is None:
        length = secrets.randbelow(16) + 5
        prefix = "".join(secrets.choice(string.printable[:-6]) for _ in range(length))
    if not 5 <= len(prefix) <= 20:
        raise ValueError("prefix must contain 5–20 characters")
    if any(char not in string.printable[:-6] for char in prefix):
        raise ValueError("prefix must contain printable non-whitespace characters")
    return prefix.encode("ascii") + KNOWN_SUFFIX


def recover_seed(ciphertext: bytes) -> tuple[int, bytes, int]:
    """Search every 16-bit seed; the marker position is not supplied.

    Returns (seed, full_plaintext, marker_offset). Raises ValueError if no
    candidate yields the known 14-byte marker.
    """
    for seed in range(SEED_SPACE):
        plaintext = mt19937_stream(ciphertext, seed)
        offset = plaintext.find(KNOWN_SUFFIX)
        if offset != -1:
            return seed, plaintext, offset
    raise ValueError("no seed produced the known 14-character plaintext")


def demo(seed: int | None = None, prefix: str | None = None) -> dict[str, object]:
    """Run the reversible-cipher example, then generate and attack a message."""
    # First demonstrate the same function in both directions.
    message = b"MT19937 lab test"
    example_seed = 12345
    example_ciphertext = mt19937_stream(message, example_seed)
    example_decrypted = mt19937_stream(example_ciphertext, example_seed)
    assert example_decrypted == message

    plaintext = make_known_plaintext(prefix)
    selected_seed = secrets.randbelow(SEED_SPACE) if seed is None else seed
    ciphertext = mt19937_stream(plaintext, selected_seed)
    recovered_seed, recovered_plaintext, marker_offset = recover_seed(ciphertext)
    verified = recovered_seed == selected_seed and recovered_plaintext == plaintext
    assert verified
    return {
        "example_message": message,
        "example_ciphertext": example_ciphertext,
        "example_decrypted": example_decrypted,
        "plaintext": plaintext,
        "ciphertext": ciphertext,
        "seed": selected_seed,
        "recovered_seed": recovered_seed,
        "recovered_plaintext": recovered_plaintext,
        "marker_offset": marker_offset,
        "verified": verified,
    }


def main() -> None:
    result = demo()
    print("Reversible cipher example")
    print(f"  message:           {result['example_message'].decode('ascii')}")
    print(f"  ciphertext (hex):  {result['example_ciphertext'].hex()}")
    print(f"  decrypted:         {result['example_decrypted'].decode('ascii')}")
    print("\nKnown-plaintext seed recovery")
    print(f"  plaintext:         {result['plaintext'].decode('ascii')}")
    print(f"  ciphertext (hex):  {result['ciphertext'].hex()}")
    print(f"  recovered seed:    {result['recovered_seed']}")
    print(f"  decrypted:         {result['recovered_plaintext'].decode('ascii')}")
    print(f"  marker offset:     {result['marker_offset']} (reported after search)")
    print(f"  verified:          {result['verified']}")


if __name__ == "__main__":
    main()
