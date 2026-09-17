# Monoalphabetic substitution cipher assignment

This standalone C++17 program demonstrates:

1. Random-key encryption of plaintext loaded from a file (including a 1+ page
   plaintext).
2. `frequency_analysis()`, `word_frequency_analysis()`, and
   `pattern_analysis()`.
3. Iterative, user-driven cryptanalysis through accepted or rejected
   ciphertext-to-plaintext hypotheses.
4. `apply_substitution()`, `display_partial_plaintext()`, and
   `verify_solution()`.
5. Recovery and display of the complete substitution key, followed by exact
   re-encryption verification.

No sample key or plaintext mapping is embedded in the implementation. The
encryption key is generated randomly each run.

## Build and run

```sh
cd classical/monoalphabetic_cipher
make
./monoalphabetic_cipher --plaintext-file ../../datasets/your_one_page.txt
```

During cryptanalysis, enter mappings such as `map Q E`, where `Q` is a
ciphertext letter and `E` is the hypothesized plaintext letter. Use `show` to
preview the current partial plaintext, `reject` to undo the last hypothesis,
and `done` when the plaintext is meaningful.

The supplied input text is retained exactly, including whitespace and
punctuation, so verification compares the complete ciphertext byte-for-byte.
