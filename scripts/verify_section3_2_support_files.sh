#!/usr/bin/env bash
set -euo pipefail

REPRO="${1:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"
if [[ ! -d "$REPRO" ]]; then
  echo "ERROR: REPRO does not exist: $REPRO" >&2
  exit 1
fi

cd "$REPRO"

python - <<'PY'
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path.cwd()

required = [
    "frozen_subset/hardware_subset_event_onset_next_1h.csv",
    "statevector_reference/zz4_K_all_all.npy",
    "hardware_kernels/zz4_H0_kernel.npy",
    "hardware_kernels/zz4_H1_kernel.npy",
    "hardware_kernels/zz4_H2_kernel.npy",
    "hardware_kernels/zz4_H0_kernel.csv",
    "hardware_kernels/zz4_H1_kernel.csv",
    "hardware_kernels/zz4_H2_kernel.csv",
    "hardware_analysis/zz4_wave1_distortion_metrics.csv",
    "hardware_analysis/zz4_wave1_distortion_summary.md",
    "hardware_analysis/zz4_wave1_distortion_summary.json",
    "scripts/09b_analyze_wave1_distortion_direct.py",
]

missing = [p for p in required if not (ROOT / p).is_file()]
if missing:
    raise SystemExit("Missing Section 3.2 support files:\n" + "\n".join(missing))

if (ROOT / "NewSection_3.2.md").exists():
    raise SystemExit("NewSection_3.2.md is present in the repository root; remove it before committing.")

metrics_path = ROOT / "hardware_analysis/zz4_wave1_distortion_metrics.csv"
with metrics_path.open(newline="") as f:
    rows = list(csv.DictReader(f))

if len(rows) != 3:
    raise AssertionError(f"Expected 3 metric rows, found {len(rows)}")
by_regime = {row["regime_id"]: row for row in rows}
if set(by_regime) != {"H0", "H1", "H2"}:
    raise AssertionError(f"Unexpected regimes: {sorted(by_regime)}")

expected = {
    "H0": {
        "n": 24,
        "shots_submitted_per_circuit": 1024,
        "offdiag_spearman_vs_statevector": 0.741297081842571,
        "offdiag_pearson_vs_statevector": 0.8272527142734244,
        "kernel_mae": 0.04903588514843187,
        "kernel_rmse": 0.08777046763666438,
        "median_absolute_kernel_error": 0.02615354758561056,
        "max_absolute_kernel_error": 0.5686656028808117,
        "hardware_offdiag_variance": 0.005386539766002768,
        "statevector_offdiag_variance": 0.018655817197306912,
        "effective_rank_hardware": 21.184209317363713,
        "effective_rank_statevector": 17.971891698723347,
        "KTA_hardware": 0.18330845936020965,
        "KTA_statevector": 0.15851109235208113,
        "CKA_hardware_vs_statevector": 0.9333906746578973,
        "CKA_statevector_self": 1.0,
        "CKA_drop_relative_to_statevector": 0.06660932534210273,
    },
    "H1": {
        "n": 24,
        "shots_submitted_per_circuit": 1024,
        "offdiag_spearman_vs_statevector": 0.7749509552911102,
        "offdiag_pearson_vs_statevector": 0.8427741783413908,
        "kernel_mae": 0.04728950462019737,
        "kernel_rmse": 0.08642753836276364,
        "median_absolute_kernel_error": 0.026143446979889462,
        "max_absolute_kernel_error": 0.5638969084391722,
        "hardware_offdiag_variance": 0.005284249632330007,
        "statevector_offdiag_variance": 0.018655817197306912,
        "effective_rank_hardware": 21.217026154911494,
        "effective_rank_statevector": 17.971891698723347,
        "KTA_hardware": 0.18146337847595853,
        "KTA_statevector": 0.15851109235208113,
        "CKA_hardware_vs_statevector": 0.9373725928446407,
        "CKA_statevector_self": 1.0,
        "CKA_drop_relative_to_statevector": 0.0626274071553593,
    },
    "H2": {
        "n": 24,
        "shots_submitted_per_circuit": 1024,
        "offdiag_spearman_vs_statevector": 0.9437436780691297,
        "offdiag_pearson_vs_statevector": 0.9862028716378275,
        "kernel_mae": 0.025725586521733776,
        "kernel_rmse": 0.042727419504658484,
        "median_absolute_kernel_error": 0.016161047901678764,
        "max_absolute_kernel_error": 0.2639781028808117,
        "hardware_offdiag_variance": 0.009758499784896263,
        "statevector_offdiag_variance": 0.018655817197306912,
        "effective_rank_hardware": 19.7881695506022,
        "effective_rank_statevector": 17.971891698723347,
        "KTA_hardware": 0.17102484410377672,
        "KTA_statevector": 0.15851109235208113,
        "CKA_hardware_vs_statevector": 0.9886681278100088,
        "CKA_statevector_self": 1.0,
        "CKA_drop_relative_to_statevector": 0.01133187218999121,
    },
}

def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return math.nan
    return float(value)

for regime, expected_values in expected.items():
    row = by_regime[regime]
    for key, exp in expected_values.items():
        if key in {"n", "shots_submitted_per_circuit"}:
            got = int(float(row[key]))
            if got != int(exp):
                raise AssertionError(f"{regime}:{key} = {got}, expected {exp}")
        else:
            got = as_float(row, key)
            if not math.isclose(got, float(exp), rel_tol=0.0, abs_tol=2e-12):
                raise AssertionError(f"{regime}:{key} = {got}, expected {exp}")

    # Correlation p-values must remain blank/NaN in the supported minimal workflow.
    for key in ("offdiag_spearman_pvalue", "offdiag_pearson_pvalue"):
        value = row.get(key, "")
        if value not in ("", "nan", "NaN"):
            raise AssertionError(f"{regime}:{key} should be blank/NaN, found {value!r}")

    if as_float(row, "min_eigenvalue_before_psd") <= 0:
        raise AssertionError(f"{regime}: uncorrected kernel is not PSD-positive")
    if as_float(row, "psd_correction_frobenius_relative") >= 5e-15:
        raise AssertionError(f"{regime}: PSD relative Frobenius correction is not roundoff-scale")

# Descriptive point-estimate ordering used in Section 3.2.
for metric in ("offdiag_spearman_vs_statevector", "offdiag_pearson_vs_statevector", "CKA_hardware_vs_statevector"):
    vals = {r: as_float(by_regime[r], metric) for r in by_regime}
    if max(vals, key=vals.get) != "H2":
        raise AssertionError(f"H2 is not best for {metric}: {vals}")

for metric in ("kernel_mae", "kernel_rmse", "median_absolute_kernel_error", "max_absolute_kernel_error"):
    vals = {r: as_float(by_regime[r], metric) for r in by_regime}
    if min(vals, key=vals.get) != "H2":
        raise AssertionError(f"H2 is not lowest for {metric}: {vals}")

sv_rank = as_float(by_regime["H0"], "effective_rank_statevector")
rank_dist = {r: abs(as_float(by_regime[r], "effective_rank_hardware") - sv_rank) for r in by_regime}
if min(rank_dist, key=rank_dist.get) != "H2":
    raise AssertionError(f"H2 is not closest to statevector effective rank: {rank_dist}")

sv_kta = as_float(by_regime["H0"], "KTA_statevector")
kta_uplift = {r: as_float(by_regime[r], "KTA_hardware") - sv_kta for r in by_regime}
if any(v <= 0 for v in kta_uplift.values()):
    raise AssertionError(f"Expected positive hardware KTA uplift in all regimes: {kta_uplift}")
if min(kta_uplift, key=kta_uplift.get) != "H2":
    raise AssertionError(f"H2 is not the smallest KTA uplift: {kta_uplift}")

sv_var = as_float(by_regime["H0"], "statevector_offdiag_variance")
retained = {r: as_float(by_regime[r], "hardware_offdiag_variance") / sv_var for r in by_regime}
if not (retained["H0"] < 0.30 and retained["H1"] < 0.30 and 0.50 < retained["H2"] < 0.55):
    raise AssertionError(f"Unexpected off-diagonal variance-retention pattern: {retained}")

summary_md = (ROOT / "hardware_analysis/zz4_wave1_distortion_summary.md").read_text()
for token in ("H0", "H1", "H2", "0.933391", "0.937373", "0.988668"):
    if token not in summary_md:
        raise AssertionError(f"Missing token in distortion summary: {token}")

print("Section 3.2 verification passed.")
print("metrics rows: H0, H1, H2")
print("H2 point estimates: highest Spearman/Pearson/CKA; lowest MAE/RMSE/MedAE/MaxAE")
print("PSD relative Frobenius corrections: all < 5e-15")
print("hardware KTA uplift is treated as distortion; H2 has the smallest uplift")
print("off-diagonal variance retained: H0={:.1%}, H1={:.1%}, H2={:.1%}".format(retained["H0"], retained["H1"], retained["H2"]))
PY
