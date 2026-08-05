# CryptoLabX_Group13

A modular cryptography learning and experimentation lab. CryptoLabX provides an interactive command-line interface for exploring classical and modern ciphers, running cryptographic attacks, and analyzing text files.

## Team Members

| Name        | University ID |
|-------------|---------------|
| Divyanshu   | 2024UCP1194   |
| Vishwasingh | 2024UCP1118   |

---

## Table of Contents

- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Folder Explanation](#folder-explanation)
- [Features](#features)
- [Screenshots](#screenshots)
- [Future Work](#future-work)
- [License](#license)

---

## Installation

1. **Clone the repository** (or download the project folder):
   ```bash
   git clone https://github.com/your-org/CryptoLabX_Group13.git
   cd CryptoLabX_Group13
   ```

2. **(Recommended) Create a virtual environment**:
   - **Windows (Command Prompt / PowerShell):**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file includes:
   - `numpy` — core numerical support
   - `pytest` — unit testing framework
   - `matplotlib` — optional, for analysis visualization
   - `pandas` — optional, for data handling

---

## Running the Project

1. Ensure the virtual environment is activated (if you created one).

2. Run the main entry point:
   ```bash
   python main.py
   ```

3. You will see the menu-driven CLI:
   ```
   === CryptoLabX Menu ===
   1. Encrypt
   2. Decrypt
   3. Attack
   4. Analyze
   5. Exit
   =======================
   ```

4. Select an option by entering its number:
   - **1 / 2 / 3** — Encrypt, Decrypt, Attack (currently display "Coming Soon")
   - **4** — Analyze a text file from the `datasets` folder
   - **5** — Exit the program

5. Run the unit tests:
   ```bash
   python -m pytest tests/
   ```

---

## Folder Explanation

| Folder        | Purpose                                                                 |
|---------------|-------------------------------------------------------------------------|
| `classical`   | Classical ciphers (e.g., Caesar, Vigenère, substitution)                |
| `attacks`     | Cryptographic attacks (e.g., brute force, frequency analysis)           |
| `math`        | Mathematical utilities (e.g., modular arithmetic, primes, gcd)          |
| `modern`      | Modern cryptosystems (e.g., RSA, AES, hashing)                          |
| `analysis`    | Analysis and visualization tools (e.g., `file_analyzer.py`)             |
| `datasets`    | Data files and sample datasets (e.g., `sample.txt`)                     |
| `outputs`     | Generated outputs and results from running the tools                    |
| `docs`        | Documentation and references                                            |
| `tests`       | Unit tests (e.g., `test_file_analyzer.py`)                              |
| `utils`       | Shared utility functions used across modules                            |

---

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

---

## Screenshots

> Placeholder: Add screenshots of the application here once available.

<details>
<summary>Main Menu (placeholder)</summary>

<!-- Add image of the main menu here -->
```
![Main Menu](screenshots/main_menu.png)
```

</details>

<details>
<summary>Analysis Report (placeholder)</summary>

<!-- Add image of the analysis report here -->
```
![Analysis Report](screenshots/analysis_report.png)
```

</details>

---

## Future Work

- Implement the **Encrypt** feature with classical ciphers (Caesar, Vigenère, etc.)
- Implement the **Decrypt** feature with corresponding decryption algorithms
- Implement the **Attack** feature with brute-force and frequency-analysis attacks
- Add modern cryptosystems (RSA, AES, hashing) modules
- Add visualization of letter frequency using `matplotlib`
- Expand the `datasets` folder with larger sample texts
- Add more unit tests and increase code coverage
- Add a GUI or web-based interface

---

## License

TBD
</content>
