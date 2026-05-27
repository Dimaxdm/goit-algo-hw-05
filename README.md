# Homework Assigment Description
Compare the efficiency of the following substring search algorithms:
* Boyer-Moore
* Knuth-Morris-Pratt (KMP)
* Rabin-Karp

Use two text files (*article_01.txt* and *article_02.txt*) as the basis for your comparison. 

Using Python's `timeit` module, measure the execution time of each algorithm for two types of substrings: 
1. A substring that actually exist in the text.
2. A fictional/nonexistent substring (you may choose the substrings yourself).

Based on the collected data, determine:
* The fastest algorithm for each text separately.
* The fastest algorithm overall.

## Requirements
* Implement the substring search algorithms programmatically:
    * Boyer-Moore
    * Knuth-Morris-Pratt (KMP)
    * Rabin-Karp
* Based on the execution results of all three algorithms, determine the fastest algorithm for each of the two texts.
    * first text  -> Article 1 (see text file *aritcle_01.txt*)
    * second text -> Article 2 (see text file *article_02.txt*)
* Draw conclusions about the performance of the algorithms for:
    * Each text individually.
    * the overall comparison.
* Present your conclusions in a **Markdown** document (current document).


# Substring Search Algorithm Benchmark - Conclusions
## 1. Setup

| Item | Value |
|---|---|
| Repetitions per measurement | 10 |
| Timer | `timeit.default_timer()` (wall-clock) |
| Text encoding | UTF-8 |
| Pattern type A | Substring that **exists** in the target article |
| Pattern type B | Substring that **does not exist** in either article | 

## Patterns used 

| ID | Pattern | Present in |
|---|---|---|
| P1 | `"if (integers[previousStep] == elementToSearch)"` | Article 1 only |
| P2 | `"Здійснюється пошук усіх предметів, які належать"` | Article 2 only |
| P3 | `""алгоритми та структури данних \| Neoversity""` | Neither article |

---
## 2. Raw Benchmark Results (mean time in µs)

### Article 1

<img width="585" height="548" alt="image" src="https://github.com/user-attachments/assets/c136e0c3-a6cd-418d-80e4-23327db9ff01" />

### Article 2

<img width="573" height="549" alt="image" src="https://github.com/user-attachments/assets/0a2c6936-3529-4d40-b7ba-6cfa46649433" />

--- 

## 3. Summary - Fastest per Scenario $ Overall Ranking (cumulative mean time across all 4 scenarios)

<img width="656" height="299" alt="image" src="https://github.com/user-attachments/assets/31fa89dd-1aa8-4388-a8f0-e7dbbb1ac61c" />

## 4. Conclusions

### 4.1 Fastest algorithm for Article 1
**Boyer–Moore** dominated all measurements on Article 1, running in ≈ 96 µs (existing pattern) and ≈ 205 µs (non-existent pattern) - roughly **15×** faster than KMP and **20×** faster than Rabin–Karp in the same scenarios.

### 5.2 Fastest algorithm for Article 2
**Boyer–Moore** was again the clear winner on Article 2, with ≈ 288 µs for an existing pattern and ≈ 289 µs for a missing one. The speed advantage over the other two algorithms remained consistent (~11–17×).

### 5.3 Overall fastest algorithm
**Boyer–Moore** is the overall winner across both articles and both pattern types. Its cumulative mean time of **877 µs** is **14×** lower than KMP (12 330 µs) and nearly **18×** lower than Rabin–Karp (15 851 µs).

### 5.4 Why Boyer–Moore wins here
Boyer–Moore's **bad-character** and **good-suffix** heuristics let it skip large portions of the text on every mismatch - often jumping several characters at once.
Because the Ukrainian text is rich in multi-byte UTF-8 characters that appear infrequently in the pattern, the bad-character table produces large skip values, which dramatically reduces the number of comparisons.

### 5.5 Why KMP was slower than expected
KMP guarantees O(n + m) time and is excellent when the alphabet is very small (e.g. binary DNA sequences). In natural language with a large and varied alphabet, the failure function rarely rescues many comparisons, so KMP ends up paying the full O(n) scan with non-trivial overhead from table lookups.

### 5.6 Why Rabin–Karp was slowest
Rabin–Karp's rolling hash requires arithmetic on every single character of the text (mod, multiply, add). The constant overhead of these operations dominates for short-to-medium patterns in long text, making it uncompetitive here. Rabin–Karp shines in **multi-pattern** scenarios (searching for many patterns simultaneously), which was not tested here.

### 5.7 Non-existent vs. existing substrings
In all three algorithms, searching for a **non-existent** substring was *slower* than finding an existing one — the algorithm is forced to scan the entire text before confirming absence. The gap is most visible in Rabin–Karp (~20 % slower on Article 2) and KMP (~16 % slower on Article 2), while Boyer–Moore remains the least affected.

---
## 6. Practical Recommendations

| Use case | Recommended algorithm |
|---|---|
| Single-pattern search in natural language text | **Boyer–Moore** |
| Binary / very-small-alphabet strings (e.g. DNA) | **KMP** |
| Multi-pattern search in the same text | **Rabin–Karp** |
| Simplicity + correctness with moderate speed | **KMP** |
