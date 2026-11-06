"""Demonstrate recovery of a timestamp-seeded MT19937 reset token.

This is intentionally insecure lab code. Python's random.Random uses MT19937,
which is not suitable for generating security tokens.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

TOKEN_BYTES = 16
SEARCH_RADIUS_SECONDS = 300
RECORD_PATH = Path(__file__).with_name("password_reset_token_record.json")


def generate_token(timestamp: int) -> bytes:
    """Generate 16 bytes using the same MT19937 byte extraction as Part A."""
    if not isinstance(timestamp, int) or timestamp < 0:
        raise ValueError("timestamp must be a non-negative integer")
    generator = random.Random(timestamp)
    return bytes(generator.getrandbits(8) for _ in range(TOKEN_BYTES))


def save_generation_record(timestamp: int, token: bytes, path: Path = RECORD_PATH) -> None:
    """Save both the timestamp and token in hexadecimal form."""
    record = {
        "generation_timestamp_unix_seconds": timestamp,
        "generation_timestamp_hex": f"0x{timestamp:x}",
        "token_hex": token.hex(),
    }
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def recover_timestamp(
    observed_token: bytes,
    approximate_timestamp: int,
    radius: int = SEARCH_RADIUS_SECONDS,
) -> tuple[int, int, tuple[int, int]]:
    """Test every candidate timestamp in the inclusive search interval."""
    if len(observed_token) != TOKEN_BYTES:
        raise ValueError(f"observed token must be exactly {TOKEN_BYTES} bytes")
    if not isinstance(approximate_timestamp, int) or approximate_timestamp < 0:
        raise ValueError("approximate_timestamp must be a non-negative integer")
    if not isinstance(radius, int) or radius < 0:
        raise ValueError("radius must be a non-negative integer")

    start = max(0, approximate_timestamp - radius)
    end = approximate_timestamp + radius
    matches: list[int] = []
    candidates_tested = 0
    for candidate_timestamp in range(start, end + 1):
        candidates_tested += 1
        if generate_token(candidate_timestamp) == observed_token:
            matches.append(candidate_timestamp)

    if not matches:
        raise ValueError("no matching timestamp found in the search interval")
    if len(matches) != 1:
        raise ValueError(f"ambiguous token: {len(matches)} matching timestamps found")
    return matches[0], candidates_tested, (start, end)


def run_attack(
    timestamp: int | None = None,
    radius: int = SEARCH_RADIUS_SECONDS,
    record_path: Path = RECORD_PATH,
) -> dict[str, int | str | bool | tuple[int, int]]:
    """Generate a token, recover its timestamp, and verify regeneration."""
    generation_timestamp = int(time.time()) if timestamp is None else timestamp
    token = generate_token(generation_timestamp)
    save_generation_record(generation_timestamp, token, record_path)

    recovered_timestamp, candidates_tested, search_interval = recover_timestamp(
        token, generation_timestamp, radius
    )
    regenerated_token = generate_token(recovered_timestamp)
    verified = regenerated_token == token
    if not verified:
        raise RuntimeError("recovered timestamp did not regenerate the observed token")

    return {
        "generation_timestamp": generation_timestamp,
        "token_hex": token.hex(),
        "record_path": str(record_path),
        "search_interval": search_interval,
        "candidates_tested": candidates_tested,
        "recovered_timestamp": recovered_timestamp,
        "recovered_timestamp_hex": f"0x{recovered_timestamp:x}",
        "regenerated_token_hex": regenerated_token.hex(),
        "verified": verified,
    }


def main() -> None:
    result = run_attack()
    start, end = result["search_interval"]
    print("Predictable password reset token attack")
    print(f"  original timestamp:       {result['generation_timestamp']}")
    print(f"  timestamp (hex):          0x{result['generation_timestamp']:x}")
    print(f"  original token (hex):     {result['token_hex']}")
    print(f"  saved generation record:  {result['record_path']}")
    print(f"  search interval:          [{start}, {end}]")
    print(f"  timestamps tested:        {result['candidates_tested']}")
    print(f"  recovered timestamp:      {result['recovered_timestamp']}")
    print(f"  recovered timestamp hex:  {result['recovered_timestamp_hex']}")
    print(f"  regenerated token (hex):  {result['regenerated_token_hex']}")
    print(f"  verification:             {result['verified']}")


if __name__ == "__main__":
    main()
