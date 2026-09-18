#include "utils.h"

#include <algorithm>
#include <stdexcept>

std::vector<double> string_to_digits(const std::string& value) {
    if (value.empty() ||
        !std::all_of(value.begin(), value.end(), [](char c) { return c >= '0' && c <= '9'; })) {
        throw std::invalid_argument("integer strings must contain decimal digits");
    }
    std::vector<double> digits;
    digits.reserve(value.size());
    for (auto it = value.rbegin(); it != value.rend(); ++it) {
        digits.push_back(static_cast<double>(*it - '0'));
    }
    return digits;
}

std::string digits_to_string(const std::vector<long long>& coefficients) {
    std::vector<long long> digits = coefficients;
    if (digits.empty()) return "0";
    for (std::size_t i = 0; i + 1 < digits.size(); ++i) {
        if (digits[i] < 0) throw std::runtime_error("negative FFT coefficient");
        digits[i + 1] += digits[i] / 10;
        digits[i] %= 10;
    }
    while (digits.back() >= 10) {
        const long long carry = digits.back() / 10;
        digits.back() %= 10;
        digits.push_back(carry);
    }
    while (digits.size() > 1 && digits.back() == 0) digits.pop_back();
    std::string result;
    result.reserve(digits.size());
    for (auto it = digits.rbegin(); it != digits.rend(); ++it) {
        result.push_back(static_cast<char>('0' + *it));
    }
    return result;
}

std::string random_number(std::size_t length, unsigned int& state) {
    if (length == 0) throw std::invalid_argument("length must be positive");
    auto next_digit = [&state](unsigned int bound) {
        state = 1664525u * state + 1013904223u;
        return state % bound;
    };
    std::string result(1, static_cast<char>('1' + next_digit(9)));
    for (std::size_t i = 1; i < length; ++i) {
        result.push_back(static_cast<char>('0' + next_digit(10)));
    }
    return result;
}
