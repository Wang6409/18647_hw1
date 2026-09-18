from __future__ import annotations

import random

from .multiplication import multiply_fft, multiply_n2
from .utils import random_number


def main() -> None:
    rng = random.Random(18647)
    for length in [1, 2, 3, 8, 31, 64, 127, 256, 1024]:
        for _ in range(5):
            num1, num2 = random_number(length, rng), random_number(length, rng)
            expected = multiply_n2(num1, num2)
            # if length < 30:
            #     print([num1, "*", num2, "=", expected])
            assert multiply_fft(num1, num2) == expected
    print("all correctness checks passed")


if __name__ == "__main__":
    main()
