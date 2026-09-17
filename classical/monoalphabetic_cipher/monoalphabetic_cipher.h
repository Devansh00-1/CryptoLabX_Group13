#ifndef CRYPTOLABX_MONOALPHABETIC_CIPHER_H
#define CRYPTOLABX_MONOALPHABETIC_CIPHER_H

#include <array>
#include <map>
#include <string>
#include <vector>

class MonoalphabeticCipher {
public:
    using Key = std::array<char, 26>;

    MonoalphabeticCipher();

    std::string encrypt(const std::string& plaintext, const Key& key) const;
    std::string apply_substitution(const std::string& ciphertext,
                                   const Key& cipher_to_plaintext) const;

    void frequency_analysis(const std::string& ciphertext) const;
    void word_frequency_analysis(const std::string& ciphertext) const;
    void pattern_analysis(const std::string& ciphertext) const;

    void display_partial_plaintext(
        const std::string& ciphertext,
        const Key& cipher_to_plaintext) const;
    bool verify_solution(const std::string& ciphertext,
                         const std::string& plaintext,
                         const Key& cipher_to_plaintext) const;

    static Key identity_key();
    static Key inverse_key(const Key& cipher_to_plaintext);
    static bool assign_mapping(Key& key, char cipher_letter, char plain_letter,
                               std::string& error);
    static std::string key_to_string(const Key& key);
    static std::string normalize_key(const std::string& key_text);

private:
    static std::vector<std::string> words(const std::string& text);
    static std::string pattern(const std::string& word);
};

#endif
