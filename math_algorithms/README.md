# Math

One file per technique: implementation + tests. Explanations: [Math — Field Guide](https://claude.ai/code/artifact/4b1830c1-4c61-4508-8f97-25f8c017b5a5).

```
python3 math_algorithms/fast_power.py                                   # one file
for f in math_algorithms/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Huge exponent, `x^n mod m`, n-th term of a recurrence | [fast_power.py](fast_power.py) |
| Simplify fractions, common periods, Bezout, water jugs | [gcd_lcm.py](gcd_lcm.py) |
| All primes up to N, factorise many numbers | [sieve.py](sieve.py) |
| Is n prime, factorise one n, divisors | [primes.py](primes.py) |
| n-th ugly / super-ugly number | [smooth_numbers.py](smooth_numbers.py) |
| "Answer mod 10^9 + 7", modular inverse | [modular.py](modular.py) |
| C(n, k), Pascal's triangle | [binomial.py](binomial.py) |
| Grid paths, stars and bars, Catalan, inclusion-exclusion, pigeonhole | [counting.py](counting.py) |
| Floor / ceil / truncate on negatives, divide without `/` | [integer_division.py](integer_division.py) |
| Base k, base -2, Excel columns, Roman numerals, English words | [base_conversion.py](base_conversion.py) |
| Add / subtract / multiply numbers given as strings | [big_number_strings.py](big_number_strings.py) |
| Turns, collinearity, slopes, rectangles, squares, convex hull | [geometry.py](geometry.py) |
| Shuffle, reservoir sampling, weighted pick, rand10 from rand7 | [randomized.py](randomized.py) |
| Reverse digits, palindrome number, 32-bit overflow, atoi | [digits.py](digits.py) |
