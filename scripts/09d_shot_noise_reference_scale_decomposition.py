#!/usr/bin/env python3
"""Compute the Section 2.12 shot-noise reference-scale decomposition.

Inputs expected in the reproducibility repository:
  hardware_analysis/zz4_wave1_distortion_metrics.csv
  hardware_kernels/zz4_wave1_kernel_entries_long.csv
  hardware_kernels/zz4_H0_kernel.csv
  hardware_kernels/zz4_H1_kernel.csv
  hardware_kernels/zz4_H2_kernel.csv

Outputs:
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md

This is a diagnostic quadrature decomposition, not a physical noise model.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd


REGIME_TO_MANUSCRIPT = {"H0": "M0", "H1": "M1", "H2": "M2"}
OUTPUT_STEM = "zz4_wave1_shot_noise_reference_scale_decomposition"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_matrix_csv(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"missing matrix CSV: {path}")
    arr = pd.read_csv(path, header=None).to_numpy(dtype=float)
    if arr.shape != (24, 24):
        raise ValueError(f"{path} has shape {arr.shape}, expected (24, 24)")
    if not np.isfinite(arr).all():
        raise ValueError(f"{path} contains non-finite values")
    if not np.allclose(arr, arr.T, atol=0.0, rtol=0.0):
        raise ValueError(f"{path} is not exactly symmetric")
    return arr


def offdiag_values(K: np.ndarray) -> np.ndarray:
    return K[~np.eye(K.shape[0], dtype=bool)]


def infer_shots(metrics: pd.DataFrame, entries: pd.DataFrame) -> int:
    metric_shots = sorted(set(metrics["shots_submitted_per_circuit"].dropna().astype(int).tolist()))
    entry_shots = sorted(set(entries["shots_observed"].dropna().astype(int).tolist()))
    if metric_shots != [1024]:
        raise ValueError(f"expected metrics shot count [1024], observed {metric_shots}")
    if entry_shots != [1024]:
        raise ValueError(f"expected kernel-entry shot count [1024], observed {entry_shots}")
    return 1024


def compute(root: Path) -> pd.DataFrame:
    metrics_path = root / "hardware_analysis" / "zz4_wave1_distortion_metrics.csv"
    entries_path = root / "hardware_kernels" / "zz4_wave1_kernel_entries_long.csv"

    if not metrics_path.exists():
        raise FileNotFoundError(f"missing metrics CSV: {metrics_path}")
    if not entries_path.exists():
        raise FileNotFoundError(f"missing kernel entries CSV: {entries_path}")

    metrics = pd.read_csv(metrics_path)
    entries = pd.read_csv(entries_path)

    required_metric_cols = {"regime_id", "n", "shots_submitted_per_circuit", "kernel_rmse", "hardware_offdiag_variance"}
    missing_metric_cols = required_metric_cols.difference(metrics.columns)
    if missing_metric_cols:
        raise ValueError(f"missing columns in {metrics_path}: {sorted(missing_metric_cols)}")

    required_entry_cols = {"regime_id", "i", "j", "all_zero_count", "shots_observed", "kernel_value_raw"}
    missing_entry_cols = required_entry_cols.difference(entries.columns)
    if missing_entry_cols:
        raise ValueError(f"missing columns in {entries_path}: {sorted(missing_entry_cols)}")

    if len(entries) != 900:
        raise ValueError(f"expected 900 long-form kernel-entry rows, observed {len(entries)}")
    per_regime_counts = entries.groupby("regime_id").size().to_dict()
    if per_regime_counts != {"H0": 300, "H1": 300, "H2": 300}:
        raise ValueError(f"expected 300 entries per regime, observed {per_regime_counts}")

    S = infer_shots(metrics, entries)
    # Conservative upper reference; exceeds max per-entry binomial SE by sqrt(2).
    sigma_global = 1.0 / math.sqrt(2.0 * S)

    rows: List[Dict[str, object]] = []
    metrics_by_regime = {str(r["regime_id"]): r for _, r in metrics.iterrows()}

    for regime in ["H0", "H1", "H2"]:
        if regime not in metrics_by_regime:
            raise ValueError(f"missing metrics row for regime {regime}")

        K = read_matrix_csv(root / "hardware_kernels" / f"zz4_{regime}_kernel.csv")
        p = offdiag_values(K)
        if p.size != 552:
            raise ValueError(f"{regime}: expected 552 directed off-diagonal entries, observed {p.size}")
        if np.any((p < 0.0) | (p > 1.0)):
            raise ValueError(f"{regime}: matrix contains probabilities outside [0, 1]")

        metric_row = metrics_by_regime[regime]
        rmse = float(metric_row["kernel_rmse"])
        sigma_matrix_var = float(np.mean(p * (1.0 - p) / S))
        sigma_matrix = math.sqrt(sigma_matrix_var)

        hardware_offdiag_variance = float(np.var(p))
        persisted_variance = float(metric_row["hardware_offdiag_variance"])
        if not math.isclose(hardware_offdiag_variance, persisted_variance, rel_tol=0.0, abs_tol=5e-15):
            raise ValueError(
                f"{regime}: matrix off-diagonal variance {hardware_offdiag_variance} "
                f"does not match persisted value {persisted_variance}"
            )

        rows.append(
            {
                "regime_id": regime,
                "manuscript_configuration": REGIME_TO_MANUSCRIPT[regime],
                "n": int(metric_row["n"]),
                "shots_observed_per_entry": S,
                "omega_size_directed": int(p.size),
                "omega_size_unique_unordered": int(p.size // 2),
                "kernel_rmse": rmse,
                "sigma_shot_global": sigma_global,
                "sigma_shot_global_variance": sigma_global**2,
                "residual_global": math.sqrt(max(rmse**2 - sigma_global**2, 0.0)),
                "shot_share_global": (sigma_global**2) / (rmse**2),
                "sigma_shot_matrix": sigma_matrix,
                "sigma_shot_matrix_variance": sigma_matrix_var,
                "residual_matrix": math.sqrt(max(rmse**2 - sigma_matrix**2, 0.0)),
                "shot_share_matrix": sigma_matrix_var / (rmse**2),
                "hardware_offdiag_mean": float(np.mean(p)),
                "hardware_offdiag_variance": hardware_offdiag_variance,
                "decomposition_policy": "diagnostic_quadrature_reference_not_physical_noise_model",
            }
        )

    return pd.DataFrame(rows)


def write_outputs(root: Path, table: pd.DataFrame) -> None:
    analysis_dir = root / "hardware_analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    csv_path = analysis_dir / f"{OUTPUT_STEM}.csv"
    json_path = analysis_dir / f"{OUTPUT_STEM}.json"
    md_path = analysis_dir / f"{OUTPUT_STEM}.md"

    table.to_csv(csv_path, index=False, float_format="%.15g")

    summary = {
        "artifact_type": OUTPUT_STEM,
        "created_utc": utc_now(),
        "n": 24,
        "shots_observed_per_entry": 1024,
        "global_reference_scale": {
            "formula": "1/sqrt(2*S)",
            "sigma_shot_global": float(table["sigma_shot_global"].iloc[0]),
            "variance": float(table["sigma_shot_global_variance"].iloc[0]),
            "interpretation": (
                "conservative upper reference; exceeds max per-entry binomial SE "
                "1/(2*sqrt(S)) by sqrt(2); not the sampling SE of an individual kernel entry"
            ),
        },
        "matrix_reference_scale": {
            "formula": "sqrt(mean_{(i,j) in Omega} p_ij*(1-p_ij)/S)",
            "domain": "off-diagonal directed entries i != j; symmetric matrices make directed and unique-unordered averages identical",
            "probability_source": "reconstructed hardware all-zero probabilities in hardware_kernels/zz4_H{0,1,2}_kernel.csv",
        },
        "input_paths": [
            "hardware_analysis/zz4_wave1_distortion_metrics.csv",
            "hardware_kernels/zz4_wave1_kernel_entries_long.csv",
            "hardware_kernels/zz4_H0_kernel.csv",
            "hardware_kernels/zz4_H1_kernel.csv",
            "hardware_kernels/zz4_H2_kernel.csv",
        ],
        "output_paths": [
            f"hardware_analysis/{OUTPUT_STEM}.csv",
            f"hardware_analysis/{OUTPUT_STEM}.json",
            f"hardware_analysis/{OUTPUT_STEM}.md",
        ],
        "caveat": (
            "This decomposition assumes a simple finite-shot reference scale and treats shot noise "
            "and residual hardware distortion as approximately separable in quadrature. It is diagnostic, "
            "not a full physical noise-model decomposition."
        ),
        "rows": table.to_dict(orient="records"),
    }
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# ZZ4 Wave 1 shot-noise reference-scale decomposition",
        "",
        "- Shots per circuit: `1024`",
        f"- Conservative global reference scale: `1/sqrt(2*S) = {float(table['sigma_shot_global'].iloc[0]):.12f}`",
        "- Matrix reference scale: `sqrt(mean(p_ij*(1-p_ij)/S))` over off-diagonal entries.",
        "- Interpretation: diagnostic quadrature bookkeeping only; not a physical noise-model decomposition.",
        "",
        "| Configuration | Regime | RMSE | sigma_global | residual_global | ShotShare_global | sigma_matrix | residual_matrix | ShotShare_matrix |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, r in table.iterrows():
        lines.append(
            f"| `{r['manuscript_configuration']}` | `{r['regime_id']}` | "
            f"{r['kernel_rmse']:.6f} | {r['sigma_shot_global']:.6f} | "
            f"{r['residual_global']:.6f} | {100*r['shot_share_global']:.2f}% | "
            f"{r['sigma_shot_matrix']:.6f} | {r['residual_matrix']:.6f} | "
            f"{100*r['shot_share_matrix']:.2f}% |"
        )
    lines.extend(
        [
            "",
            "The matrix-aware scale is computed from reconstructed hardware all-zero probabilities. "
            "Under this plug-in calculation, finite-shot variance accounts for less than 1% of the "
            "squared off-diagonal RMSE in `M0/H0` and `M1/H1`, and 3.98% in `M2/H2`.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"[shot-noise] wrote {csv_path.relative_to(root)}")
    print(f"[shot-noise] wrote {json_path.relative_to(root)}")
    print(f"[shot-noise] wrote {md_path.relative_to(root)}")


def compare_with_existing(root: Path, computed: pd.DataFrame, tol: float = 5e-12) -> None:
    csv_path = root / "hardware_analysis" / f"{OUTPUT_STEM}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"missing decomposition CSV for --check: {csv_path}")

    existing = pd.read_csv(csv_path)
    key_cols = [
        "regime_id",
        "manuscript_configuration",
        "n",
        "shots_observed_per_entry",
        "omega_size_directed",
        "omega_size_unique_unordered",
    ]
    value_cols = [
        "kernel_rmse",
        "sigma_shot_global",
        "sigma_shot_global_variance",
        "residual_global",
        "shot_share_global",
        "sigma_shot_matrix",
        "sigma_shot_matrix_variance",
        "residual_matrix",
        "shot_share_matrix",
        "hardware_offdiag_mean",
        "hardware_offdiag_variance",
    ]

    existing = existing.sort_values("regime_id").reset_index(drop=True)
    computed = computed.sort_values("regime_id").reset_index(drop=True)

    for col in key_cols:
        if existing[col].astype(str).tolist() != computed[col].astype(str).tolist():
            raise AssertionError(f"column {col} differs between existing and recomputed output")

    for col in value_cols:
        if not np.allclose(existing[col].to_numpy(dtype=float), computed[col].to_numpy(dtype=float), rtol=0.0, atol=tol):
            diff = np.max(np.abs(existing[col].to_numpy(dtype=float) - computed[col].to_numpy(dtype=float)))
            raise AssertionError(f"column {col} differs; max abs diff={diff}")

    print(f"[shot-noise] check passed for {csv_path.relative_to(root)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".", help="Reproducibility repository root")
    parser.add_argument("--check", action="store_true", help="Recompute and compare with existing output CSV")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    table = compute(root)
    if args.check:
        compare_with_existing(root, table)
    else:
        write_outputs(root, table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
