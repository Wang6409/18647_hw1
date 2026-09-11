from __future__ import annotations

import numpy as np

from .utils import coeffs_to_str, str_to_coeffs


def _normalise(value: str) -> str:
    if not value or any(char < "0" or char > "9" for char in value):
        raise ValueError("inputs must be non-empty strings of decimal digits")
    return value.lstrip("0") or "0"


def multiply_quadratic(num1: str, num2: str) -> str:
    num1, num2 = _normalise(num1), _normalise(num2)
    if num1 == "0" or num2 == "0":
        return "0"
    result = [0] * (len(num1) + len(num2))
    for i, num1_digit in enumerate(reversed(num1)):
        for j, num2_digit in enumerate(reversed(num2)):
            result[i + j] += (ord(num1_digit) - 48) * (ord(num2_digit) - 48)
    for index in range(len(result) - 1):
        result[index + 1] += result[index] // 10
        result[index] %= 10
    while result[-1] >= 10:
        result.append(result[-1] // 10)
        result[-2] %= 10
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return "".join(str(digit) for digit in reversed(result))


def multiply_fft(num1: str, num2: str) -> str:
    num1, num2 = _normalise(num1), _normalise(num2)
    if num1 == "0" or num2 == "0":
        return "0"
    num1_coeffs, num2_coeffs = str_to_coeffs(num1), str_to_coeffs(num2)
    size = 1
    while size < len(num1_coeffs) + len(num2_coeffs) - 1:
        size <<= 1
    num1_fft = np.fft.rfft(np.pad(num1_coeffs, (0, size - len(num1_coeffs))))
    num2_fft = np.fft.rfft(np.pad(num2_coeffs, (0, size - len(num2_coeffs))))
    convolution = np.fft.irfft(num1_fft * num2_fft, n=size)
    return coeffs_to_str(
        [int(round(value)) for value in convolution[: len(num1_coeffs) + len(num2_coeffs) - 1]]
    )
