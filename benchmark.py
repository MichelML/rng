"""Benchmark both RNG implementations: compute time and peak memory.

Run with:  python benchmark.py

The gap widens with state size, because the list implementation pays O(n) per
call for the front insert while the ring buffer pays O(1).
"""

import time
import tracemalloc

from random_number_generator import RandomNumberGenerator as ListRNG
from ring_buffer_rng import RandomNumberGenerator as RingRNG
from deque_rng import RandomNumberGenerator as DequeRNG


def make_state(n: int) -> list[str]:
    return [chr(ord("a") + (i % 26)) for i in range(n)]


def time_calls(rng_cls, config, state, calls: int) -> float:
    rng = rng_cls(config, state)
    start = time.perf_counter()
    for _ in range(calls):
        rng.next()
    return time.perf_counter() - start


def peak_memory(rng_cls, config, state, calls: int) -> int:
    tracemalloc.start()
    rng = rng_cls(config, state)
    for _ in range(calls):
        rng.next()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def main():
    calls = 200_000
    config = [2, 3]
    sizes = [10, 100, 1_000, 10_000, 50_000]

    print(f"{calls:,} next() calls, config={config}\n")
    header = f"{'state n':>10} | {'list (s)':>10} | {'ring (s)':>10} | {'deque (s)':>10}"
    print(header)
    print("-" * len(header))
    for n in sizes:
        state = make_state(n)
        t_list = time_calls(ListRNG, config, state, calls)
        t_ring = time_calls(RingRNG, config, state, calls)
        t_deque = time_calls(DequeRNG, config, state, calls)
        print(f"{n:>10,} | {t_list:>10.4f} | {t_ring:>10.4f} | {t_deque:>10.4f}")

    print()
    header = f"{'state n':>10} | {'list peak':>12} | {'ring peak':>12} | {'deque peak':>12}"
    print(header)
    print("-" * len(header))
    for n in sizes:
        state = make_state(n)
        m_list = peak_memory(ListRNG, config, state, 10_000)
        m_ring = peak_memory(RingRNG, config, state, 10_000)
        m_deque = peak_memory(DequeRNG, config, state, 10_000)
        print(f"{n:>10,} | {m_list:>10,} B | {m_ring:>10,} B | {m_deque:>10,} B")

    # Worst case: a single tap in the MIDDLE of the state. This is the deque's
    # worst case -- indexing has to walk ~n/2 nodes -- so it degrades toward the
    # list, while the ring buffer stays flat (its O(1) holds for any tap).
    print(f"\nworst case: config=[n // 2] (middle tap), {calls:,} next() calls\n")
    header = f"{'state n':>10} | {'list (s)':>10} | {'ring (s)':>10} | {'deque (s)':>10}"
    print(header)
    print("-" * len(header))
    for n in sizes:
        state = make_state(n)
        mid_config = [n // 2]
        t_list = time_calls(ListRNG, mid_config, state, calls)
        t_ring = time_calls(RingRNG, mid_config, state, calls)
        t_deque = time_calls(DequeRNG, mid_config, state, calls)
        print(f"{n:>10,} | {t_list:>10.4f} | {t_ring:>10.4f} | {t_deque:>10.4f}")


if __name__ == "__main__":
    main()
