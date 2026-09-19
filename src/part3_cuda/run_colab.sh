#!/usr/bin/env bash
set -euo pipefail

PART3_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${PART3_DIR}/../.." && pwd)"
OUTPUT="${ROOT_DIR}/runs/gpu_results.csv"
LOG="${ROOT_DIR}/runs/part3_colab.log"
ENVIRONMENT="${ROOT_DIR}/runs/part3_environment.txt"

mkdir -p "${ROOT_DIR}/runs" "${ROOT_DIR}/plots"
exec > >(tee "${LOG}") 2>&1

command -v nvidia-smi >/dev/null || {
  echo "No NVIDIA GPU is attached. In Colab select Runtime > Change runtime type > T4 GPU." >&2
  exit 1
}
command -v nvcc >/dev/null || {
  echo "nvcc is unavailable in this Colab runtime." >&2
  exit 1
}

nvidia-smi
{
  echo "=== GPU ==="
  nvidia-smi
  echo "=== CUDA compiler ==="
  nvcc --version
  echo "=== CPU ==="
  lscpu
} > "${ENVIRONMENT}" 2>&1

make -C "${PART3_DIR}"
"${PART3_DIR}/fft_multiply" --output "${OUTPUT}"
python3 "${PART3_DIR}/plot_results.py" \
  --input "${OUTPUT}" \
  --table "${ROOT_DIR}/runs/gpu_fft_table.csv" \
  --plot "${ROOT_DIR}/plots/gpu_fft_mops.pdf" \
  --time total

echo "Part 3 outputs:"
echo "  ${OUTPUT}"
echo "  ${ROOT_DIR}/runs/gpu_fft_table.csv"
echo "  ${ROOT_DIR}/plots/gpu_fft_mops.pdf"
echo "  ${LOG}"
echo "  ${ENVIRONMENT}"
