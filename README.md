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

The merge step creates `runs/n2_table.csv` and `runs/fft_table.csv`. Each table
matches the spreadsheet layout with `IMUL`, `n^2`, `n ld n`, `n`, `ld n`,
ECE/EC2 runtime in milliseconds, and ECE/EC2 Mop/s.

`src/multiplication.py` contains both algorithms. The FFT implementation uses
one decimal digit per coefficient (base 10), NumPy FFT/IFFT, rounding, and
explicit carry propagation. `src/utils.py` contains random input generation
and the required string/coefficient conversions.

## Correctness validation

`src/verify.py` is the correctness test. For several small and medium input
lengths, it generates random decimal strings, computes the reference result
with the O(n^2) implementation, and checks that the FFT implementation returns
the identical product. Run it with:

```text
python -m src.verify
```

## Performance plots

Generate the two required bar charts after merging the machine results:

```text
python -m src.plot_results
```

This creates `plots/n2_mops.png` and `plots/fft_mops.png`. Each problem
size has exactly two bars, ECE (blue) and EC2 (red), with labels such as
`IMUL16`. MOp/s is computed as
`n^2 / runtime` for the n2 algorithm and
`(5*n*log2(n)) / runtime` for FFT, with runtime converted from milliseconds.
