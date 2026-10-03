# Binary Search

One file per technique family: implementation + tests, checked against brute force. Explanations: Binary Search — Field Guide.

```
python3 binary_search/templates.py                                   # one file
for f in binary_search/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| First true of a monotone predicate, lower/upper bound | [templates.py](templates.py) |
| First/last position, count, insert position, floor/ceil, k closest | [occurrences.py](occurrences.py) |
| Rotated sorted array: min, search, duplicates | [rotated_array.py](rotated_array.py) |
| Peak element, mountain / bitonic array, 2D peak | [peak_finding.py](peak_finding.py) |
| Min-max / max-min: Koko, ship capacity, split array, bouquets | [answer_search.py](answer_search.py) |
| sqrt, roots to a precision, max average, fractional answers | [real_valued.py](real_valued.py) |
| 2D matrix: row-major flatten vs staircase | [matrix_search.py](matrix_search.py) |
| Median / k-th of two sorted arrays | [two_arrays.py](two_arrays.py) |
| K-th smallest in matrix, multiplication table, pair distance | [kth_by_value.py](kth_by_value.py) |

**Conventions:** half-open `[lo, hi)`, `while lo < hi`, predicate `F..F T..T`; "not found" is `-1` (or `hi`); `k` is 1-based.
