# Tries

One file per technique family: implementation + tests, checked against brute force. Explanations: [Tries — Field Guide](https://claude.ai/code/artifact/b43a5a21-403d-4104-8ee9-c6eec0e3e3b0).

```
python3 tries/basic_trie.py                                   # one file
for f in tries/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Insert / search / startsWith, counts, delete | [basic_trie.py](basic_trie.py) |
| Search with `.` wildcards | [wildcard_search.py](wildcard_search.py) |
| LCP, replace words, top-3 suggestions, map sum, prefix + suffix | [prefix_queries.py](prefix_queries.py) |
| Longest word one char at a time, concatenated words, word break | [word_building.py](word_building.py) |
| Does a word end at the latest stream char | [stream_matching.py](stream_matching.py) |
| Max XOR pair, max XOR under a limit | [bitwise_trie.py](bitwise_trie.py) |
| Concatenation is a palindrome | [palindrome_pairs.py](palindrome_pairs.py) |

**Conventions:** dict-of-dicts with `"$"` as the end marker unless counts are needed; word search II → [backtracking/grid_search.py](../backtracking/grid_search.py); hash-set word break → [dynamic_programming/string_segmentation.py](../dynamic_programming/string_segmentation.py).
