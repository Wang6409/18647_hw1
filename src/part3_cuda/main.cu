#include "bigint_fft.h"
#include "utils.h"

#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
std::string multiply_n2(const std::string& left, const std::string& right) {
    std::vector<long long> digits(left.size() + right.size());
    for (std::size_t i = 0; i < left.size(); ++i)
        for (std::size_t j = 0; j < right.size(); ++j)
            digits[i + j] += (left[left.size() - 1 - i] - '0') *
                             (right[right.size() - 1 - j] - '0');
    return digits_to_string(digits);
}
}

int main(int argc, char** argv) {
    std::size_t max_length = 0;
    bool has_max_length = false;
    std::string output = "runs/gpu_results.csv";
    for (int i = 1; i < argc; ++i) {
        std::string argument = argv[i];
        if (argument == "--help") {
            std::cout << "Usage: fft_multiply [--max-length N] [--output FILE]\n"
                         "Omit --max-length for the ten-minute automatic experiment.\n";
            return 0;
        }
        if (argument == "--max-length") {
            if (i + 1 >= argc) throw std::invalid_argument("--max-length needs a value");
            max_length = std::stoul(argv[++i]);
            has_max_length = true;
        }
        else if (argument == "--output") {
            if (i + 1 >= argc) throw std::invalid_argument("--output needs a path");
            output = argv[++i];
        }
        else throw std::invalid_argument("unknown argument: " + argument);
    }
    std::ofstream log(output);
    if (!log) throw std::runtime_error("cannot open output file");
    log << "n,gpu_time_ms,total_ms,status\n";
    unsigned int seed = 18647;
    const auto experiment_start = std::chrono::steady_clock::now();
    for (std::size_t n = 1; !has_max_length || n <= max_length; n *= 2) {
        const auto left = random_number(n, seed);
        const auto right = random_number(n, seed);
        const auto start = std::chrono::steady_clock::now();
        std::string product;
        try {
            const double gpu_ms = gpu_multiply(left, right, product);
            const auto stop = std::chrono::steady_clock::now();
            const double total_ms = std::chrono::duration<double, std::milli>(stop - start).count();
            const bool valid = n > 2048 || product == multiply_n2(left, right);
            const double experiment_ms =
                std::chrono::duration<double, std::milli>(
                    stop - experiment_start).count();
            const bool timed_out = experiment_ms >= 600000.0;
            const char* status = !valid ? "incorrect" : (timed_out ? "timeout" : "success");
            log << n << ',' << gpu_ms << ',' << total_ms << ',' << status << '\n';
            std::cout << n << ',' << gpu_ms << ',' << total_ms << '\n';
            if (!valid || timed_out) break;
        } catch (const std::exception& error) {
            const std::string reason = error.what();
            const char* status = reason.find("memory") != std::string::npos
                                     ? "oom"
                                     : "error";
            log << n << ",,," << status << ':' << reason << '\n';
            std::cerr << "stopping at n=" << n << ": " << reason << '\n';
            break;
        }
        if (n > static_cast<std::size_t>(-1) / 2) break;
    }
}
