# OS random generation evaluation

Open `evaluation_of_os_random_generation.ipynb` and run all cells. The notebook captures 1 MiB from each mechanism that is genuinely available on the host, analyzes byte and bit frequencies, repeated patterns, serial correlations, and statistical tests, and produces histograms and a comparison table.

## Requirements

- Python 3.10 or later
- `numpy` and `matplotlib`
- OpenSSL executable on `PATH` for the OpenSSL sample
- Windows for the Windows CNG sample; the implementation uses `BCryptGenRandom` via `ctypes`
- Linux for the Linux `/dev/urandom` sample

Install Python dependencies with `pip install numpy matplotlib`. The project root already lists both dependencies. Run Jupyter from either this directory or the repository root; the notebook resolves the supporting module in either case.

The generated captures are written to `data/` and are ignored by Git. Do not distribute them. On macOS, OpenSSL may run, but the notebook explicitly does not count macOS `/dev/urandom` as the Linux mechanism. Run separately on native Linux and Windows systems for a complete three-way comparison. Results are runtime measurements and are intentionally not fabricated or prefilled.

## Method caveats

The chi-square, monobit, runs, and byte-autocorrelation p-values are diagnostics under simplified null-model assumptions. The code reports repeated identical-byte runs and duplicate aligned four-byte blocks; these do not exhaustively enumerate every possible repeated substring. Statistical tests cannot demonstrate cryptographic unpredictability or adequate entropy.
