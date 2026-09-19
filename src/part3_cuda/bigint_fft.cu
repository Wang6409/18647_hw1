#include "bigint_fft.h"

#include "utils.h"

#include <cuda_runtime.h>
#include <cufft.h>

#include <cmath>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <vector>

namespace {
void check_cuda(cudaError_t status) {
    if (status != cudaSuccess) throw std::runtime_error(cudaGetErrorString(status));
}

void check_fft(cufftResult status) {
    if (status != CUFFT_SUCCESS) throw std::runtime_error("cuFFT operation failed");
}

std::size_t available_host_bytes() {
    std::ifstream memory_info("/proc/meminfo");
    std::string label;
    std::size_t kilobytes = 0;
    while (memory_info >> label >> kilobytes) {
        if (label == "MemAvailable:") return kilobytes * 1024;
        memory_info.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
    return 0;
}

__global__ void pointwise_multiply(const cufftDoubleComplex* left,
                                   const cufftDoubleComplex* right,
                                   cufftDoubleComplex* product, int size) {
    const int index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index < size) {
        product[index].x = left[index].x * right[index].x - left[index].y * right[index].y;
        product[index].y = left[index].x * right[index].y + left[index].y * right[index].x;
    }
}
}  // namespace

double gpu_multiply(const std::string& left, const std::string& right,
                    std::string& product) {
    const auto left_digits = string_to_digits(left);
    const auto right_digits = string_to_digits(right);
    int size = 1;
    while (size < static_cast<int>(left_digits.size() + right_digits.size() - 1)) size <<= 1;

    std::size_t free_bytes = 0;
    std::size_t total_bytes = 0;
    check_cuda(cudaMemGetInfo(&free_bytes, &total_bytes));
    const std::size_t complex_bytes = sizeof(cufftDoubleComplex) * static_cast<std::size_t>(size);
    const std::size_t allocation_bytes = 3 * complex_bytes;
    // Leave room for cuFFT's internal workspace and the Colab runtime.
    if (allocation_bytes > free_bytes * 3 / 5) {
        throw std::runtime_error("insufficient GPU memory for next problem size");
    }
    const std::size_t available_host = available_host_bytes();
    if (available_host != 0 && allocation_bytes > available_host / 2) {
        throw std::runtime_error("insufficient host memory for next problem size");
    }

    std::vector<cufftDoubleComplex> host_left(size), host_right(size), host_product(size);
    for (std::size_t i = 0; i < left_digits.size(); ++i) host_left[i] = {left_digits[i], 0.0};
    for (std::size_t i = 0; i < right_digits.size(); ++i) host_right[i] = {right_digits[i], 0.0};

    cufftDoubleComplex *device_left = nullptr, *device_right = nullptr, *device_product = nullptr;
    check_cuda(cudaMalloc(reinterpret_cast<void**>(&device_left),
                          sizeof(cufftDoubleComplex) * size));
    check_cuda(cudaMalloc(reinterpret_cast<void**>(&device_right),
                          sizeof(cufftDoubleComplex) * size));
    check_cuda(cudaMalloc(reinterpret_cast<void**>(&device_product),
                          sizeof(cufftDoubleComplex) * size));
    cufftHandle plan;
    check_fft(cufftPlan1d(&plan, size, CUFFT_Z2Z, 1));
    cudaEvent_t start, stop;
    check_cuda(cudaEventCreate(&start));
    check_cuda(cudaEventCreate(&stop));

    check_cuda(cudaMemcpy(device_left, host_left.data(), sizeof(cufftDoubleComplex) * size,
                          cudaMemcpyHostToDevice));
    check_cuda(cudaMemcpy(device_right, host_right.data(), sizeof(cufftDoubleComplex) * size,
                          cudaMemcpyHostToDevice));
    check_cuda(cudaEventRecord(start));
    check_fft(cufftExecZ2Z(plan, device_left, device_left, CUFFT_FORWARD));
    check_fft(cufftExecZ2Z(plan, device_right, device_right, CUFFT_FORWARD));
    pointwise_multiply<<<(size + 255) / 256, 256>>>(device_left, device_right, device_product, size);
    check_cuda(cudaGetLastError());
    check_fft(cufftExecZ2Z(plan, device_product, device_product, CUFFT_INVERSE));
    check_cuda(cudaEventRecord(stop));
    check_cuda(cudaEventSynchronize(stop));

    check_cuda(cudaMemcpy(host_product.data(), device_product,
                          sizeof(cufftDoubleComplex) * size, cudaMemcpyDeviceToHost));
    std::vector<long long> coefficients(left_digits.size() + right_digits.size() - 1);
    for (std::size_t i = 0; i < coefficients.size(); ++i) {
        coefficients[i] = static_cast<long long>(
            std::llround(host_product[i].x / static_cast<double>(size)));
    }
    product = digits_to_string(coefficients);
    float elapsed_ms = 0.0f;
    check_cuda(cudaEventElapsedTime(&elapsed_ms, start, stop));

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    cufftDestroy(plan);
    cudaFree(device_left);
    cudaFree(device_right);
    cudaFree(device_product);
    return elapsed_ms;
}
