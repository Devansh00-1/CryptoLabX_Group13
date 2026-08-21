import string

# English letter frequencies (expected percentages)
ENGLISH_FREQUENCIES = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
    'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
    'i': 0.06966, 'j': 0.00015, 'k': 0.00772, 'l': 0.04025,
    'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
    'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
    'y': 0.01974, 'z': 0.00074
}

def decrypt_shift_cipher(ciphertext: str, shift: int) -> str:
    """Decrypts a shift cipher given the ciphertext and the shift value."""
    plaintext = []
    for char in ciphertext:
        if char.isalpha():
            start = ord('a') if char.islower() else ord('A')
            decrypted_char = chr((ord(char) - start - shift) % 26 + start)
            plaintext.append(decrypted_char)
        else:
            plaintext.append(char)
    return "".join(plaintext)

def calculate_chi_square(text: str) -> float:
    """Calculates the chi-square statistic for a given text based on English letter frequencies."""
    text_length = sum(1 for char in text if char.isalpha())
    if text_length == 0:
        return float('inf')

    # Count occurrences of each letter in the text
    letter_counts = {char: 0 for char in string.ascii_lowercase}
    for char in text.lower():
        if char.isalpha():
            letter_counts[char] += 1

    chi_square_stat = 0.0
    for char in string.ascii_lowercase:
        observed = letter_counts[char]
        expected = ENGLISH_FREQUENCIES[char] * text_length
        if expected > 0:
            chi_square_stat += ((observed - expected) ** 2) / expected
            
    return chi_square_stat

def break_shift_cipher_chi_square(ciphertext: str) -> tuple[int, str]:
    """
    Attempts to break a shift cipher using chi-square cryptanalysis.
    Returns the most likely shift and the corresponding decrypted text.
    """
    best_shift = 0
    min_chi_square = float('inf')
    best_plaintext = ""

    for shift in range(26):
        decrypted_text = decrypt_shift_cipher(ciphertext, shift)
        chi_square = calculate_chi_square(decrypted_text)
        
        if chi_square < min_chi_square:
            min_chi_square = chi_square
            best_shift = shift
            best_plaintext = decrypted_text

    return best_shift, best_plaintext

if __name__ == "__main__":
    # Example usage:
    # A longer text is needed for reliable statistical analysis
    plaintext = "Chi square cryptanalysis is a statistical technique used to break classical ciphers like the shift cipher. It relies on comparing the expected frequency of letters in a language to the observed frequency in the decrypted text."
    
    # Encrypt the plaintext with a shift of 7
    shift_key = 7
    ciphertext = ""
    for char in plaintext:
        if char.isalpha():
            start = ord('a') if char.islower() else ord('A')
            ciphertext += chr((ord(char) - start + shift_key) % 26 + start)
        else:
            ciphertext += char
            
    print(f"Ciphertext: {ciphertext}\n")
    
    likely_shift, likely_plaintext = break_shift_cipher_chi_square(ciphertext)
    
    print(f"Most likely shift: {likely_shift}")
    print(f"Decrypted text: {likely_plaintext}")
