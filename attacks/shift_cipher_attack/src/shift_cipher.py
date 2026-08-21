
def shift_cipher(text: str, shift: int) -> str:
	"""Apply a Caesar shift to alphabetic characters in ``text``.

	Uppercase and lowercase letters retain their case. Non-alphabetic
	characters are returned unchanged, and shifts wrap around the alphabet.
	"""
	shifted_characters = []

	for character in text:
		if "A" <= character <= "Z":
			alphabet_start = ord("A")
		elif "a" <= character <= "z":
			alphabet_start = ord("a")
		else:
			shifted_characters.append(character)
			continue

		offset = (ord(character) - alphabet_start + shift) % 26
		shifted_characters.append(chr(alphabet_start + offset))

	return "".join(shifted_characters)


def encrypt(plaintext: str, shift: int) -> str:
	"""Encrypt ``plaintext`` with a Caesar shift."""
	return shift_cipher(plaintext, shift)


def decrypt(ciphertext: str, shift: int) -> str:
	"""Decrypt ``ciphertext`` with a Caesar shift."""
	return shift_cipher(ciphertext, -shift)
