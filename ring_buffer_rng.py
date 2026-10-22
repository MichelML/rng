"""Ring-buffer random number generator (the O(1) reading of the challenge).

Same LFSR semantics as list_rng.py, but it exploits the fact
that the state never changes length: every call pushes one symbol onto the
front and pops one off the back, so there are always exactly n symbols.

Instead of moving elements, we keep a fixed-size array plus a `head` pointer.
Logical index i lives at buf[(head + i) % n], so tap reads, the front push,
and the back pop are all O(1) with no shifting.
"""


class RandomNumberGenerator:
    def __init__(self, config: list[int], state: list[str]):
        self.config = config
        self.buf = list(state)
        self.n = len(state)
        self.head = 0  # logical index 0 lives at buf[head]

    def next(self) -> str:
        value = 0
        for i in self.config:
            value ^= ord(self.buf[(self.head + i) % self.n])
        value = chr(value)

        # Pushing onto the front means moving head back one slot; the slot it
        # lands on is the current tail, so that symbol is the one popped off.
        self.head = (self.head - 1) % self.n
        popped = self.buf[self.head]
        self.buf[self.head] = value
        return popped
