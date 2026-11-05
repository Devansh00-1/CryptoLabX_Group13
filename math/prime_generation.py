"""Generate and independently verify cryptographic-size probable primes.

Run with ``python -m math.prime_generation``. SymPy is used only for the
independent final verification; candidate generation relies on ``secrets``.
"""

from dataclasses import dataclass, replace
import secrets
import time


@dataclass(frozen=True)
class GenerationResult:
    prime: int
    candidates_tested: int
    rounds_performed: int
    elapsed_seconds: float
    miller_rabin_rounds: int


def generate_odd_candidate(bits: int = 512) -> int:
    """Return a cryptographically random odd integer with exactly ``bits`` bits."""
    if bits < 2:
        raise ValueError("bits must be at least 2")
    return secrets.randbits(bits) | (1 << (bits - 1)) | 1


def _miller_rabin(number: int, rounds: int) -> tuple[bool, int]:
    """Return the Miller–Rabin result and the actual number of bases tested."""
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    if number < 2:
        return False, 0
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if number == prime:
            return True, 0
        if number % prime == 0:
            return False, 0

    # Factor n - 1 as d * 2**s, with d odd.
    d = number - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    performed = 0
    for _ in range(rounds):
        performed += 1
        base = secrets.randbelow(number - 3) + 2  # Uniform in [2, n - 2].
        value = pow(base, d, number)
        if value in (1, number - 1):
            continue
        for _ in range(s - 1):
            value = pow(value, 2, number)
            if value == number - 1:
                break
        else:
            return False, performed
    return True, performed


def is_probable_prime(number: int, rounds: int = 40) -> bool:
    """Perform the Miller–Rabin test using independently random bases."""
    return _miller_rabin(number, rounds)[0]


def generate_probable_prime(bits: int = 512, rounds: int = 40) -> GenerationResult:
    """Search random odd candidates until Miller–Rabin accepts one."""
    if bits < 2:
        raise ValueError("bits must be at least 2")
    if rounds < 1:
        raise ValueError("rounds must be at least 1")

    candidates_tested = rounds_performed = 0
    started = time.perf_counter()
    while True:
        candidate = generate_odd_candidate(bits)
        candidates_tested += 1
        # Small-prime filtering avoids spending full MR rounds on obvious composites.
        small_primes = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
        if candidate != 3 and any(candidate % p == 0 for p in small_primes):
            continue
        probable_prime, performed = _miller_rabin(candidate, rounds)
        rounds_performed += performed
        if probable_prime:
            elapsed = time.perf_counter() - started
            return GenerationResult(candidate, candidates_tested, rounds_performed,
                                    elapsed, rounds)


def verify_with_sympy(number: int) -> bool:
    """Independently verify primality with SymPy, with a useful install error."""
    try:
        from sympy import isprime
    except ImportError as error:
        raise RuntimeError(
            "SymPy is required for independent verification; install it with "
            "'python -m pip install sympy'."
        ) from error
    return bool(isprime(number))


def _print_results(result: GenerationResult, verified: bool, bits: int) -> None:
    """Print experiment parameters and outcomes as a readable table."""
    rows = (
        ("Requested size (bits)", str(bits)),
        ("Prime (hex)", hex(result.prime)),
        ("Bit length", str(result.prime.bit_length())),
        ("Candidate generation", "secrets.randbits; high and low bits set"),
        ("Miller–Rabin bases", f"up to {result.miller_rabin_rounds} independent CSPRNG bases in [2, n-2] per candidate"),
        ("Miller–Rabin rounds per candidate", str(result.miller_rabin_rounds)),
        ("Candidates tested", str(result.candidates_tested)),
        ("Miller–Rabin rounds performed", str(result.rounds_performed)),
        ("Execution time (seconds)", f"{result.elapsed_seconds:.6f}"),
        ("SymPy verification", "PASS" if verified else "FAIL"),
    )
    width = max(len(key) for key, _ in rows)
    print(f"| {'Parameter'.ljust(width)} | Result |")
    print(f"| {'-' * width} | {'-' * 70} |")
    for key, value in rows:
        print(f"| {key.ljust(width)} | {value} |")


def main() -> None:
    bits, rounds = 512, 40
    experiment_started = time.perf_counter()
    result = generate_probable_prime(bits=bits, rounds=rounds)
    if result.prime.bit_length() != bits:
        raise RuntimeError("Generated candidate does not have exactly 512 bits")
    verified = verify_with_sympy(result.prime)
    # Report total experiment time, including the independent verification.
    result = replace(result, elapsed_seconds=time.perf_counter() - experiment_started)
    _print_results(result, verified, bits)
    if not verified:
        raise RuntimeError("SymPy rejected the generated probable prime")


if __name__ == "__main__":
    main()
