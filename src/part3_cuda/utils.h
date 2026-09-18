#pragma once

#include <string>
#include <vector>

std::vector<double> string_to_digits(const std::string& value);
std::string digits_to_string(const std::vector<long long>& coefficients);
std::string random_number(std::size_t length, unsigned int& state);
