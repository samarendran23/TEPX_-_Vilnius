#!/usr/bin/env python3
"""Plot reverse-bias IV curve for a given module/date/hybridID.

This will read:
  /Users/samar/work-at-vilnius-university/qc_data_analysis/qc_data/
    run_<module>-<date>/Results_dirigent/iv_curve/Module<hybridID>_iv_curve.csv

Example:
  python plot_iv_curve.py P-1009 17022026 0

Reads:
  .../run_P-1009-17022026/Results_dirigent/iv_curve/Module0_iv_curve.csv

And saves BOTH:
  .../plots_iv_curve/P-1009_Module0_iv_curve_17022026.png
  .../plots_iv_curve/P-1009_Module0_iv_curve_17022026.pdf

The script:
- reads Voltage (V), Current (A)
- flips sign for both V and I
- converts current to microamp (µA)
- plots Reverse Bias (V) vs Leakage Current (µA)
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(
    "/Users/samar/work-at-vilnius-university/qc_data_analysis/qc_data"
)

PLOT_BASE_DIR = Path(
    "/Users/samar/work-at-vilnius-university/qc_data_analysis/plots_iv_curve"
)


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: python plot_iv_curve.py <module> <date> <hybridID>\n"
            "Example: python plot_iv_curve.py P-1009 17022026 0"
        )
        return 2

    module = sys.argv[1].strip()        # e.g. P-1009
    date = sys.argv[2].strip()          # e.g. 17022026
    hybridID = sys.argv[3].strip()      # e.g. 0

    run_name = f"run_{module}-{date}"
    module_name = f"Module{hybridID}"

    csv_path = (
        BASE_DIR
        / run_name
        / "Results_dirigent"
        / "iv_curve"
        / f"{module_name}_iv_curve.csv"
    )

    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}")
        return 1

    df = pd.read_csv(csv_path)

    # Be tolerant to small header variations
    v_col = None
    i_col = None
    for c in df.columns:
        cl = c.strip().lower()
        if "voltage" in cl:
            v_col = c
        if "current" in cl:
            i_col = c

    if v_col is None or i_col is None:
        print(f"ERROR: Could not find voltage/current columns in {list(df.columns)}")
        return 1

    # Flip sign to make reverse bias positive
    df["Reverse Bias (V)"] = -df[v_col].astype(float)

    # Flip sign and convert A -> microA
    df["Leakage Current (µA)"] = (-df[i_col].astype(float)) * 1e6

    # Sort by bias just in case
    df = df.sort_values("Reverse Bias (V)")

    # Plot
    plt.figure(figsize=(7.5, 5.0))
    plt.plot(
        df["Reverse Bias (V)"],
        df["Leakage Current (µA)"],
        marker="o",
        color='black',
        linewidth=1.5,
        markersize=4,
    )

    plt.xlabel("Reverse Bias (V)")
    plt.ylabel("Leakage Current (µA)")
    plt.title(f"IV Curve: {module}")
    plt.grid(True, alpha=0.3)

    # Y-axis limit: 0 to 1.5 * max(y)
    #y_max = float(df["Leakage Current (µA)"].max())
    #plt.ylim(0, 1.2 * y_max if y_max > 0 else 1.0)

    out_stem = f"{module}_{module_name}_iv_curve_{date}"

    # Save into a dedicated plot folder (central location)
    plot_dir = PLOT_BASE_DIR
    plot_dir.mkdir(parents=True, exist_ok=True)

    out_png = plot_dir / f"{out_stem}.png"
    out_pdf = plot_dir / f"{out_stem}.pdf"

    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.savefig(out_pdf)

    print(f"Saved plot: {out_png}")
    print(f"Saved plot: {out_pdf}")

    # Optional: show window if running interactively
    plt.show()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

