"""List-based random number generator (the straightforward reading of the challenge).

An LFSR-style generator: each call XORs the symbols at the configured tap
indices into a new symbol, shifts it onto the front of the state, and returns
the symbol shifted off the back.

The state is kept in a plain list, so `next()` is O(n): inserting at the front
shifts every element over by one.
"""


class RandomNumberGenerator:
    def __init__(self, config: list[int], state: list[str]):
        self.config = config
        self.state = list(state)

    def next(self) -> str:
        value = 0
        for i in self.config:
            value ^= ord(self.state[i])
        value = chr(value)

        self.state.insert(0, value)  # O(n): shifts every element
        return self.state.pop()      # pop the symbol shifted off the back
