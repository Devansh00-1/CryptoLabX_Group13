"""Generation and lightweight statistical analysis for OS random streams."""
from __future__ import annotations

import math
import os
import platform
import shutil
import subprocess
from pathlib import Path

import numpy as np


SAMPLE_SIZE = 1024 * 1024


def generate_samples(output_dir: Path, size: int = SAMPLE_SIZE) -> dict[str, bytes | None]:
    """Generate byte streams with each real platform mechanism available."""
    output_dir.mkdir(parents=True, exist_ok=True)
    samples: dict[str, bytes | None] = {}

    if platform.system() == "Linux" and Path("/dev/urandom").exists():
        with Path("/dev/urandom").open("rb") as source:
            data = source.read(size)
        (output_dir / "linux_dev_urandom.bin").write_bytes(data)
        samples["Linux /dev/urandom"] = data

    openssl = shutil.which("openssl")
    if openssl:
        target = output_dir / "openssl_rand.bin"
        subprocess.run([openssl, "rand", "-out", str(target), str(size)], check=True)
        data = target.read_bytes()
        samples["OpenSSL rand"] = data

    if os.name == "nt":
        # BCryptGenRandom with BCRYPT_USE_SYSTEM_PREFERRED_RNG uses Windows CNG.
        import ctypes
        from ctypes import wintypes

        bcrypt = ctypes.WinDLL("bcrypt")
        fn = bcrypt.BCryptGenRandom
        fn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, wintypes.ULONG, wintypes.ULONG]
        fn.restype = wintypes.LONG
        buf = (ctypes.c_ubyte * size)()
        status = fn(None, buf, size, 0x00000002)
        if status != 0:
            raise OSError(f"BCryptGenRandom failed: NTSTATUS 0x{status & 0xffffffff:08x}")
        data = bytes(buf)
        (output_dir / "windows_cng.bin").write_bytes(data)
        samples["Windows CNG"] = data
    else:
        samples["Windows CNG"] = None
    return samples


def _gamma_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma, for chi-square p-values."""
    if x < 0 or a <= 0:
        return float("nan")
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:
        ap, summ, delta = a, 1.0 / a, 1.0 / a
        for _ in range(10000):
            ap += 1
            delta *= x / ap
            summ += delta
            if abs(delta) < abs(summ) * 1e-14:
                break
        return max(0.0, min(1.0, 1.0 - summ * math.exp(-x + a * math.log(x) - gln)))
    b = x + 1 - a
    c, d, h = 1e300, 1 / b, 1 / b
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return max(0.0, min(1.0, math.exp(-x + a * math.log(x) - gln) * h))


def analyze(data: bytes, max_lag: int = 16) -> dict:
    """Compute byte/bit summaries and approximate statistical test p-values."""
    if not data:
        raise ValueError("Sample must not be empty")
    arr = np.frombuffer(data, dtype=np.uint8)
    n = int(arr.size)
    counts = np.bincount(arr, minlength=256)
    expected = n / 256
    chi2 = float(np.sum((counts - expected) ** 2 / expected))

    bits = np.unpackbits(arr)
    ones = int(bits.sum())
    bit_count = int(bits.size)
    monobit_z = (ones - bit_count / 2) / math.sqrt(bit_count / 4)
    monobit_p = math.erfc(abs(monobit_z) / math.sqrt(2))
    transitions = int(np.count_nonzero(bits[1:] != bits[:-1]))
    pi = ones / bit_count
    runs = transitions + 1
    expected_runs = 2 * bit_count * pi * (1 - pi) + 1
    run_var = 2 * bit_count * pi * (1 - pi) * (2 * bit_count * pi * (1 - pi) - 1) / (bit_count - 1)
    if abs(pi - 0.5) >= 2 / math.sqrt(bit_count) or run_var <= 0:
        runs_p = 0.0
    else:
        runs_p = math.erfc(abs(runs - expected_runs) / math.sqrt(2 * run_var))

    # Exact repeated-byte runs and repeated aligned 4-byte blocks.
    boundaries = np.flatnonzero(arr[1:] != arr[:-1])
    run_lengths = np.diff(np.concatenate(([-1], boundaries, [n - 1])))
    max_repeat = int(run_lengths.max())
    block_view = np.frombuffer(data[: n - n % 4], dtype="V4")
    _, block_counts = np.unique(block_view, return_counts=True)
    repeated_blocks = int(np.sum(block_counts[block_counts > 1] - 1))
    correlations = {}
    x = arr.astype(np.float64)
    x -= x.mean()
    denom = float(np.dot(x, x))
    for lag in range(1, max_lag + 1):
        corr = float(np.dot(x[:-lag], x[lag:]) / denom)
        correlations[lag] = {"correlation": corr, "z": corr * math.sqrt(n), "p_value": math.erfc(abs(corr * math.sqrt(n)) / math.sqrt(2))}

    return {
        "bytes": n, "byte_counts": counts.tolist(), "byte_chi_square": chi2,
        "byte_chi_square_df": 255, "byte_chi_square_p": _gamma_q(255 / 2, chi2 / 2),
        "ones": ones, "zeros": bit_count - ones, "bit_proportion_ones": pi,
        "monobit_z": monobit_z, "monobit_p": monobit_p,
        "bit_runs": runs, "runs_expected": expected_runs, "runs_p": runs_p,
        "max_repeated_byte_run": max_repeat, "repeated_aligned_4byte_blocks": repeated_blocks,
        "autocorrelation": correlations,
    }
