"""Command-line entry point for the shift-cipher tools."""

from pathlib import Path

from .brute_force_dictionary import dictionary_attack
from .chi_square_attack import break_shift_cipher_chi_square
from .shift_cipher import decrypt, encrypt


DICTIONARY_PATH = Path(__file__).parents[1] / "dictionary" / "english_words.txt"


def main() -> None:
	"""Run the shift-cipher command-line menu."""
	while True:
		print("\n=== Shift Cipher Menu ===")
		print("1. Encrypt")
		print("2. Decrypt")
		print("3. Attack")
		print("4. Exit")

		choice = input("Enter your choice: ").strip()
		if choice == "1":
			text = input("Enter plaintext: ")
			shift = int(input("Enter shift (integer): "))
			print(f"Ciphertext: {encrypt(text, shift)}")
		elif choice == "2":
			text = input("Enter ciphertext: ")
			shift = int(input("Enter shift (integer): "))
			print(f"Plaintext: {decrypt(text, shift)}")
		elif choice == "3":
			ciphertext = input("Enter ciphertext: ")
			candidates = dictionary_attack(
				ciphertext,
				dictionary_path=DICTIONARY_PATH,
			)
			shift, plaintext = break_shift_cipher_chi_square(ciphertext)
			print(f"Dictionary candidate: shift={candidates[0].shift}, "
				  f"score={candidates[0].score}, "
				  f"plaintext={candidates[0].plaintext}")
			print(f"Chi-square candidate: shift={shift}, plaintext={plaintext}")
		elif choice == "4":
			print("Goodbye!")
			break
		else:
			print("Invalid choice. Please try again.")


if __name__ == "__main__":
	main()
