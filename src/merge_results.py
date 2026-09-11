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
    parser.add_argument("--output", type=Path, default=Path("runs/merged_results.csv"))
    args = parser.parse_args()
    ece, ec2 = read_results(args.ece), read_results(args.ec2)
    keys = sorted(set(ece) | set(ec2), key=lambda item: (item[0], item[1]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        fields = ["algorithm", "n", "log2n", "ECE Runtime [ms]", "EC2 Runtime [ms]"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for algorithm, n in keys:
            writer.writerow({"algorithm": algorithm, "n": n, "log2n": n.bit_length() - 1,
                             "ECE Runtime [ms]": ece.get((algorithm, n), ""),
                             "EC2 Runtime [ms]": ec2.get((algorithm, n), "")})
    print(f"saved {args.output}")


if __name__ == "__main__":
    main()
