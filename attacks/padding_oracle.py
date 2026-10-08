"""CBC padding-oracle plaintext recovery.

The oracle callable is expected to accept ``(ciphertext, iv)`` and return a
truthy value when PKCS#7 padding is valid. No encryption key is needed here.
"""

from __future__ import annotations

from typing import Callable


BLOCK_SIZE = 16
PaddingOracle = Callable[[bytes, bytes], bool]


def padding_oracle_attack(
    ciphertext: bytes, iv: bytes, oracle: PaddingOracle
) -> tuple[bytes, int]:
    """Recover and unpad plaintext, returning it with the oracle query count.

    ``ciphertext`` must contain one or more complete AES blocks, and ``iv``
    must be one AES block. The oracle is called with the full ciphertext and
    the candidate IV for each guess.
    """
    if not isinstance(ciphertext, bytes) or not isinstance(iv, bytes):
        raise TypeError("ciphertext and iv must be bytes")
    if len(iv) != BLOCK_SIZE:
        raise ValueError("IV must be exactly 16 bytes")
    if not ciphertext or len(ciphertext) % BLOCK_SIZE:
        raise ValueError("ciphertext must contain complete AES blocks")

    blocks = [ciphertext[i : i + BLOCK_SIZE] for i in range(0, len(ciphertext), BLOCK_SIZE)]
    previous_blocks = [iv, *blocks[:-1]]
    recovered = bytearray()
    query_count = 0

    for block_index, (original_previous, target) in enumerate(zip(previous_blocks, blocks)):
        intermediate = bytearray(BLOCK_SIZE)  # D_K(target), recovered byte by byte
        plaintext_block = bytearray(BLOCK_SIZE)

        for position in range(BLOCK_SIZE - 1, -1, -1):
            pad_value = BLOCK_SIZE - position
            crafted_previous = bytearray(original_previous)

            # Preserve already recovered intermediate bytes while setting the
            # desired padding value in the crafted plaintext suffix.
            for suffix_position in range(position + 1, BLOCK_SIZE):
                crafted_previous[suffix_position] = intermediate[suffix_position] ^ pad_value

            found = False
            for guess in range(256):
                crafted_previous[position] = guess
                candidate_iv = bytes(crafted_previous) if block_index == 0 else iv
                if block_index == 0:
                    candidate_ciphertext = target
                else:
                    # Truncate after the block under attack so that it is
                    # the final block checked by a conventional oracle.
                    candidate_blocks = blocks[:block_index]
                    candidate_blocks[block_index - 1] = bytes(crafted_previous)
                    candidate_ciphertext = b"".join(candidate_blocks)

                query_count += 1
                if not oracle(candidate_ciphertext, candidate_iv):
                    continue

                # For a 1-byte pad, eliminate accidental acceptance of a
                # longer pre-existing padding string by perturbing its neighbor.
                if position > 0:
                    confirmation = bytearray(crafted_previous)
                    confirmation[position - 1] ^= 1
                    if block_index == 0:
                        confirm_iv = bytes(confirmation)
                        confirm_ciphertext = target
                    else:
                        confirm_iv = iv
                        confirm_blocks = blocks[:block_index]
                        confirm_blocks[block_index - 1] = bytes(confirmation)
                        confirm_ciphertext = b"".join(confirm_blocks)
                    query_count += 1
                    if not oracle(confirm_ciphertext, confirm_iv):
                        continue

                intermediate[position] = guess ^ pad_value
                plaintext_block[position] = intermediate[position] ^ original_previous[position]
                found = True
                break

            if not found:
                raise ValueError(f"no valid padding guess for block {block_index}, byte {position}")

        recovered.extend(plaintext_block)

    if not recovered:
        raise ValueError("no plaintext recovered")
    padding_length = recovered[-1]
    if not 1 <= padding_length <= BLOCK_SIZE or recovered[-padding_length:] != bytes([padding_length]) * padding_length:
        raise ValueError("oracle responses did not yield valid PKCS#7 padded plaintext")
    return bytes(recovered[:-padding_length]), query_count
