from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_results(path: Path) -> dict[tuple[str, int], str]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            (row["algorithm"], int(row["n"])): row["runtime_ms"]
            for row in csv.DictReader(stream)
            if row["status"] == "ok"
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge ECE and EC2 measurement CSV files.")
    parser.add_argument("--ece", type=Path, default=Path("runs/ece_results.csv"))
    parser.add_argument("--ec2", type=Path, default=Path("runs/ec2_results.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = parser.parse_args()
    ece, ec2 = read_results(args.ece), read_results(args.ec2)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for algorithm in ("n2", "fft"):
        sizes = sorted(
            n for current_algorithm, n in set(ece) | set(ec2)
            if current_algorithm == algorithm
            and (algorithm, n) in ece
            and (algorithm, n) in ec2
        )
        output = args.output_dir / f"{algorithm}_table.csv"
        with output.open("w", newline="", encoding="utf-8") as stream:
            fields = ["IMUL", "n^2", "n ld n", "n", "ld n",
                      "ECE Runtime [ms]", "EC2 Runtime [ms]",
                      "Mop/s ECE", "Mop/s EC2"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for n in sizes:
                log_n = n.bit_length() - 1
                operations = n * n if algorithm == "n2" else 5 * n * log_n
                ece_ms, ec2_ms = float(ece[(algorithm, n)]), float(ec2[(algorithm, n)])
                writer.writerow({
                    "IMUL": f"IMUL{n}",
                    "n^2": n * n,
                    "n ld n": operations,
                    "n": n,
                    "ld n": log_n,
                    "ECE Runtime [ms]": f"{ece_ms:.6f}",
                    "EC2 Runtime [ms]": f"{ec2_ms:.6f}",
                    "Mop/s ECE": f"{operations / ece_ms / 1000:.6f}",
                    "Mop/s EC2": f"{operations / ec2_ms / 1000:.6f}",
                })
        print(f"saved {output}")


if __name__ == "__main__":
    main()
