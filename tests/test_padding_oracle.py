from attacks.padding_oracle import BLOCK_SIZE, ByteQueryStats, padding_oracle_attack


def _xor_blocks(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def _make_ciphertext(plaintext: bytes, iv: bytes) -> bytes:
    padding_length = BLOCK_SIZE - len(plaintext) % BLOCK_SIZE
    padded = plaintext + bytes([padding_length]) * padding_length
    blocks = [
        padded[offset : offset + BLOCK_SIZE]
        for offset in range(0, len(padded), BLOCK_SIZE)
    ]

    ciphertext_blocks = []
    previous = iv
    for plaintext_block in blocks:
        # The test oracle uses the identity block permutation as D; this
        # constructs blocks whose CBC plaintext is the requested padded data.
        ciphertext_block = _xor_blocks(plaintext_block, previous)
        ciphertext_blocks.append(ciphertext_block)
        previous = ciphertext_block
    return b"".join(ciphertext_blocks)


def _identity_permutation_oracle(ciphertext: bytes, iv: bytes) -> bool:
    if not ciphertext or len(ciphertext) % BLOCK_SIZE:
        return False
    blocks = [
        ciphertext[offset : offset + BLOCK_SIZE]
        for offset in range(0, len(ciphertext), BLOCK_SIZE)
    ]
    previous = iv if len(blocks) == 1 else blocks[-2]
    final_plaintext = _xor_blocks(blocks[-1], previous)
    padding_length = final_plaintext[-1]
    return (
        1 <= padding_length <= BLOCK_SIZE
        and final_plaintext[-padding_length:] == bytes([padding_length]) * padding_length
    )


def test_recovers_multiblock_plaintext_and_tracks_every_oracle_call() -> None:
    plaintext = b"padding oracle spans several blocks"
    iv = bytes(range(BLOCK_SIZE))
    ciphertext = _make_ciphertext(plaintext, iv)
    calls = []
    progress: list[ByteQueryStats] = []

    def oracle(candidate_ciphertext: bytes, candidate_iv: bytes) -> bool:
        calls.append((candidate_ciphertext, candidate_iv))
        return _identity_permutation_oracle(candidate_ciphertext, candidate_iv)

    recovered, query_count = padding_oracle_attack(
        ciphertext, iv, oracle, on_byte_recovered=progress.append
    )

    assert recovered == plaintext
    assert query_count == len(calls)
    assert len(progress) == len(ciphertext) // BLOCK_SIZE * BLOCK_SIZE
    assert progress[-1].total_queries == query_count
    for block_index in range(len(ciphertext) // BLOCK_SIZE):
        block_events = [event for event in progress if event.block_index == block_index]
        assert len(block_events) == BLOCK_SIZE
        assert block_events[-1].block_queries == sum(
            event.byte_queries for event in block_events
        )


def test_removes_a_full_block_of_pkcs7_padding() -> None:
    plaintext = b"1234567890abcdef"
    assert len(plaintext) == BLOCK_SIZE
    iv = bytes(reversed(range(BLOCK_SIZE)))
    ciphertext = _make_ciphertext(plaintext, iv)

    recovered, query_count = padding_oracle_attack(
        ciphertext, iv, _identity_permutation_oracle
    )

    assert recovered == plaintext
    assert query_count > 0
