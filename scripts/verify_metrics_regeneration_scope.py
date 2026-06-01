#!/usr/bin/env python3
"""
verify_metrics_regeneration_scope.py

Guard for the Section 2.8 / 2.13 invariant: regenerating
``hardware_analysis/zz4_wave1_distortion_metrics.csv`` with the supported
direct-workflow generator (09b) must change ONLY the two correlation
p-value columns (populated -> blank/NaN) and must not move any other
reported value beyond float64 roundoff.

It regenerates 09b into a throwaway project root (inputs symlinked, so the
committed artifacts are never touched) and diffs the result, column by
column, against the committed CSV.

Exit 0 : scope confirmed -- safe to commit the regenerated CSV.
Exit 1 : scope violated -- a non-p-value column moved beyond --atol, the
         schema/rows changed, or the p-value columns were not blanked.

Run from the repository root, in the PINNED environment:

    python scripts/verify_metrics_regeneration_scope.py --project-root .
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

PVAL_COLS = ["offdiag_spearman_pvalue", "offdiag_pearson_pvalue"]
INPUT_DIRS = ["statevector_reference", "frozen_subset", "hardware_kernels"]
GEN_SCRIPT = "scripts/09b_analyze_wave1_distortion_direct.py"
METRICS_REL = "hardware_analysis/zz4_wave1_distortion_metrics.csv"


def regenerate(root: Path) -> pd.DataFrame:
    """Run 09b into a temp root and return the regenerated metrics frame."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for d in INPUT_DIRS:
            (tmp / d).symlink_to((root / d).resolve())
        (tmp / "hardware_analysis").mkdir()
        proc = subprocess.run(
            [sys.executable, str(root / GEN_SCRIPT), "--project-root", str(tmp)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout + proc.stderr)
            raise SystemExit(f"09b generator failed (exit {proc.returncode})")
        return pd.read_csv(tmp / METRICS_REL)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument(
        "--atol",
        type=float,
        default=1e-9,
        help="max allowed abs diff for non-p-value numeric columns "
        "(default 1e-9: well below any reported significant digit, "
        "well above float64/BLAS roundoff)",
    )
    args = ap.parse_args()
    root = Path(args.project_root).resolve()

    committed = pd.read_csv(root / METRICS_REL)
    regen = regenerate(root)

    problems: list[str] = []
    if list(committed.columns) != list(regen.columns):
        problems.append("column set or order changed")
    if list(committed.get("regime_id", [])) != list(regen.get("regime_id", [])):
        problems.append("regime_id rows changed")

    print(f"{'column':40s} {'verdict':28s} max|delta|")
    print("-" * 84)
    for c in committed.columns:
        if c == "regime_id":
            print(f"{c:40s} {'key (unchanged)':28s} -")
            continue
        a = pd.to_numeric(committed[c], errors="coerce").to_numpy(float)
        b = pd.to_numeric(regen[c], errors="coerce").to_numpy(float)

        if c in PVAL_COLS:
            if not np.isnan(b).all():
                problems.append(f"{c}: regeneration did NOT blank this column")
                print(f"{c:40s} {'FAIL: not blanked':28s} -")
            else:
                was = "populated" if not np.isnan(a).all() else "already blank"
                print(f"{c:40s} {('OK: ' + was + ' -> NaN'):28s} -")
            continue

        d = float(np.nanmax(np.abs(a - b))) if a.size else 0.0
        if d > args.atol:
            problems.append(f"{c}: moved by {d:.3e} (> atol {args.atol:.0e})")
            print(f"{c:40s} {'FAIL: moved':28s} {d:.2e}")
        else:
            print(f"{c:40s} {'ok':28s} {d:.2e}")

    print("-" * 84)
    if problems:
        print("SCOPE VIOLATED:")
        for p in problems:
            print("  - " + p)
        return 1
    print(
        "SCOPE OK: only the two correlation p-value columns change "
        "(populated -> NaN); no reported value moved beyond atol."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
