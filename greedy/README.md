# Greedy

One file per technique family: implementation + tests, checked against brute force. Explanations: [Greedy — Field Guide](https://claude.ai/code/artifact/0274a374-e893-43e9-b66a-6e5b667cd5f7).

```
python3 greedy/reachability.py                                   # one file
for f in greedy/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Prove it (exchange, stays ahead); coins where greedy fails | [proofs.py](proofs.py) |
| Reach the end, fewest jumps, cover [0, T] | [reachability.py](reachability.py) |
| Gas station, running sum ≥ 1, stock II | [running_balance.py](running_balance.py) |
| Cookies, boats, two cities, tokens, perimeter | [sort_assign.py](sort_assign.py) |
| Most parts, balanced split, hand of straights | [partitioning.py](partitioning.py) |
| Candy, unique frequencies, queue by height | [two_pass.py](two_pass.py) |
| Largest number, `*` brackets, min additions | [string_greedy.py](string_greedy.py) |
| Deadlines, refuelling, bricks/ladders (heap regret) | [heap_regret.py](heap_regret.py) |

**Conventions:** impossible is `-1`; brute force on small random inputs with fixed seeds; intervals in `intervals/`, remove-k-digits and meeting rooms in `stacks_heaps/`.
