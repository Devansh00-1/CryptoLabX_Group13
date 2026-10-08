# Lab Assignment 4: Cryptanalysis of Shift Cipher

**Purpose:** Cryptanalysis of Shift Cipher using Brute Force, Dictionary Scoring, and Chi-Square Analysis.

---

## 1. Algorithms of Cryptanalysis

### Algorithm 1: Brute Force with Dictionary Scoring
This method systematically tries every possible key in the keyspace (shifts 0 through 25). For each resulting candidate plaintext, the algorithm splits the text into separate words and checks them against an English dictionary (`english_words.txt`). Each candidate is assigned a score based on how many valid English words it contains. The shift that produces the plaintext with the highest number of dictionary word matches is predicted as the correct key.

### Algorithm 2: Chi-Square Analysis
This statistical attack relies on the expected frequencies of letters in the English language (e.g., 'E' is ~12.7%, 'T' is ~9.1%). For each possible shift (0-25), the algorithm counts the occurrences of each letter in the decrypted candidate. It then calculates the Chi-Square statistic formula: `Sum( (Observed - Expected)^2 / Expected )` across all 26 letters. A lower Chi-Square value indicates a closer match to expected English distributions. The shift producing the lowest Chi-Square value is selected as the key.

---

## 2. Comparison: Dictionary Scoring vs. Chi-Square Analysis

*   **Speed & Efficiency:** Chi-Square is significantly faster. It only requires simple mathematical operations and letter counting. Dictionary scoring requires string splitting and searching through a potentially massive set of dictionary words.
*   **Accuracy on Short Texts:** Dictionary scoring is vastly superior on short phrases (e.g., "hello world") because a few valid words instantly yield a high score. Chi-Square fails here because short texts lack the sample size needed to match statistical language averages.
*   **Resilience to Unknown Words:** Chi-Square excels when text contains proper nouns, typos, or abbreviations (which would fail dictionary lookups) because it only evaluates the underlying character distribution.
*   **Accuracy on Long Texts:** Both perform well on long texts, but Chi-Square is the standard for automated statistical cryptanalysis of long ciphertexts.

---

## 3. Failure Analysis

*   **Dictionary Scoring Failure (Test Case 3: `short msg`)**
    *   **Why it failed:** The abbreviation "msg" was not present in the dictionary. The score for the correct shift tied with other shifts, and the algorithm defaulted to a lower shift (0).
    *   **Improvement:** Expand the dictionary file to include common slang, names, and abbreviations. Alternatively, implement a partial-word scoring system or n-gram analysis instead of strict full-word matching.
*   **Chi-Square Failure (Test Cases 1 & 5: `hello world`, `wx`)**
    *   **Why it failed:** Statistical attacks require a sufficient sample size (typically 40+ characters) to reliably mirror expected language frequencies. A small 10-character string like "hello world" has distorted frequencies (e.g., three 'l's and two 'o's), causing the math to predict an incorrect shift (8).
    *   **Improvement:** Implement a hybrid approach. Use bigram/trigram frequencies which capture structure better in short texts, or automatically fall back to Dictionary Scoring if the ciphertext length is under a specific threshold (e.g., 30 characters).

---

## 4. Observations

Based on the experimental results, it was observed that Chi-Square analysis shines on large blocks of standard English text (e.g., the cryptography definition test case) but fails miserably on short phrases or isolated words. Conversely, the Brute Force Dictionary approach is highly reliable for short, grammatically correct sentences but breaks down if the ciphertext contains abbreviations or words outside its specific `english_words.txt` file.

---

## 5. Conclusion

The cryptanalysis of the Shift Cipher demonstrates that while the cipher is trivially broken due to its tiny key space (26), the methodology used to automatically verify the correct key dictates the attack's success. Statistical methods (Chi-Square) require larger ciphertext samples, whereas linguistic methods (Dictionary) require comprehensive wordlists. Combining both approaches yields an extremely robust automated attack against historical ciphers.

---

## 6. Results Table

| Test Case | Actual Key | Dictionary Key | Chi-Square Key | Dictionary Correct? | Chi-Square Correct? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `hello world` | 5 | 5 | 8 | Yes | No |
| `this is a longer test case...` | 12 | 12 | 12 | Yes | Yes |
| `short msg` | 3 | 0 | 17 | No | No |
| `cryptography is the practice...`| 20 | 20 | 20 | Yes | Yes |
| `wx` | 1 | 0 | 5 | No | No |
