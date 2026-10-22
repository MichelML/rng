"""Equivalence and correctness tests for all three RNG implementations.

Every test runs a naive oracle and all three implementations in lockstep and
asserts they agree on every single call, so correctness and cross-implementation
equivalence are checked together.

Run with:  python test_rng.py
"""

from list_rng import RandomNumberGenerator as ListRNG
from ring_buffer_rng import RandomNumberGenerator as RingRNG
from deque_rng import RandomNumberGenerator as DequeRNG

IMPLEMENTATIONS = [("list", ListRNG), ("ring", RingRNG), ("deque", DequeRNG)]


def reference_next(config, state):
    """A deliberately naive, obviously-correct next() used as the oracle.

    Mutates `state` in place and returns the popped symbol.
    """
    value = 0
    for i in config:
        value ^= ord(state[i])
    state.insert(0, chr(value))
    return state.pop()


def run_in_lockstep(config, state, steps):
    """Step the oracle and all three implementations `steps` times.

    Asserts that on every call all three implementations return exactly what the
    oracle returns. Returns the full output stream.
    """
    ref_state = list(state)
    instances = [(name, cls(config, state)) for name, cls in IMPLEMENTATIONS]
    stream = []
    for step in range(steps):
        expected = reference_next(config, ref_state)
        for name, rng in instances:
            got = rng.next()
            assert got == expected, (
                f"{name} diverged at step {step} with config={config}: "
                f"got {got!r}, expected {expected!r}"
            )
        stream.append(expected)
    return stream


# --- Base case from the challenge ------------------------------------------

def test_base_case_construction():
    for _, cls in IMPLEMENTATIONS:
        assert cls([2, 3], ["a", "b", "c", "d", "e", "f", "g"])


def test_base_case_stream():
    run_in_lockstep([2, 3], ["a", "b", "c", "d", "e", "f", "g"], steps=50)


# --- Real-world cases ------------------------------------------------------

def test_many_configs_short_run():
    """A spread of realistic tap configurations."""
    configs = [[2, 3], [0], [0, 1, 2], [6, 0], [1, 3, 5, 6], [0, 6], [3, 3, 3]]
    for config in configs:
        run_in_lockstep(config, ["a", "b", "c", "d", "e", "f", "g"], steps=100)


def test_long_run_100k_same_instance():
    """100,000 next() calls on the same instances; all must stay in agreement."""
    run_in_lockstep([2, 3], ["a", "b", "c", "d", "e", "f", "g"], steps=100_000)


def test_larger_state_long_run():
    """A bigger state over many calls, taps spread across its length."""
    state = [chr(ord("a") + (i % 26)) for i in range(256)]
    run_in_lockstep([0, 50, 128, 255], state, steps=10_000)


def test_determinism_same_inputs_same_stream():
    """Same config + state produce identical streams from fresh instances."""
    config, state = [2, 3], ["a", "b", "c", "d", "e", "f", "g"]
    first = run_in_lockstep(config, state, steps=500)
    second = run_in_lockstep(config, state, steps=500)
    assert first == second


def test_does_not_mutate_caller_state():
    """Constructing an RNG must copy the state, not alias the caller's list."""
    state = ["a", "b", "c", "d", "e", "f", "g"]
    original = list(state)
    for _, cls in IMPLEMENTATIONS:
        cls([2, 3], state).next()
    assert state == original, state


# --- Edge cases ------------------------------------------------------------

def test_single_element_state():
    """n == 1: the one symbol is both the tap and what gets shifted out."""
    run_in_lockstep([0], ["a"], steps=1_000)


def test_single_tap():
    """One tap: new value is just a copy of that symbol (x ^ nothing)."""
    run_in_lockstep([3], ["a", "b", "c", "d", "e"], steps=1_000)


def test_empty_config():
    """No taps: fold over nothing is 0, so every new symbol is chr(0)."""
    run_in_lockstep([], ["a", "b", "c", "d", "e"], steps=1_000)


def test_repeated_tap_cancels():
    """A tap repeated an even number of times XORs to 0 (x ^ x == 0)."""
    stream = run_in_lockstep([2, 2], ["a", "b", "c", "d", "e"], steps=50)
    assert stream  # agreement is asserted inside run_in_lockstep


def test_tap_at_last_index():
    run_in_lockstep([0, 6], ["a", "b", "c", "d", "e", "f", "g"], steps=1_000)


def test_duplicate_symbols_in_state():
    run_in_lockstep([0, 1, 2], ["x", "x", "x", "x", "x"], steps=1_000)


def test_unicode_symbols():
    """ord/chr round-trip works for multi-byte code points too."""
    run_in_lockstep([0, 2], ["α", "β", "γ", "€", "☃"], steps=1_000)


def test_high_codepoint_values():
    """XORing large code points stays a valid single character."""
    run_in_lockstep([0, 1], ["一", "￿", "A"], steps=1_000)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
