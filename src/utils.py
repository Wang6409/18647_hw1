from __future__ import annotations

import random
from math import log2


def random_number(length: int, rng: random.Random) -> str:
    if length < 1:
        raise ValueError("length must be positive")
    return str(rng.randrange(1, 10)) + "".join(
        str(rng.randrange(10)) for _ in range(length - 1)
    )


def str_to_coeffs(value: str, k: int = 4) -> list[int]:
    if k < 1 or not value or any(char < "0" or char > "9" for char in value):
        raise ValueError("value must contain decimal digits and k must be positive")
    value = value.lstrip("0") or "0"
    return [
        int(value[max(0, end - k) : end])
        for end in range(len(value), 0, -k)
    ]


def coeffs_to_str(coeffs: list[int], k: int = 4) -> str:
    if k < 1:
        raise ValueError("k must be positive")
    base = 10**k
    values = list(coeffs) or [0]
    for index in range(len(values) - 1):
        carry, values[index] = divmod(values[index], base)
        values[index + 1] += carry
    while values[-1] >= base:
        carry, values[-1] = divmod(values[-1], base)
        values.append(carry)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return str(values[-1]) + "".join(f"{value:0{k}d}" for value in reversed(values[:-1]))


def operation_count(algorithm: str, n: int) -> float:
    if n < 1:
        raise ValueError("n must be positive")
    if algorithm == "quadratic":
        return float(n * n)
    if algorithm == "fft":
        return 5.0 * n * log2(n) if n > 1 else 0.0
    raise ValueError(f"unknown algorithm: {algorithm}")

