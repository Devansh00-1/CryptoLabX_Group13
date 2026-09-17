from attacks.vigenere_cipher_attack.src.vigenere_cryptanalysis import (
    calculate_distances,
    calculate_ic,
    clean_ciphertext,
    find_factors,
    find_repeated_patterns,
    frequency_analysis,
    split_into_groups,
    verify,
    vigenere_decrypt,
    vigenere_encrypt,
)


def test_clean_ciphertext_and_groups() -> None:
    assert clean_ciphertext("a-b C!1") == "ABC"
    assert split_into_groups("ABCDEFGH", 3) == ["ADG", "BEH", "CF"]


def test_kasiski_helpers() -> None:
    repeated = find_repeated_patterns("ABCXYZABC", min_length=3, max_length=3)
    assert repeated == {"ABC": [0, 6]}
    assert calculate_distances(repeated) == [6]
    assert find_factors([6], max_factor=10)[3] == 1


def test_frequency_analysis_has_complete_alphabet() -> None:
    tables = frequency_analysis(["AAB!", "CZ"])
    assert tables[0]["A"] == 2
    assert tables[0]["Z"] == 0
    assert tables[1]["C"] == 1


def test_ic_and_vigenere_round_trip() -> None:
    plaintext = "Attack at dawn!"
    ciphertext = vigenere_encrypt(plaintext, "LEMON")
    assert vigenere_decrypt(ciphertext, "LEMON") == "ATTACK AT DAWN!"
    assert verify(ciphertext, plaintext, "LEMON")
    assert calculate_ic("AAAA") == 1.0
