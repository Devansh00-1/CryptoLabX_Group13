"""
CryptoLabX - A modular cryptography learning and experimentation lab.

This is the main entry point for the CryptoLabX_Group13 project.
It provides a menu-driven command-line interface for encrypting,
decrypting, attacking, and analyzing cryptographic data.
"""

from datetime import datetime
from pathlib import Path

from analysis.file_analyzer import FileAnalyzer
from attacks.shift_cipher_attack.src.brute_force_dictionary import dictionary_attack
from attacks.shift_cipher_attack.src.chi_square_attack import break_shift_cipher_chi_square
from attacks.shift_cipher_attack.src.shift_cipher import decrypt, encrypt

# Path to the datasets folder relative to this file
DATASETS_DIR = Path(__file__).parent / "datasets"
LOG_FILE = Path(__file__).parent / "outputs" / "execution_log.txt"


def start_session_log() -> None:
    """Write a session header to the execution log indicating a new run."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 60
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write("\n")
        file.write(sep + "\n")
        file.write(f"  SESSION STARTED  [{ts}]\n")
        file.write(sep + "\n")


def log_menu_selection(action: str, detail: str | None = None) -> None:
    """Append a formatted action line to the execution log.

    Examples:
      [2026-08-04 20:37:10]  ACTION: ANALYZE  |  DETAIL: data1.txt
      [2026-08-04 20:37:18]  ACTION: EXIT
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if detail:
        line = f"[{timestamp}]  ACTION: {action}  |  DETAIL: {detail}\n"
    else:
        line = f"[{timestamp}]  ACTION: {action}\n"
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line)


def initialize_datasets() -> None:
    """Create the datasets folder and sample files for future assignments."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    dataset_files = {
        "sample.txt": (
            "The quick brown fox jumps over the lazy dog.\n"
            "Cryptography is the art of writing and solving codes.\n"
            "Hello World from CryptoLabX Group Thirteen."
        ),
        "dataset1.txt": "This dataset contains sample plaintext for classical cipher analysis.\nLine 2 of dataset one.",
        "dataset2.txt": "This dataset contains sample ciphertext for frequency analysis.\nLine 2 of dataset two.",
        "dataset3.txt": "This dataset contains sample keys and messages for modern cipher testing.\nLine 2 of dataset three.",
        "dataset4.txt": "This dataset contains text for attack simulation and brute-force practice.\nLine 2 of dataset four.",
        "dataset5.txt": "This dataset contains notes and sample phrases for cryptanalysis exercises.\nLine 2 of dataset five.",
    }

    for filename, content in dataset_files.items():
        file_path = DATASETS_DIR / filename
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")


def display_menu() -> None:
    """Show the main menu options."""
    print("\n=== CryptoLabX Menu ===")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Attack")
    print("4. Analyze")
    print("5. Exit")
    print("=======================")


def handle_analyze() -> Path | None:
    """Run the file analysis task on a text file in the datasets folder."""
    print("\nAvailable datasets:")
    files = sorted(
        p for p in DATASETS_DIR.iterdir()
        if p.is_file() and p.name != ".gitkeep"
    )
    if not files:
        print("No text files found in the datasets folder.")
        log_menu_selection("ANALYZE", detail="NO_DATASETS")
        return None

    for i, f in enumerate(files, start=1):
        print(f"  {i}. {f.name}")

    choice = input("Select a file number (or press Enter to skip): ").strip()
    if not choice:
        print("Analysis cancelled.")
        log_menu_selection("ANALYZE_CANCELLED")
        return None

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(files):
            print("Invalid selection.")
            log_menu_selection("ANALYZE_INVALID_SELECTION", detail=choice)
            return None
        selected = files[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        log_menu_selection("ANALYZE_INVALID_INPUT", detail=choice)
        return None

    analyzer = FileAnalyzer(str(selected))
    analyzer.print_report()
    log_menu_selection("ANALYZE", detail=selected.name)
    return selected


def ask_sample_file() -> None:
    """Create a sample text file in the datasets folder if none exists."""
    if not DATASETS_DIR.exists():
        DATASETS_DIR.mkdir(parents=True)
    sample = DATASETS_DIR / "sample.txt"
    if not sample.exists():
        sample.write_text(
            "The quick brown fox jumps over the lazy dog.\n"
            "Cryptography is the art of writing and solving codes.\n"
            "Hello World from CryptoLabX Group Thirteen.",
            encoding="utf-8",
        )


def handle_encrypt() -> None:
    """Encrypt text with a Caesar shift."""
    plaintext = input("Enter plaintext: ")
    try:
        shift = int(input("Enter shift (integer): ").strip())
    except ValueError:
        print("Invalid shift. Please enter an integer.")
        return

    print(f"Ciphertext: {encrypt(plaintext, shift)}")
    log_menu_selection("ENCRYPT", detail=f"shift={shift}")


def handle_decrypt() -> None:
    """Decrypt text with a Caesar shift."""
    ciphertext = input("Enter ciphertext: ")
    try:
        shift = int(input("Enter shift (integer): ").strip())
    except ValueError:
        print("Invalid shift. Please enter an integer.")
        return

    print(f"Plaintext: {decrypt(ciphertext, shift)}")
    log_menu_selection("DECRYPT", detail=f"shift={shift}")


def handle_attack() -> None:
    """Run dictionary and chi-square attacks against ciphertext."""
    ciphertext = input("Enter ciphertext: ")
    dictionary_path = (
        Path(__file__).parent
        / "attacks"
        / "shift_cipher_attack"
        / "dictionary"
        / "english_words.txt"
    )
    candidates = dictionary_attack(ciphertext, dictionary_path=dictionary_path)
    likely_shift, likely_plaintext = break_shift_cipher_chi_square(ciphertext)

    print("\nBest dictionary candidate:")
    print(f"  Shift: {candidates[0].shift}")
    print(f"  Score: {candidates[0].score}")
    print(f"  Plaintext: {candidates[0].plaintext}")
    print("\nBest chi-square candidate:")
    print(f"  Shift: {likely_shift}")
    print(f"  Plaintext: {likely_plaintext}")
    log_menu_selection("ATTACK", detail="dictionary+chi_square")


def main() -> None:
    """Run the menu-driven command-line interface."""
    print("CryptoLabX_Group13")
    print("Welcome to CryptoLabX - Cryptography Lab Project")

    # Ensure the datasets folder contains required sample files
    initialize_datasets()

    # Start a new session entry in the log
    start_session_log()

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            handle_encrypt()
        elif choice == "2":
            handle_decrypt()
        elif choice == "3":
            handle_attack()
        elif choice == "4":
            handle_analyze()  # Analyze
        elif choice == "5":
            log_menu_selection("EXIT")
            print("Goodbye!")
            break
        else:
            log_menu_selection("INVALID")
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
