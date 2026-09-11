from __future__ import annotations

import argparse
import csv
import random
import time
from pathlib import Path

from .multiplication import multiply_fft, multiply_quadratic
from .utils import operation_count, random_number


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Part 2 multiplication measurements.")
    parser.add_argument("--machine", choices=["ece", "ec2"], required=True)
    parser.add_argument("--max-length", type=int, default=16384)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=18647)
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.max_length < 1 or args.repeats < 1:
        parser.error("--max-length and --repeats must be positive")
    output = args.output or Path("runs") / f"{args.machine}_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    sizes, length = [], 1
    while length <= args.max_length:
        sizes.append(length)
        length *= 2
    rng = random.Random(args.seed)
    rows = []
    for n in sizes:
        left, right = random_number(n, rng), random_number(n, rng)
        expected = multiply_quadratic(left, right)
        for algorithm, multiply in (("quadratic", multiply_quadratic), ("fft", multiply_fft)):
            start = time.perf_counter()
            status, elapsed_ms = "ok", None
            try:
                for _ in range(args.repeats):
                    actual = multiply(left, right)
                    if actual != expected:
                        raise AssertionError("incorrect result")
                elapsed_ms = (time.perf_counter() - start) * 1000 / args.repeats
                if elapsed_ms > args.timeout_seconds * 1000:
                    status = "timeout"
            except MemoryError:
                status = "oom"
            except Exception as error:
                status = f"error:{type(error).__name__}"
            rows.append(
                {"algorithm": algorithm, "n": n, "log2n": n.bit_length() - 1,
                 "runtime_ms": "" if elapsed_ms is None else f"{elapsed_ms:.6f}",
                 "status": status, "operations": operation_count(algorithm, n)}
            )
            print(rows[-1], flush=True)
            if status == "timeout":
                break
        if rows[-1]["status"] == "timeout":
            break
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved {output}")


if __name__ == "__main__":
    main()

