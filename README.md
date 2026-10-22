# Random Number Generator — three implementations

Three implementations of the same LFSR-style generator — a plain list, a
`collections.deque`, and a fixed-size ring buffer — with a shared test suite and
benchmarks. The deque is fastest for the challenge's small, front-tap case, but
the **ring buffer is the recommended default**: it is the only one whose O(1)
cost holds regardless of state size or where the taps land, with similar memory
consumption (see benchmark results).

> Built with [Claude Code](https://claude.com/claude-code). The full working
> conversation that produced these implementations is in
> [conversation.pdf](conversation.pdf).

## Getting started

No third-party dependencies — just the Python standard library (Python 3.9+ for
the `list[int]` type hints; developed on 3.13).

```bash
# optional: an isolated environment with uv
uv venv --python 3.13
source .venv/bin/activate
```

Run the suite and benchmarks:

```bash
python test_rng.py    # run the equivalence + edge-case test suite
python benchmark.py   # run the time + memory benchmarks
```

`test_rng.py` prints one line per test and a final count; `benchmark.py` prints
the normal-case, memory, and worst-case tables.

## Overview

An LFSR-style (linear-feedback shift register) generator. Each `next()` call
XORs the symbols at the configured tap indices into a new symbol
(`chr(ord(a) ^ ord(b) ^ ...)`), pushes it onto the front of the state, and
returns the symbol shifted off the back. The state never changes length, which
is the key fact the fastest implementation exploits.

## The three approaches

**List** ([random_number_generator.py](random_number_generator.py)) — the
straightforward reading. The state is a plain `list`; tap reads are O(1) by
index, but pushing onto the front with `list.insert(0, …)` shifts every element
over by one, making each `next()` call O(n). Dead simple and perfectly fine for
small states, but it scales badly: the cost grows linearly with state size.

**Deque** ([deque_rng.py](deque_rng.py)) — a `collections.deque` flips the
list's tradeoff. `appendleft()` and `pop()` are both O(1) at the ends, so the
shift itself is cheap; but indexing the middle (`deque[i]`) walks the internal
blocks, so a tap read is O(distance from the nearest end). It's the fastest of
the three *when taps sit near an end* (as in the base case, `config=[2,3]`), and
degrades toward the list when taps are deep in a large state.

**Ring buffer** ([ring_buffer_rng.py](ring_buffer_rng.py)) — the O(1) approach.
Because the state length is fixed, nothing needs to move: keep the symbols in a
fixed array plus a `head` pointer, where logical index `i` lives at
`buf[(head + i) % n]`. A front push is just moving `head` back one slot, and the
slot it lands on holds the old tail (the symbol popped off). Tap reads, push,
and pop are all O(1) regardless of state size *or* tap position.

## Benchmarks

200,000 `next()` calls. Times in seconds; peak memory in bytes.

**Normal case — `config=[2, 3]` (taps near the front):**

| state n | list (s) | ring (s) | deque (s) | list peak | ring peak | deque peak |
|--------:|---------:|---------:|----------:|----------:|----------:|-----------:|
| 10      | 0.022    | 0.030    | 0.021     | 592 B     | 544 B     | 1,696 B    |
| 100     | 0.026    | 0.030    | 0.022     | 1,376 B   | 1,248 B   | 2,208 B    |
| 1,000   | 0.079    | 0.034    | 0.022     | 9,496 B   | 8,564 B   | 9,592 B    |
| 10,000  | 0.595    | 0.035    | 0.022     | 90,480 B  | 80,556 B  | 84,032 B   |
| 50,000  | 2.959    | 0.035    | 0.023     | 450,472 B | 400,548 B | 414,024 B  |

**Worst case — `config=[n // 2]` (one tap in the middle):**

| state n | list (s) | ring (s) | deque (s) |
|--------:|---------:|---------:|----------:|
| 10      | 0.018    | 0.024    | 0.018     |
| 100     | 0.023    | 0.024    | 0.018     |
| 1,000   | 0.079    | 0.028    | 0.019     |
| 10,000  | 0.601    | 0.029    | 0.032     |
| 50,000  | 2.958    | 0.029    | 0.379     |

## Deque and ring are both strong — why ring wins

In the normal case the deque is the fastest implementation at every size, and
its memory sits between the other two. If the taps are guaranteed to stay near
an end of the state, it is the best practical choice — including the challenge's
own 7-element base case.

But the deque's speed is a property of *where the taps are*, not just how big
the state is. The worst-case table shows this: with a single middle tap, the
deque degrades toward O(n) and at n=50,000 it is ~13x slower than the ring
buffer (0.379s vs 0.029s), because each tap read walks ~25,000 nodes. The list
is O(n) in every case.

The ring buffer is the only implementation whose cost is flat — ~0.03s per
200k calls at every size, in both the normal and worst cases, because its O(1)
holds no matter where the taps land. It also uses the least memory. You give up
a little in the small/front-tap case, but you buy a guarantee: performance that
never depends on the config or the state size. For a reusable generator where
the caller chooses the taps, **go with the ring buffer** — it is the safe
default that can't be made slow by an unlucky configuration.
