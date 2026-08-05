# CryptoLabX_Group13

A modular cryptography learning and experimentation lab.

## Project Structure

```
CryptoLabX_Group13
│
├── classical   # Classical ciphers (e.g., Caesar, Vigenère)
├── attacks     # Cryptographic attacks (e.g., brute force, frequency analysis)
├── math        # Mathematical utilities (e.g., modular arithmetic, primes)
├── modern      # Modern cryptosystems (e.g., RSA, AES, hashing)
├── analysis    # Analysis and visualization tools
├── datasets    # Data files and sample datasets
├── outputs     # Generated outputs and results
├── docs        # Documentation and references
├── tests       # Unit tests
├── utils       # Shared utility functions
│
├── main.py
├── README.md
└── requirements.txt
```

## Features

### Menu-Driven CLI

Running `python main.py` starts an interactive menu with the following options:

1. **Encrypt** — Coming soon
2. **Decrypt** — Coming soon
3. **Attack** — Coming soon
4. **Analyze** — Analyzes a text file from the `datasets` folder
5. **Exit** — Exits the program

### File Analyzer

The **Analyze** option reads a text file from the `datasets` folder and reports:

- Number of characters
- Number of words
- Number of lines
- Number of unique characters
- Letter frequency (A–Z, case-insensitive)

A sample file `datasets/sample.txt` is provided for demonstration.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the main entry point:
   ```bash
   python main.py
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Tests

Unit tests are located in the `tests` folder and can be run with:

```bash
python -m pytest tests/
```

## License

TBD
