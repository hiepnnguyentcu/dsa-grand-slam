# Bit Manipulation

One file per technique: implementation + tests. Explanations: [Bit Manipulation — Field Guide](FIELD_GUIDE_URL).

```
python3 bit_manipulation/xor_tricks.py                                   # one file
for f in bit_manipulation/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Get / set / clear / flip a bit, lowest set bit, power of two / four, 32-bit emulation | [bit_basics.py](bit_basics.py) |
| One element unpaired (twice / thrice), missing number, XOR of 0..n | [xor_tricks.py](xor_tricks.py) |
| Popcount for 0..n, number of 1 bits, Hamming distance (pairs, total) | [counting_bits.py](counting_bits.py) |
| Add / multiply without operators, reverse bits, AND of a range | [bit_arithmetic.py](bit_arithmetic.py) |
| Subsets, submasks, k-subsets (Gosper), letter masks, Gray code | [bitmask_sets.py](bitmask_sets.py) |
| XOR-equal triplets, distinct subarray ORs, decode adjacent XORs | [subarray_bitwise.py](subarray_bitwise.py) |

Related: subset DP in [bitmask_dp.py](../dynamic_programming/bitmask_dp.py), max XOR pair in [bitwise_trie.py](../tries/bitwise_trie.py), divide without `/` in [integer_division.py](../math_algorithms/integer_division.py), subarray XOR = k in [prefix_hashmap.py](../prefix_sums/prefix_hashmap.py).

**Conventions:** bit `i` = value `1 << i`; "32-bit" means mask with `0xFFFFFFFF`, then map `>= 2^31` back to negative.
