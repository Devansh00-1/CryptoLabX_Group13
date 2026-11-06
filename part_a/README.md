# Part A — MT19937 Stream Cipher

Run the standalone demonstration with:

```sh
python part_a/mt19937_stream_cipher.py
```

It picks a fresh random 16-bit seed and a fresh printable 5–20 character prefix on each run. The companion notebook, `mt19937_stream_cipher.ipynb`, gives a repeatable example and explains the attack.

## Concepts

MT19937 is a deterministic pseudorandom number generator with a 19937-bit state. Python's built-in `random.Random` uses MT19937. Its output is useful for simulation, but it is not a cryptographic random number generator: its state can be inferred from enough output, and its outputs are predictable. Reusing its output as a keystream therefore does not provide secure encryption.

A stream cipher combines plaintext bytes and keystream bytes with XOR. XOR is its own inverse, so the same function encrypts and decrypts. A known-plaintext attack uses a known portion of plaintext to identify a key or generator state. Here the attacker knows that 14 consecutive bytes are `A`, but does not know where they occur. For each candidate seed, decrypt all ciphertext bytes and search the resulting plaintext for that marker.

A 16-bit seed has only 2^16 = 65,536 possibilities. Exhaustively trying every value is practical and recovers the seed in this demonstration. The seed itself is selected with `secrets`, independently of the insecure MT19937 stream generator.

## Seed-recovery pseudocode

```text
for seed from 0 through 65535:
    candidate_plaintext = XOR(ciphertext, MT19937_bytes(seed, ciphertext_length))
    if candidate_plaintext contains fourteen consecutive 'A' bytes:
        return seed, candidate_plaintext
fail: no matching seed
```

The found marker position is returned as a diagnostic, but it is not used to constrain the search.
