#include "monoalphabetic_cipher.h"

#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>

namespace {
char upper(char value) {
    return static_cast<char>(std::toupper(static_cast<unsigned char>(value)));
}

bool letter(char value) {
    return std::isalpha(static_cast<unsigned char>(value)) != 0;
}

int index_of(char value) { return upper(value) - 'A'; }
}

MonoalphabeticCipher::MonoalphabeticCipher() = default;

MonoalphabeticCipher::Key MonoalphabeticCipher::identity_key() {
    Key key{};
    for (int i = 0; i < 26; ++i) key[i] = static_cast<char>('A' + i);
    return key;
}

MonoalphabeticCipher::Key MonoalphabeticCipher::inverse_key(
    const Key& cipher_to_plaintext) {
    Key inverse = identity_key();
    for (int i = 0; i < 26; ++i) {
        const char plain = upper(cipher_to_plaintext[i]);
        if (plain >= 'A' && plain <= 'Z') inverse[index_of(plain)] = 'A' + i;
    }
    return inverse;
}

std::string MonoalphabeticCipher::encrypt(const std::string& plaintext,
                                          const Key& key) const {
    std::string result = plaintext;
    for (char& value : result) {
        if (letter(value)) {
            const bool is_lower = std::islower(static_cast<unsigned char>(value));
            char mapped = key[index_of(value)];
            value = is_lower ? static_cast<char>(std::tolower(mapped)) : mapped;
        }
    }
    return result;
}

std::string MonoalphabeticCipher::apply_substitution(
    const std::string& ciphertext, const Key& cipher_to_plaintext) const {
    std::string result = ciphertext;
    for (char& value : result) {
        if (letter(value)) {
            const bool is_lower = std::islower(static_cast<unsigned char>(value));
            char mapped = cipher_to_plaintext[index_of(value)];
            value = is_lower ? static_cast<char>(std::tolower(mapped)) : mapped;
        }
    }
    return result;
}

std::vector<std::string> MonoalphabeticCipher::words(const std::string& text) {
    std::vector<std::string> result;
    std::string current;
    for (char value : text) {
        if (letter(value)) {
            current += upper(value);
        } else if (!current.empty()) {
            result.push_back(current);
            current.clear();
        }
    }
    if (!current.empty()) result.push_back(current);
    return result;
}

std::string MonoalphabeticCipher::pattern(const std::string& word) {
    std::map<char, int> ids;
    std::ostringstream output;
    int next = 0;
    for (std::size_t position = 0; position < word.size(); ++position) {
        const char value = word[position];
        auto [it, inserted] = ids.emplace(value, next);
        if (inserted) ++next;
        if (position > 0) output << '.';
        output << it->second;
    }
    return output.str();
}

void MonoalphabeticCipher::frequency_analysis(
    const std::string& ciphertext) const {
    std::array<int, 26> counts{};
    int total = 0;
    for (char value : ciphertext) {
        if (letter(value)) {
            ++counts[index_of(value)];
            ++total;
        }
    }
    std::vector<std::pair<char, int>> ranked;
    for (int i = 0; i < 26; ++i) ranked.emplace_back('A' + i, counts[i]);
    std::sort(ranked.begin(), ranked.end(),
              [](const auto& left, const auto& right) {
                  if (left.second != right.second) return left.second > right.second;
                  return left.first < right.first;
              });

    std::cout << "\n=== Frequency analysis ===\n";
    std::cout << "Letter  Count  Percent\n";
    for (const auto& [value, count] : ranked) {
        if (count == 0) continue;
        const double percentage = total == 0 ? 0.0 : 100.0 * count / total;
        std::cout << "  " << value << "      " << count << "    "
                  << std::fixed << std::setprecision(2) << percentage << "%\n";
    }
    if (!ranked.empty() && total > 0) {
        std::cout << "Most frequent ciphertext letter(s): ";
        const int highest = ranked.front().second;
        bool first = true;
        for (const auto& [value, count] : ranked) {
            if (count != highest) break;
            if (!first) std::cout << ", ";
            std::cout << value;
            first = false;
        }
        std::cout << '\n';
    }
}

void MonoalphabeticCipher::word_frequency_analysis(
    const std::string& ciphertext) const {
    std::map<std::string, int> counts;
    for (const auto& word : words(ciphertext)) ++counts[word];
    std::vector<std::pair<std::string, int>> ranked(counts.begin(), counts.end());
    std::sort(ranked.begin(), ranked.end(),
              [](const auto& left, const auto& right) {
                  if (left.second != right.second) return left.second > right.second;
                  return left.first < right.first;
              });

    std::cout << "\n=== Word frequency analysis ===\n";
    std::cout << "Repeated words:\n";
    for (const auto& [word, count] : ranked) {
        if (count > 1) std::cout << "  " << word << " (" << count << ")\n";
    }
    std::cout << "Short-word candidates (1-, 2-, and 3-letter words):\n";
    for (const auto& [word, count] : ranked) {
        if (word.size() <= 3)
            std::cout << "  " << word << " (" << count << ")\n";
    }
}

void MonoalphabeticCipher::pattern_analysis(
    const std::string& ciphertext) const {
    std::map<std::string, std::vector<std::string>> grouped;
    for (const auto& word : words(ciphertext)) grouped[pattern(word)].push_back(word);

    std::cout << "\n=== Repeated-letter pattern analysis ===\n";
    for (const auto& [shape, matching_words] : grouped) {
        if (matching_words.size() > 1 || shape.find('.') != std::string::npos) {
            std::cout << "  " << shape << ": ";
            for (std::size_t i = 0; i < matching_words.size(); ++i) {
                if (i) std::cout << ", ";
                std::cout << matching_words[i];
            }
            std::cout << '\n';
        }
    }
}

void MonoalphabeticCipher::display_partial_plaintext(
    const std::string& ciphertext, const Key& cipher_to_plaintext) const {
    std::cout << "\nPartial plaintext:\n"
              << apply_substitution(ciphertext, cipher_to_plaintext) << "\n";
}

bool MonoalphabeticCipher::verify_solution(
    const std::string& ciphertext, const std::string& plaintext,
    const Key& cipher_to_plaintext) const {
    const std::string reencryption = encrypt(plaintext, inverse_key(cipher_to_plaintext));
    const bool matches = reencryption == ciphertext;
    std::cout << "\n=== Verification ===\n"
              << (matches ? "PASS: " : "FAIL: ")
              << "re-encrypted plaintext " << (matches ? "exactly matches" : "does not match")
              << " the original ciphertext.\n";
    return matches;
}

bool MonoalphabeticCipher::assign_mapping(Key& key, char cipher_letter,
                                           char plain_letter, std::string& error) {
    cipher_letter = upper(cipher_letter);
    plain_letter = upper(plain_letter);
    if (cipher_letter < 'A' || cipher_letter > 'Z' ||
        plain_letter < 'A' || plain_letter > 'Z') {
        error = "Both symbols must be letters A-Z.";
        return false;
    }
    const int cipher_index = index_of(cipher_letter);
    for (int i = 0; i < 26; ++i) {
        if (i != cipher_index && key[i] != '?' && key[i] == plain_letter) {
            error = "That plaintext letter is already assigned to another ciphertext letter.";
            return false;
        }
    }
    key[cipher_index] = plain_letter;
    return true;
}

std::string MonoalphabeticCipher::key_to_string(const Key& key) {
    std::ostringstream output;
    for (int i = 0; i < 26; ++i) {
        if (i) output << ' ';
        output << static_cast<char>('A' + i) << "->"
               << (key[i] == '?' ? '_' : key[i]);
    }
    return output.str();
}

std::string MonoalphabeticCipher::normalize_key(const std::string& key_text) {
    std::string letters;
    for (char value : key_text)
        if (letter(value)) letters += upper(value);
    return letters;
}
