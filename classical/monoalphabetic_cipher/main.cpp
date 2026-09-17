#include "monoalphabetic_cipher.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <map>
#include <random>
#include <sstream>

namespace {
std::string read_file(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("Unable to open input file: " + path);
    std::ostringstream contents;
    contents << input.rdbuf();
    return contents.str();
}

MonoalphabeticCipher::Key random_key() {
    auto key = MonoalphabeticCipher::identity_key();
    std::random_device source;
    std::mt19937 generator(source());
    std::shuffle(key.begin(), key.end(), generator);
    return key;
}

void show_key(const MonoalphabeticCipher::Key& key) {
    std::cout << "\nCiphertext -> plaintext key:\n"
              << MonoalphabeticCipher::key_to_string(key) << '\n';
}

void propose_frequency_mappings(const std::string& ciphertext) {
    std::map<char, int> counts;
    for (char value : ciphertext) {
        if (std::isalpha(static_cast<unsigned char>(value)))
            ++counts[static_cast<char>(std::toupper(static_cast<unsigned char>(value)))];
    }
    std::vector<std::pair<char, int>> ranked(counts.begin(), counts.end());
    std::sort(ranked.begin(), ranked.end(),
              [](const auto& left, const auto& right) {
                  if (left.second != right.second) return left.second > right.second;
                  return left.first < right.first;
              });
    const std::string english_order = "ETAOINSHRDLU";
    std::cout << "Frequency-based proposals (test each with 'map C P'; reject any bad guess):\n";
    for (std::size_t i = 0; i < ranked.size() && i < english_order.size(); ++i)
        std::cout << "  " << ranked[i].first << " -> " << english_order[i]
                  << " (" << ranked[i].second << " occurrences)\n";
}

void interactive_cryptanalysis(const std::string& ciphertext,
                               const std::string& known_plaintext,
                               MonoalphabeticCipher& cipher) {
    auto candidate = MonoalphabeticCipher::identity_key();
    candidate.fill('?');
    std::cout << "\n=== Iterative cryptanalysis ===\n"
              << "Enter hypotheses as 'map C P' (ciphertext letter C means plaintext P).\n"
              << "Use 'propose' for frequency-based candidate substitutions.\n"
              << "Use 'reject' to reject the last proposed mapping, 'show' to preview,\n"
              << "and 'done' after meaningful plaintext is recovered.\n";

    std::vector<std::pair<char, char>> proposals;
    std::string line;
    while (true) {
        std::cout << "\nHypothesis> ";
        if (!std::getline(std::cin, line)) break;
        std::istringstream input(line);
        std::string command;
        input >> command;
        if (command == "map") {
            char encrypted, plain;
            if (!(input >> encrypted >> plain)) {
                std::cout << "Usage: map C P\n";
                continue;
            }
            std::string error;
            if (MonoalphabeticCipher::assign_mapping(candidate, encrypted, plain, error)) {
                proposals.emplace_back(encrypted, plain);
                std::cout << "Accepted hypothesis " << static_cast<char>(std::toupper(encrypted))
                          << " -> " << static_cast<char>(std::toupper(plain)) << ".\n";
                cipher.display_partial_plaintext(ciphertext, candidate);
            } else {
                std::cout << "Rejected hypothesis: " << error << '\n';
            }
        } else if (command == "propose") {
            propose_frequency_mappings(ciphertext);
        } else if (command == "reject") {
            if (proposals.empty()) {
                std::cout << "No hypothesis to reject.\n";
                continue;
            }
            auto [encrypted, plain] = proposals.back();
            candidate[std::toupper(static_cast<unsigned char>(encrypted)) - 'A'] = '?';
            proposals.pop_back();
            std::cout << "Rejected " << encrypted << " -> " << plain << ".\n";
            cipher.display_partial_plaintext(ciphertext, candidate);
        } else if (command == "show") {
            cipher.display_partial_plaintext(ciphertext, candidate);
            show_key(candidate);
        } else if (command == "done") {
            break;
        } else {
            std::cout << "Commands: map C P, propose, reject, show, done.\n";
        }
    }

    if (!known_plaintext.empty()) {
        if (cipher.verify_solution(ciphertext, known_plaintext, candidate)) show_key(candidate);
        else std::cout << "The current hypotheses are incomplete or incorrect.\n";
    }
}
}

int main(int argc, char* argv[]) {
    try {
        std::string plaintext;
        if (argc == 3 && std::string(argv[1]) == "--plaintext-file") {
            plaintext = read_file(argv[2]);
        } else if (argc == 2 && std::string(argv[1]) == "--demo") {
            std::cout << "Enter plaintext (a file is recommended for a 1+ page sample):\n";
            std::ostringstream input;
            input << std::cin.rdbuf();
            plaintext = input.str();
        } else {
            std::cerr << "Usage: " << argv[0] << " --plaintext-file path\n"
                      << "       " << argv[0] << " --demo < plaintext.txt\n";
            return 2;
        }
        if (plaintext.empty()) throw std::runtime_error("Plaintext must not be empty.");

        MonoalphabeticCipher cipher;
        const auto encryption_key = random_key();
        const std::string ciphertext = cipher.encrypt(plaintext, encryption_key);
        std::cout << "=== Monoalphabetic substitution workflow ===\n"
                  << "Plaintext characters: " << plaintext.size() << "\n"
                  << "\nCiphertext:\n" << ciphertext << '\n';
        cipher.frequency_analysis(ciphertext);
        cipher.word_frequency_analysis(ciphertext);
        cipher.pattern_analysis(ciphertext);
        std::cout << "\nEncryption key is generated randomly and is not shown during analysis.\n";

        interactive_cryptanalysis(ciphertext, plaintext, cipher);
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
