from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def _read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = []
        for row in csv.DictReader(stream):
            ece_ms, ec2_ms = row["ECE Runtime [ms]"], row["EC2 Runtime [ms]"]
            if not ece_ms or not ec2_ms:
                continue
            rows.append(
                {
                    "label": row["IMUL"],
                    "n": int(row["n"]),
                    "ece": float(ece_ms),
                    "ec2": float(ec2_ms),
                }
            )
    return sorted(rows, key=lambda row: row["n"])


def _mops_per_second(algorithm: str, n: int, runtime_ms: float) -> float:
    operations = n * n if algorithm == "n2" else 5 * n * (n.bit_length() - 1)
    return operations / runtime_ms / 1000.0


def _plot(table: Path, algorithm: str, output: Path) -> None:
    rows = _read_rows(table)
    if not rows:
        raise ValueError(f"no complete rows found for {algorithm}")
    positions = list(range(len(rows)))
    width = 0.38
    ece_values = [_mops_per_second(algorithm, row["n"], row["ece"]) for row in rows]
    ec2_values = [_mops_per_second(algorithm, row["n"], row["ec2"]) for row in rows]
    figure, axis = plt.subplots(figsize=(10, 6))
    axis.bar([position - width / 2 for position in positions], ece_values, width,
             label="ECE", color="#568bd3")
    axis.bar([position + width / 2 for position in positions], ec2_values, width,
             label="EC2", color="#c00000")
    axis.set_xticks(positions, [row["label"] for row in rows])
    axis.set_ylabel("Mop/s")
    axis.set_title(
        "Naive Long Integer Multiplication" if algorithm == "n2"
        else "FFT Based Long Integer Multiplication",
        loc="left", fontweight="bold", fontsize=18,
    )
    axis.text(0, 1.02, "Performance [Mop/s]", transform=axis.transAxes,
              color="#777777", fontsize=12, fontweight="bold")
    axis.legend(loc="upper right", frameon=False)
    axis.grid(axis="y", alpha=0.3)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_visible(False)
    axis.tick_params(axis="y", length=0, colors="#666666")
    axis.tick_params(axis="x", length=0, colors="#555555")
    axis.set_axisbelow(True)
    for label in axis.get_xticklabels():
        label.set_fontweight("bold")
        label.set_fontsize(11)
    for container in axis.containers:
        axis.bar_label(container, fmt="%.2f", padding=3, fontsize=8)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=200)
    plt.close(figure)
    print(f"saved {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot ECE/EC2 MOp/s comparisons.")
    parser.add_argument("--input-dir", type=Path, default=Path("runs"))
    parser.add_argument("--output-dir", type=Path, default=Path("plots"))
    args = parser.parse_args()
    _plot(args.input_dir / "n2_table.csv", "n2", args.output_dir / "n2_mops.png")
    _plot(args.input_dir / "fft_table.csv", "fft", args.output_dir / "fft_mops.png")


if __name__ == "__main__":
    main()
