# Part B — Predictable Password Reset Token Attack

Run the standalone demonstration from the repository root:

```sh
python part_b/password_reset_token_attack.py
```

The program seeds Python's `random.Random` with the current Unix timestamp in
integer seconds. As in Part A, Python's standard-library implementation of
MT19937 generates each token byte with one call to `getrandbits(8)`. The 16
bytes form the reset token. The generation timestamp (decimal and hexadecimal)
and token (hexadecimal) are printed, and the hexadecimal values are saved to
`password_reset_token_record.json` beside the script.

The simulated attacker knows the approximate generation time and tests every
integer timestamp in the inclusive interval from 300 seconds before through
300 seconds after it. The reported count is therefore 601 candidates for a
normal current-time run.

## Why this is vulnerable

A timestamp seed is not secret: it is often visible or can be estimated from
when a reset was requested. If the attacker can narrow token creation to a
short time window, the seed search has only hundreds of possibilities rather
than a large random key space. Seeding with a timestamp does not make
MT19937 secure; it makes its starting state especially easy to guess.

MT19937 is designed for simulation, not cryptography. Its output is
deterministic, and its state/output behavior is not designed to resist an
attacker who observes or predicts values. Security tokens must instead come
from a cryptographically secure random number generator, such as Python's
`secrets.token_bytes(16)`.

## Token prediction pseudocode

```text
generation_time = current Unix time in integer seconds
generator = MT19937(seed = generation_time)
token = concatenate(generator.getrandbits(8) for 16 bytes)
save generation_time and token in hexadecimal

for candidate_time from max(0, approximate_time - 300)
                      through approximate_time + 300, inclusive:
    candidate = concatenate(MT19937(candidate_time).getrandbits(8)
                            for 16 bytes)
    compare candidate with observed_token
    remember any matching candidate_time
report number of candidates tested and matching timestamp
regenerate token from matching timestamp and verify equality
```

Open `password_reset_token_attack.ipynb` and run its cells for a notebook-based
demonstration. Both this notebook and the standalone program use the same
implementation in `password_reset_token_attack.py`.
