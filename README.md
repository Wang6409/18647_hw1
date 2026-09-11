# 18-647 Homework 1, Part 2

## Install

```text
python -m pip install -r requirements.txt
```

## Verify

```text
python -m src.verify
```

## Collect measurements

Run the same seed and sizes on each machine. The runner writes milliseconds,
status, `n`, and `log2n` to a machine-specific CSV:

```text
python -m src.main --machine ece --max-length 16384 --repeats 3
python -m src.main --machine ec2 --max-length 16384 --repeats 3
```

The default outputs are `runs/ece_results.csv` and `runs/ec2_results.csv`.
Increase `--max-length` by powers of two until the run exceeds the course
limit or the machine runs out of memory. A row is marked `timeout`, `oom`, or
`error:<type>` when it cannot provide a valid time.

Merge the two machine files into data ready for the Excel template:

```text
python -m src.merge_results
```

The merged file has one row per algorithm and problem size:
`algorithm`, `n`, `log2n`, `ECE Runtime [ms]`, and `EC2 Runtime [ms]`.
Copy the rows for `quadratic` and `fft` into the corresponding template
sections. The template computes `n^2`, `5*n*log2n`, and Mop/s.

`src/multiplication.py` contains both algorithms. The FFT implementation uses
base-10^4 coefficient blocks, NumPy FFT/IFFT, rounding, and explicit carry
propagation. `src/utils.py` contains random input generation and the required
string/coefficient conversions.
