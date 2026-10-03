"""Mini systems — Twitter feed, browser history, in-memory file system, tic-tac-toe.

Signs: "design Twitter", "back/forward n steps", "mkdir / ls / addContent",
       "n x n board, report the winner after each move". Several entities and
       several operations; the interviewer is grading the data model.
Approach:
  - Twitter: user -> list of (time, tweet) appended in time order; user -> set
    of followees. Feed = k-way merge (stacks_heaps/k_way_merge.py): seed a
    heap with each relevant user's newest tweet, pop 10, pushing that user's
    next-older tweet after each pop.
  - Browser history: one list + `cur` + `last`. visit writes at cur + 1 and
    sets last = cur, which discards forward history without deleting it.
    back / forward clamp the pointer.
  - File system: a tree of dict nodes, one per path component (a trie on path
    parts — see tries/basic_trie.py). A node with `content` set is a file.
  - Tic-tac-toe: never scan the board. Keep rows[n], cols[n], diag, anti;
    player 1 adds +1, player 2 adds -1. |sum| == n means that line is full of
    one player.
Complexity: Twitter post/follow O(1), feed O(f + 10 log f) for f followees.
            Browser O(1) per op. File system O(path length), ls adds a sort.
            Tic-tac-toe O(1) per move, O(n) space instead of O(n^2).
Gotchas:
  - Twitter: a user always sees their own tweets; following yourself or
    unfollowing yourself must not change that. Use a global clock, not tweet
    ids, for order.
  - Browser: visit must reset `last`; truncating with slicing is O(n).
  - File system: ls on a FILE path returns [file name]; ls on a dir returns
    sorted child names. Creating a file creates missing parent dirs.
  - Tic-tac-toe: the anti-diagonal is r + c == n - 1; a cell can be on both.

Run the tests at the bottom with:  python3 design/mini_systems.py
"""

import heapq
from collections import defaultdict


# ---------------------------------------------------------------- implementation


class Twitter:
    """LC 355. Feed = 10 most recent tweets from the user and followees."""

    FEED = 10

    def __init__(self):
        self.clock = 0
        self.tweets = defaultdict(list)  # user -> [(time, tweet id)], oldest first
        self.follows = defaultdict(set)

    def post_tweet(self, user, tweet_id):
        self.clock += 1
        self.tweets[user].append((self.clock, tweet_id))

    def follow(self, follower, followee):
        if follower != followee:
            self.follows[follower].add(followee)

    def unfollow(self, follower, followee):
        self.follows[follower].discard(followee)

    def get_news_feed(self, user):
        heap = []
        for u in self.follows[user] | {user}:
            if self.tweets[u]:
                i = len(self.tweets[u]) - 1
                t, tid = self.tweets[u][i]
                heap.append((-t, tid, u, i))
        heapq.heapify(heap)
        feed = []
        while heap and len(feed) < self.FEED:
            _, tid, u, i = heapq.heappop(heap)
            feed.append(tid)
            if i:
                t, nxt = self.tweets[u][i - 1]
                heapq.heappush(heap, (-t, nxt, u, i - 1))
        return feed


class BrowserHistory:
    """LC 1472."""

    def __init__(self, homepage):
        self.hist = [homepage]
        self.cur = self.last = 0

    def visit(self, url):
        self.cur += 1
        if self.cur == len(self.hist):
            self.hist.append(url)
        else:
            self.hist[self.cur] = url  # overwrite: forward history is gone
        self.last = self.cur

    def back(self, steps):
        self.cur = max(0, self.cur - steps)
        return self.hist[self.cur]

    def forward(self, steps):
        self.cur = min(self.last, self.cur + steps)
        return self.hist[self.cur]


class FileSystem:
    """LC 588. Absolute paths like "/a/b/c"."""

    def __init__(self):
        self.root = {"kids": {}, "content": None}

    def _walk(self, path, create=False):
        node = self.root
        for part in filter(None, path.split("/")):
            if part not in node["kids"]:
                if not create:
                    return None
                node["kids"][part] = {"kids": {}, "content": None}
            node = node["kids"][part]
        return node

    def ls(self, path):
        node = self._walk(path)
        if node["content"] is not None:
            return [path.rsplit("/", 1)[-1]]
        return sorted(node["kids"])

    def mkdir(self, path):
        self._walk(path, create=True)

    def add_content_to_file(self, path, content):
        node = self._walk(path, create=True)
        node["content"] = (node["content"] or "") + content

    def read_content_from_file(self, path):
        return self._walk(path)["content"]


class TicTacToe:
    """LC 348. move returns the winner (1 or 2) or 0."""

    def __init__(self, n):
        self.n = n
        self.rows, self.cols = [0] * n, [0] * n
        self.diag = self.anti = 0

    def move(self, r, c, player):
        d = 1 if player == 1 else -1
        self.rows[r] += d
        self.cols[c] += d
        if r == c:
            self.diag += d
        if r + c == self.n - 1:
            self.anti += d
        n = self.n
        if n in (abs(self.rows[r]), abs(self.cols[c]), abs(self.diag), abs(self.anti)):
            return player
        return 0


# ------------------------------------------------------------------------ tests


def test_twitter_example():
    tw = Twitter()
    tw.post_tweet(1, 5)
    assert tw.get_news_feed(1) == [5]
    tw.follow(1, 2)
    tw.post_tweet(2, 6)
    assert tw.get_news_feed(1) == [6, 5]
    tw.unfollow(1, 2)
    assert tw.get_news_feed(1) == [5]


def test_twitter_matches_global_log_scan():
    import random

    rng = random.Random(1)
    tw, log, follows, tid = Twitter(), [], defaultdict(set), 0
    for _ in range(6000):
        u, v = rng.randrange(6), rng.randrange(6)
        r = rng.random()
        if r < 0.4:
            tid += 1
            tw.post_tweet(u, tid)
            log.append((u, tid))
        elif r < 0.55:
            tw.follow(u, v)
            follows[u].add(v)
        elif r < 0.7:
            tw.unfollow(u, v)
            follows[u].discard(v)
        else:
            seen = follows[u] | {u}
            expect = [t for w, t in reversed(log) if w in seen][:10]
            assert tw.get_news_feed(u) == expect


def test_twitter_feed_cost_ignores_history_size():
    import time

    tw = Twitter()
    for i in range(200_000):
        tw.post_tweet(i % 50, i)
    for v in range(50):
        tw.follow(0, v)
    t0 = time.perf_counter()
    for _ in range(2000):  # scanning 200k tweets each time: 4e8 steps
        feed = tw.get_news_feed(0)
    assert feed == list(range(199_999, 199_989, -1))
    assert time.perf_counter() - t0 < 2.0


def test_browser_example():
    b = BrowserHistory("leetcode.com")
    for url in ("google.com", "facebook.com", "youtube.com"):
        b.visit(url)
    assert b.back(1) == "facebook.com" and b.back(1) == "google.com"
    assert b.forward(1) == "facebook.com"
    b.visit("linkedin.com")
    assert b.forward(2) == "linkedin.com"
    assert b.back(2) == "google.com" and b.back(7) == "leetcode.com"


def test_browser_matches_two_stacks():
    import random

    rng = random.Random(2)
    b, back, fwd, cur = BrowserHistory("h"), [], [], "h"
    for i in range(5000):
        r = rng.random()
        if r < 0.4:
            b.visit(str(i))
            back.append(cur)
            cur, fwd = str(i), []
        elif r < 0.7:
            k = rng.randint(1, 4)
            for _ in range(min(k, len(back))):
                fwd.append(cur)
                cur = back.pop()
            assert b.back(k) == cur
        else:
            k = rng.randint(1, 4)
            for _ in range(min(k, len(fwd))):
                back.append(cur)
                cur = fwd.pop()
            assert b.forward(k) == cur


def test_file_system_example():
    fs = FileSystem()
    assert fs.ls("/") == []
    fs.mkdir("/a/b/c")
    fs.add_content_to_file("/a/b/c/d", "hello")
    assert fs.ls("/") == ["a"] and fs.ls("/a/b/c") == ["d"]
    assert fs.ls("/a/b/c/d") == ["d"]
    fs.add_content_to_file("/a/b/c/d", " world")
    assert fs.read_content_from_file("/a/b/c/d") == "hello world"


def test_file_system_matches_flat_dict():
    import random

    rng = random.Random(3)
    fs, files, dirs = FileSystem(), {}, {"/"}

    def parents(p):
        parts = p.strip("/").split("/")
        return {"/" + "/".join(parts[:i]) for i in range(1, len(parts))}

    for _ in range(3000):
        depth = rng.randint(1, 3)
        path = "/" + "/".join(rng.choice("abc") for _ in range(depth))
        if any(q in files for q in parents(path) | {path}) and path not in files:
            continue  # would nest under a file: invalid input for LC 588
        r = rng.random()
        if r < 0.3 and path not in files:
            fs.mkdir(path)
            dirs |= parents(path) | {path}
        elif r < 0.6 and path not in dirs:
            s = rng.choice("xyz")
            fs.add_content_to_file(path, s)
            files[path] = files.get(path, "") + s
            dirs |= parents(path)
        elif path in files:
            assert fs.read_content_from_file(path) == files[path]
            assert fs.ls(path) == [path.rsplit("/", 1)[-1]]
        q = rng.choice(sorted(dirs))
        prefix = q.rstrip("/") + "/"
        kids = {p[len(prefix):].split("/")[0] for p in dirs | set(files) if p.startswith(prefix) and p != prefix}
        assert fs.ls(q) == sorted(kids)


def _naive_winner(board, n):
    lines = [[(r, c) for c in range(n)] for r in range(n)]
    lines += [[(r, c) for r in range(n)] for c in range(n)]
    lines += [[(i, i) for i in range(n)], [(i, n - 1 - i) for i in range(n)]]
    for line in lines:
        vals = {board[r][c] for r, c in line}
        if len(vals) == 1 and 0 not in vals:
            return vals.pop()
    return 0


def test_tic_tac_toe_example():
    t = TicTacToe(3)
    moves = [(0, 0, 1), (0, 2, 2), (2, 2, 1), (1, 1, 2), (2, 0, 1), (1, 0, 2), (2, 1, 1)]
    assert [t.move(*m) for m in moves] == [0, 0, 0, 0, 0, 0, 1]


def test_tic_tac_toe_matches_board_scan():
    import random

    rng = random.Random(4)
    for _ in range(1500):
        n = rng.randint(1, 5)
        t, board = TicTacToe(n), [[0] * n for _ in range(n)]
        cells = [(r, c) for r in range(n) for c in range(n)]
        rng.shuffle(cells)
        for i, (r, c) in enumerate(cells):
            p = 1 + i % 2
            board[r][c] = p
            got = t.move(r, c, p)
            assert got == _naive_winner(board, n)
            if got:
                break


def test_tic_tac_toe_move_is_constant_time():
    import time

    n = 3000
    t = TicTacToe(n)
    t0 = time.perf_counter()
    for i in range(100_000):  # a board scan per move: 1.2e9 steps
        assert t.move(i % n, i // n, 1 + i % 2) == 0  # distinct cells, no full line
    assert time.perf_counter() - t0 < 2.0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"\n{len(tests)} passed")
