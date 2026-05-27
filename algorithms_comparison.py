"""
Substring Search Algorithm Benchmark
-----------------------------------------------------------
Compares following algorithms on two Ukrainian-language academic articles.
    >> Boyer-Moore 
    >> Knuth-Morris-Pratt (KMP)
    >> Rabin-Karp
"""

import timeit 
from functools import wraps
from pathlib import Path
from typing import Callable, Optional

# GLOBAL VARIABLES
CURRENT_PATH = Path(__file__).resolve().parent
TXT_ARTICLE_01 = CURRENT_PATH / "article_01.txt"
TXT_ARTICLE_02 = CURRENT_PATH / "article_02.txt"

EXIST_SUB_STR_ART_01 = ("if (integers[previousStep] == elementToSearch)")
EXIST_SUB_STR_ART_02 = ("Здійснюється пошук усіх предметів, які належать")
NOT_EXIST_SUB_STR_ART= ("алгоритми та структури данних | Neoversity")

REPEAT_ALG: int = 10


# DECORATOR
def algorithm_benchmark(repeats: int = REPEAT_ALG) -> Callable:
    """
    Decorator that benchmarks a search function over *repeats* runs.
    Returns a dict with:
        func_name       - name of the wrapped function
        result          - return value of the last call
        mean_time       - average wall-clock time (seconds)
        min_time        - best run (seconds)
        max_time        - worst run (seconds)
        runs            - number of repetitions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> dict:
            timing_samples = []
            
            for _ in range(repeats):
                start = timeit.default_timer()
                func_result = func(*args, **kwargs)
                timing_samples.append(timeit.default_timer() - start)

            return {
                "func_name" : f"{func.__name__}",
                "result"    : func_result, 
                "mean_time" : sum(timing_samples) / len(timing_samples), 
                "min_time"  : min(timing_samples), 
                "max_time"  : max(timing_samples), 
                "runs"      : repeats
            }
            
        return wrapper
    return decorator 


# 1. BOYER-MOORE
def _bm_bad_char_table(pattern: str) -> dict:
    """Build the bad-character shift table for Boyer-Moore."""
    table: dict[str, int] = {}
    m = len(pattern)
    for i, ch in enumerate(pattern):
        table[ch] = m - i - 1
    return table


def _bm_good_suffix_table(pattern: str) -> list[int]:
    """Build the good-suffix shift table for Boyer-Moore."""
    m = len(pattern)
    shift = [m] * (m + 1)
    border = [0] * (m + 1)

    i, j = m, m + 1
    border[i] = j
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if shift[j] == m:
                shift[j] = j - i
            j = border[j]
        i -= 1
        j -= 1
        border[i] = j

    j = border[0]
    for i in range(m + 1):
        if shift[i] == m:
            shift[i] = j
        if i == j:
            j = border[j]

    return shift


def boyer_moore_search(text: str, pattern: str) -> Optional[int]:
    """
    Boyer-Moore substring search.
    Returns the index of the first match, or None if not found.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None

    bad_char  = _bm_bad_char_table(pattern)
    good_suf  = _bm_good_suffix_table(pattern)

    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            return s
        bc_shift = bad_char.get(text[s + j], m)
        gs_shift = good_suf[j + 1]
        s += max(bc_shift, gs_shift)

    return None


# 2. KNUTH-MORRIS-PRATT (KMP)
def _kmp_failure_function(pattern: str) -> list[int]:
    """Compute the KMP failure (partial-match) table."""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> Optional[int]:
    """
    Knuth-Morris-Pratt substring search.
    Returns the index of the first match, or None if not found.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None

    lps = _kmp_failure_function(pattern)
    i = j = 0
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            return i - j
        elif i < n and text[i] != pattern[j]:
            if j:
                j = lps[j - 1]
            else:
                i += 1
    return None


# 3. RABIN-KARP
_RK_BASE  = 256
_RK_PRIME = 101

def rabin_karp_search(text: str, pattern: str) -> Optional[int]:
    """
    Rabin-Karp substring search (rolling hash).
    Returns the index of the first match, or None if not found.
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return None

    d = _RK_BASE
    q = _RK_PRIME
    h = pow(d, m - 1, q)

    p_hash = 0
    t_hash = 0
    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % q
        t_hash = (d * t_hash + ord(text[i]))   % q

    for i in range(n - m + 1):
        if p_hash == t_hash:
            if text[i:i + m] == pattern:
                return i
        if i < n - m:
            t_hash = (d * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % q
            if t_hash < 0:
                t_hash += q

    return None


# BENCHMARK RUNNER
def run_benchmarks(text: str, pattern: str, label: str) -> dict:
    """
    Wrap all three algorithms with the benchmark decorator and run them.
    Returns a dict keyed by algorithm name.
    """
    bm_  = algorithm_benchmark(REPEAT_ALG)(boyer_moore_search)
    kmp_ = algorithm_benchmark(REPEAT_ALG)(kmp_search)
    rk_  = algorithm_benchmark(REPEAT_ALG)(rabin_karp_search)

    results = {
        "Boyer-Moore":  bm_(text, pattern),
        "KMP":          kmp_(text, pattern),
        "Rabin-Karp":   rk_(text, pattern),
    }

    print(f"\n{'─'*62}")
    print(f"  {label}")
    print(f"  Pattern : \"{pattern[:55]}{'…' if len(pattern) > 55 else ''}\"")
    print(f"  Found   : {next(iter(results.values()))['result']}")
    print(f"{'─'*62}")
    print(f"  {'Algorithm':<18} {'Mean (µs)':>12} {'Min (µs)':>11} {'Max (µs)':>11}")
    print(f"  {'─'*18} {'─'*12} {'─'*11} {'─'*11}")
    for algo, data in results.items():
        print(
            f"  {algo:<18} "
            f"{data['mean_time']*1e6:>12.4f} "
            f"{data['min_time']*1e6:>11.4f} "
            f"{data['max_time']*1e6:>11.4f}"
        )
    fastest = min(results, key=lambda k: results[k]["mean_time"])
    print(f"\n    Fastest: {fastest} "
          f"({results[fastest]['mean_time']*1e6:.4f} µs mean)\n")

    return results


# MAIN
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    text1 = load_text(TXT_ARTICLE_01)
    text2 = load_text(TXT_ARTICLE_02)

    print("\n" + "═"*62)
    print("  SUBSTRING SEARCH ALGORITHM BENCHMARK")
    print("  Boyer-Moore  |  KMP  |  Rabin-Karp")
    print("═"*62)

    # Article 1 
    r1_exist = run_benchmarks(
        text1, EXIST_SUB_STR_ART_01,
        "Article 1 -> EXISTING substring"
    )
    r1_fake = run_benchmarks(
        text1, NOT_EXIST_SUB_STR_ART,
        "Article 1 -> NON-EXISTENT substring"
    )

    # Article 2
    r2_exist = run_benchmarks(
        text2, EXIST_SUB_STR_ART_02,
        "Article 2 -> EXISTING substring"
    )
    r2_fake = run_benchmarks(
        text2, NOT_EXIST_SUB_STR_ART,
        "Article 2 -> NON-EXISTENT substring"
    )

    # Overall summary
    print("═"*62)
    print("  OVERALL SUMMARY (mean times in µs)")
    print("═"*62)
    all_scenarios = {
        "Art1 – exist":    r1_exist,
        "Art1 – no-exist": r1_fake,
        "Art2 – exist":    r2_exist,
        "Art2 – no-exist": r2_fake,
    }
    algos = ["Boyer-Moore", "KMP", "Rabin-Karp"]
    print(f"\n  {'Scenario':<22} " + "  ".join(f"{a:<14}" for a in algos))
    print(f"  {'─'*22} " + "  ".join("─"*14 for _ in algos))

    algo_total: dict[str, float] = {a: 0.0 for a in algos}
    for scenario, results in all_scenarios.items():
        row = f"  {scenario:<22}"
        for algo in algos:
            t = results[algo]["mean_time"] * 1e6
            algo_total[algo] += t
            row += f"  {t:>12.4f}  "
        print(row)

    print(f"  {'─'*22} " + "  ".join("─"*14 for _ in algos))
    total_row = f"  {'TOTAL':<22}"
    for algo in algos:
        total_row += f"  {algo_total[algo]:>12.4f}  "
    print(total_row)

    overall_winner = min(algo_total, key=algo_total.get)
    print(f"\n    Overall fastest: {overall_winner} "
          f"(cumulative mean {algo_total[overall_winner]:.4f} µs)\n")

    # Return structured data for report generation
    return all_scenarios, algo_total


if __name__ == "__main__":
    main()