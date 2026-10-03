# Matrix & Simulation

One file per technique family: implementation + tests, checked against a naive copy or step-by-step simulation.

```
python3 matrix_simulation/spiral.py                                          # one file
for f in matrix_simulation/*.py; do python3 "$f" >/dev/null && echo "ok $f"; done   # all
```

| Situation | File |
|---|---|
| Direction arrays, turning, flatten `r*C+c`, reshape, shift, padding | [grid_idioms.py](grid_idioms.py) |
| Spiral order, fill a spiral, walk outward from a cell | [spiral.py](spiral.py) |
| Group by `r+c` / `r-c`, zigzag, sort diagonals, Toeplitz, diagonal sum | [diagonals.py](diagonals.py) |
| Rotate 90° in place, flip, transpose, k quarter turns | [rotate_flip.py](rotate_flip.py) |
| O(1)-space set zeroes, Game of Life in place | [in_place_marking.py](in_place_marking.py) |
| Stones fall, Candy Crush, 2048 moves | [gravity.py](gravity.py) |
| Valid Sudoku, tic-tac-toe winner / O(1) moves, lucky numbers | [validation.py](validation.py) |
| Robot instructions, obstacles, bounded-in-circle, snake | [robot_simulation.py](robot_simulation.py) |

**Conventions:** grids are lists of lists, `R` rows × `C` columns, `(r, c)` 0-based with `r` down; `DIRS4` is clockwise from east, so turn right is `(d + 1) % 4`; robot problems use `(x, y)` with north `+y`. Related: grid BFS/DFS in [graphs/](../graphs/README.md), sorted-matrix search in [matrix_search.py](../binary_search/matrix_search.py), rectangle sums in [prefix_2d.py](../prefix_sums/prefix_2d.py), path DP in [grid_dp.py](../dynamic_programming/grid_dp.py), N-Queens and Sudoku solving in [backtracking/](../backtracking/README.md).
