# 18-647 Homework 1, Part 2

## Install

```text
python -m pip install -r requirements.txt
```

## Verify

```text
python -m src.part2_python.verify
```

## Collect measurements

Run the same seed and sizes on each machine. The runner writes milliseconds,
status, `n`, and `log2n` to a machine-specific CSV:

```text
python -m src.part2_python.main --machine ece
python -m src.part2_python.main --machine ec2
```

For the official ten-minute experiment, use `--repeats 1` (or omit the
option, since 1 is the default). Repeating each multiplication three times is
useful for a short noise-reduction test, but it unnecessarily consumes the
ten-minute budget and can prevent the next algorithm or problem size from
being measured.

The default outputs are `runs/ece_results.csv` and `runs/ec2_results.csv`.
The runner starts at `n=1` and doubles automatically. It stops when the total
experiment reaches 10 minutes, or when the process is killed by the OS/OOM.
`--max-length` is optional and should only be used as a safety cap for a short
test or debugging; omitting it follows the assignment's stopping rule. A row
is marked `timeout`, `oom`, or `error:<type>` when it cannot provide a valid
time.

Merge the two machine files into data ready for the Excel template:

```text
python -m src.part2_python.merge_results
```

The merge step creates `runs/n2_table.csv` and `runs/fft_table.csv`. Each table
matches the spreadsheet layout with `IMUL`, `n^2`, `n ld n`, `n`, `ld n`,
ECE/EC2 runtime in milliseconds, and ECE/EC2 Mop/s.

`src/part2_python/multiplication.py` contains both algorithms. The FFT implementation uses
one decimal digit per coefficient (base 10), NumPy FFT/IFFT, rounding, and
explicit carry propagation. `src/part2_python/utils.py` contains random input generation
and the required string/coefficient conversions.

## Correctness validation

`src/part2_python/verify.py` is the correctness test. For several small and medium input
lengths, it generates random decimal strings, computes the reference result
with the O(n^2) implementation, and checks that the FFT implementation returns
the identical product. Run it with:

```text
python -m src.part2_python.verify
```

## Performance plots

Generate the two required bar charts after merging the machine results:

```text
python -m src.part2_python.plot_results
```

This creates `plots/n2_mops.png` and `plots/fft_mops.png`. Each problem
size has exactly two bars, ECE (blue) and EC2 (red), with labels such as
`IMUL16`. MOp/s is computed as
`n^2 / runtime` for the n2 algorithm and
`(5*n*log2(n)) / runtime` for FFT, with runtime converted from milliseconds.

## Part 3 CUDA/cuFFT

The Part 3 CUDA implementation is in `src/part3_cuda/`. It uses base-10
digits, double-precision cuFFT (`CUFFT_Z2Z`), a CUDA pointwise multiplication
kernel, and CPU carry propagation. Part 3 is run on a Google Colab GPU runtime
(for example, T4), not on the AWS one-vCPU instance used for Part 2.

```text
# Colab cell 1: clone/upload the repository and enter its root
%cd /content/647_hw1
!pip install -r requirements.txt

# Colab cell 2: select Runtime > Change runtime type > T4 GPU, then run:
!nvidia-smi
!bash src/part3_cuda/run_colab.sh
```

The executable records both GPU kernel/FFT time and end-to-end time in
`runs/gpu_results.csv`. Colab's CUDA runtime provides `nvcc`, CUDA, and cuFFT.
Part 3 is independent of the Part 2 multiplication code and does not change
Part 2 results. The script compiles the program, runs the automatic `n=1, 2,
4, ...` experiment, and creates the template-style GPU table and plot.

The CUDA runner also starts at `n=1`, doubles the input size, and stops after
10 minutes or an unrecoverable CUDA/OS error. Its `--max-length` option is
optional and is only a testing safeguard; omit it for the actual Part 3 run.

To run individual steps in Colab instead:

```text
!make -C src/part3_cuda
!src/part3_cuda/fft_multiply --output runs/gpu_results.csv
!python3 src/part3_cuda/plot_results.py --time total
```

This creates `runs/gpu_fft_table.csv` and `plots/gpu_fft_mops.png`. Use
`--time gpu` to plot only cuFFT/kernel time instead of end-to-end time. The
table uses the same `n ld n = 5*n*ld(n)` operation estimate as the assignment.
Download the CSV/table/plot from Colab after the run and include them in the
submission.
