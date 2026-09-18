from __future__ import annotations

import argparse
import csv
from math import log2
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Part 3 GPU table and plot.")
    parser.add_argument("--input", type=Path, default=Path("runs/gpu_results.csv"))
    parser.add_argument("--table", type=Path, default=Path("runs/gpu_fft_table.csv"))
    parser.add_argument("--plot", type=Path, default=Path("plots/gpu_fft_mops.png"))
    parser.add_argument("--time", choices=("gpu", "total"), default="total")
    args = parser.parse_args()

    rows = []
    with args.input.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["status"] != "success":
                continue
            n = int(row["n"])
            runtime_ms = float(row["gpu_time_ms"] if args.time == "gpu" else row["total_ms"])
            log_n = int(log2(n)) if n > 0 else 0
            operations = 5 * n * log_n
            rows.append((n, log_n, runtime_ms, operations,
                         operations / runtime_ms / 1000 if runtime_ms else 0.0))
    rows.sort()
    if not rows:
        raise ValueError("no successful GPU measurements found")

    args.table.parent.mkdir(parents=True, exist_ok=True)
    with args.table.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["IMUL", "n^2", "n ld n", "n", "ld n",
                         "GPU Runtime [ms]", "Mop/s GPU"])
        for n, log_n, runtime_ms, operations, mops in rows:
            writer.writerow([f"IMUL{n}", n * n, operations, n, log_n,
                             f"{runtime_ms:.6f}", f"{mops:.6f}"])

    figure, axis = plt.subplots(figsize=(10, 6))
    values = [row[4] for row in rows]
    bars = axis.bar([row[0] for row in rows], values, color="#568bd3", width=0.7)
    axis.set_title("GPU FFT Based Long Integer Multiplication",
                   loc="left", fontweight="bold", fontsize=18)
    axis.text(0, 1.02, "Performance [Mop/s]", transform=axis.transAxes,
              color="#777777", fontsize=12, fontweight="bold")
    axis.set_xlabel("Problem size")
    axis.set_ylabel("Mop/s")
    axis.set_xticks([row[0] for row in rows],
                    [f"IMUL{row[0]}" for row in rows])
    axis.grid(axis="y", alpha=0.3)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_visible(False)
    axis.tick_params(axis="y", length=0, colors="#666666")
    axis.tick_params(axis="x", length=0, colors="#555555")
    for label in axis.get_xticklabels():
        label.set_fontweight("bold")
    axis.bar_label(bars, fmt="%.2f", padding=3, fontsize=8)
    figure.tight_layout()
    args.plot.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.plot, dpi=200)
    plt.close(figure)
    print(f"saved {args.table}")
    print(f"saved {args.plot}")


if __name__ == "__main__":
    main()
