"""Deque-based random number generator.

Same LFSR semantics as the other two implementations. A collections.deque
makes the shift itself cheap -- appendleft() and pop() are both O(1) at the
ends -- but it flips the list's tradeoff: indexing the middle to read a tap
(deque[i]) walks the linked blocks, so tap reads are O(n).

Fast for the shift, slow for the taps -- the opposite of the plain list.
"""

from collections import deque


class RandomNumberGenerator:
    def __init__(self, config: list[int], state: list[str]):
        self.config = config
        self.state = deque(state)

    def next(self) -> str:
        value = 0
        for i in self.config:
            value ^= ord(self.state[i])  # O(n): deque indexing walks to i
        value = chr(value)

        self.state.appendleft(value)  # O(1)
        return self.state.pop()       # O(1): symbol shifted off the back
