from __future__ import annotations

import random

from .multiplication import multiply_fft, multiply_quadratic
from .utils import random_number


def main() -> None:
    rng = random.Random(18647)
    for length in [1, 2, 3, 8, 31, 64, 127, 256, 1024]:
        for _ in range(5):
            left, right = random_number(length, rng), random_number(length, rng)
            expected = multiply_quadratic(left, right)
            assert multiply_fft(left, right) == expected
    print("all correctness checks passed")


if __name__ == "__main__":
    main()

