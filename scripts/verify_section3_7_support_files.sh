#!/usr/bin/env bash
set -euo pipefail

REPO=${1:-${REPO:-.}}
if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: repository directory does not exist: ${REPO}" >&2
  exit 2
fi
REPO=$(cd "${REPO}" && pwd)
cd "${REPO}"

# Manuscript drafts and local transfer bundles are not reproducibility artifacts.
for draft in \
  NewSection_3.7.md \
  NewSection_3.7_*.md \
  section3_7_artifacts.zip \
  section3_7_update_bundle.zip; do
  if [[ -e "${draft}" ]]; then
    echo "ERROR: ${draft} is manuscript/local material and must not be committed to the reproducibility repository root." >&2
    exit 1
  fi
done

required_files=(
  "README.md"
  "MANIFEST.md"
  "metadata/zz4_wave1_kernel_manifest.json"
  "hardware_analysis/zz4_wave1_distortion_metrics.csv"
  "hardware_analysis/zz4_wave1_distortion_uncertainty.csv"
  "hardware_analysis/zz4_wave1_distortion_uncertainty.json"
  "statevector_reference/zz4_K_all_all.npy"
  "hardware_kernels/zz4_H0_kernel.csv"
  "hardware_kernels/zz4_H1_kernel.csv"
  "hardware_kernels/zz4_H2_kernel.csv"
  "hardware_kernels/zz4_H0_kernel.npy"
  "hardware_kernels/zz4_H1_kernel.npy"
  "hardware_kernels/zz4_H2_kernel.npy"
  "scripts/08b_audit_kernel_reconstruction.py"
  "scripts/09b_analyze_wave1_distortion_direct.py"
  "scripts/09c_wave1_distortion_uncertainty.py"
  "scripts/verify_section3_7_support_files.sh"
)
for f in "${required_files[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: required Section 3.7 support file is missing: ${f}" >&2
    exit 1
  fi
done

"${PYTHON_BIN:-python}" - <<'PY'
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

root = Path.cwd()

def assert_close(name: str, got: float, exp: float, tol: float = 5e-12) -> None:
    if not math.isfinite(got) or abs(got - exp) > tol:
        raise SystemExit(f"ERROR: {name}: got {got!r}, expected {exp!r}")

def read_metrics() -> dict[str, dict[str, str]]:
    with (root / "hardware_analysis/zz4_wave1_distortion_metrics.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 3:
        raise SystemExit(f"ERROR: expected 3 distortion-metric rows, observed {len(rows)}")
    by = {row["regime_id"]: row for row in rows}
    if set(by) != {"H0", "H1", "H2"}:
        raise SystemExit(f"ERROR: unexpected regimes in distortion metrics: {sorted(by)}")
    return by

metrics = read_metrics()

expected_metrics = {
    "H0": {
        "effective_rank_hardware": 21.184209317363713,
        "effective_rank_statevector": 17.971891698723347,
        "effective_rank_change": 3.212317618640366,
        "min_eigenvalue_before_psd": 0.428763111071851,
        "min_eigenvalue_after_psd": 0.42876311107185194,
        "psd_correction_frobenius": 8.583547173776992e-15,
        "psd_correction_frobenius_relative": 1.627201233628325e-15,
        "CKA_hardware_vs_statevector": 0.9333906746578973,
    },
    "H1": {
        "effective_rank_hardware": 21.217026154911494,
        "effective_rank_statevector": 17.971891698723347,
        "effective_rank_change": 3.245134456188147,
        "min_eigenvalue_before_psd": 0.46215593566687874,
        "min_eigenvalue_after_psd": 0.4621559356668794,
        "psd_correction_frobenius": 9.259630923313487e-15,
        "psd_correction_frobenius_relative": 1.7621621375280847e-15,
        "CKA_hardware_vs_statevector": 0.9373725928446407,
    },
    "H2": {
        "effective_rank_hardware": 19.78816955060221,
        "effective_rank_statevector": 17.971891698723347,
        "effective_rank_change": 1.816277851878862,
        "min_eigenvalue_before_psd": 0.23216438914772836,
        "min_eigenvalue_after_psd": 0.23216438914772833,
        "psd_correction_frobenius": 1.070945942310601e-14,
        "psd_correction_frobenius_relative": 1.9070781048728023e-15,
        "CKA_hardware_vs_statevector": 0.9886681278100088,
    },
}

for regime, expected in expected_metrics.items():
    row = metrics[regime]
    if int(float(row["n"])) != 24:
        raise SystemExit(f"ERROR: {regime}: expected n=24")
    if int(float(row["shots_submitted_per_circuit"])) != 1024:
        raise SystemExit(f"ERROR: {regime}: expected 1024 submitted shots per circuit")
    for key, exp in expected.items():
        assert_close(f"{regime}:{key}", float(row[key]), exp)
    if float(row["min_eigenvalue_before_psd"]) <= 0:
        raise SystemExit(f"ERROR: {regime}: uncorrected minimum eigenvalue is not positive")
    if float(row["psd_correction_frobenius_relative"]) >= 2.5e-15:
        raise SystemExit(f"ERROR: {regime}: PSD relative correction is not roundoff-scale")

sv_rank = float(metrics["H0"]["effective_rank_statevector"])
rank_dist = {r: abs(float(metrics[r]["effective_rank_hardware"]) - sv_rank) for r in metrics}
if min(rank_dist, key=rank_dist.get) != "H2":
    raise SystemExit(f"ERROR: H2 is not closest to the statevector effective rank: {rank_dist}")
if not (float(metrics["H2"]["CKA_hardware_vs_statevector"]) > float(metrics["H1"]["CKA_hardware_vs_statevector"]) > float(metrics["H0"]["CKA_hardware_vs_statevector"])):
    raise SystemExit("ERROR: expected CKA ordering H2 > H1 > H0")

with (root / "metadata/zz4_wave1_kernel_manifest.json").open(encoding="utf-8") as fh:
    manifest = json.load(fh)
if manifest.get("kernel_matrices_shape_24x24") is not True:
    raise SystemExit("ERROR: kernel manifest does not confirm 24x24 matrices")
if manifest.get("all_three_kernels_present") is not True:
    raise SystemExit("ERROR: kernel manifest does not confirm all three kernels")
if manifest.get("no_missing_entries") is not True:
    raise SystemExit("ERROR: kernel manifest does not confirm no missing entries")
if manifest.get("diagonal_policy") != "measured_diagonal":
    raise SystemExit("ERROR: kernel manifest diagonal policy changed")
if "diagnostic_only" not in str(manifest.get("psd_policy", "")):
    raise SystemExit("ERROR: kernel manifest PSD policy is not diagnostic-only")

manifest_rows = {row["regime_id"]: row for row in manifest.get("rows", [])}
if set(manifest_rows) != {"H0", "H1", "H2"}:
    raise SystemExit(f"ERROR: unexpected regimes in kernel manifest: {sorted(manifest_rows)}")
for regime, row in manifest_rows.items():
    if row.get("shape_rows") != 24 or row.get("shape_cols") != 24:
        raise SystemExit(f"ERROR: {regime}: kernel manifest shape mismatch")
    if row.get("finite_entry_count") != 576 or row.get("missing_entry_count") != 0:
        raise SystemExit(f"ERROR: {regime}: finite/missing entry count mismatch")
    if row.get("diagonal_policy") != "measured_diagonal":
        raise SystemExit(f"ERROR: {regime}: row-level diagonal policy changed")
    if row.get("symmetrization_policy") != "average_duplicate_entries_then_mirror":
        raise SystemExit(f"ERROR: {regime}: symmetrization policy changed")
    assert_close(f"{regime}:manifest min eigen before", float(row["min_eigenvalue_before_psd"]), expected_metrics[regime]["min_eigenvalue_before_psd"])
    assert_close(f"{regime}:manifest PSD Frobenius relative", float(row["psd_correction_frobenius_relative"]), expected_metrics[regime]["psd_correction_frobenius_relative"])

# Unit-diagonal sensitivity checks for effective rank from the uncertainty artifact.
with (root / "hardware_analysis/zz4_wave1_distortion_uncertainty.csv").open(newline="", encoding="utf-8") as fh:
    unc_rows = list(csv.DictReader(fh))
unit_expected = {
    "H0": (21.489533743636546, 0.30532442627283274),
    "H1": (21.525768064821914, 0.3087419099104203),
    "H2": (20.202003747276425, 0.41383419667421606),
}
for regime, (unit_rank, delta) in unit_expected.items():
    matches = [
        row for row in unc_rows
        if row.get("analysis_block") == "diagonal_robustness"
        and row.get("metric") == "effective_rank"
        and row.get("artifact_regime") == regime
        and row.get("contrast") == "unit_diagonal_minus_measured_diagonal"
    ]
    if len(matches) != 1:
        raise SystemExit(f"ERROR: expected exactly one unit-diagonal effective-rank sensitivity row for {regime}, found {len(matches)}")
    row = matches[0]
    assert_close(f"{regime}:unit diagonal effective rank", float(row["point_estimate"]), unit_rank)
    assert_close(f"{regime}:unit diagonal effective-rank delta", float(row["delta"]), delta)
    if row.get("diagonal_policy") != "hardware_diagonal_forced_to_one":
        raise SystemExit(f"ERROR: {regime}: unexpected diagonal-policy label in unit-diagonal row")

with (root / "hardware_analysis/zz4_wave1_distortion_uncertainty.json").open(encoding="utf-8") as fh:
    unc_json = json.load(fh)
if unc_json.get("diagonal_policy") != "Reported kernels retain measured diagonal; unit-diagonal calculations are sensitivity checks only.":
    raise SystemExit("ERROR: uncertainty JSON diagonal-policy statement changed")
if unc_json.get("resampling_unit") != "frozen_subset_window":
    raise SystemExit("ERROR: uncertainty JSON resampling unit changed")

readme = (root / "README.md").read_text(encoding="utf-8")
manifest_text = (root / "MANIFEST.md").read_text(encoding="utf-8")
for token in (
    "Section 3.7",
    "Effective-rank and PSD diagnostics",
    "verify_section3_7_support_files.sh",
    "NewSection_3.7.md",
):
    if token not in readme:
        raise SystemExit(f"ERROR: README.md missing token: {token}")
    if token not in manifest_text:
        raise SystemExit(f"ERROR: MANIFEST.md missing token: {token}")

print("[section3.7] verification passed")
print("effective ranks: SV=17.9718916987; H0=21.1842093174; H1=21.2170261549; H2=19.7881695506")
print("rank inflation: H0=+3.2123176186; H1=+3.2451344562; H2=+1.8162778519")
print("PSD minima before clip: H0=0.4287631111; H1=0.4621559357; H2=0.2321643891")
print("PSD relative Frobenius corrections: H0=1.627e-15; H1=1.762e-15; H2=1.907e-15")
print("unit-diagonal effective-rank sensitivities: H0=+0.3053; H1=+0.3087; H2=+0.4138")
PY

echo "[section3.7] support files:"
ls -lh \
  metadata/zz4_wave1_kernel_manifest.json \
  hardware_analysis/zz4_wave1_distortion_metrics.csv \
  hardware_analysis/zz4_wave1_distortion_uncertainty.csv \
  hardware_analysis/zz4_wave1_distortion_uncertainty.json \
  scripts/verify_section3_7_support_files.sh \
  README.md \
  MANIFEST.md

echo "[section3.7] key CSV preview:"
head -n 2 hardware_analysis/zz4_wave1_distortion_metrics.csv

echo "[section3.7] SHA-256 checks:"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum \
    metadata/zz4_wave1_kernel_manifest.json \
    hardware_analysis/zz4_wave1_distortion_metrics.csv \
    hardware_analysis/zz4_wave1_distortion_uncertainty.csv \
    hardware_analysis/zz4_wave1_distortion_uncertainty.json \
    scripts/verify_section3_7_support_files.sh \
    README.md \
    MANIFEST.md
else
  shasum -a 256 \
    metadata/zz4_wave1_kernel_manifest.json \
    hardware_analysis/zz4_wave1_distortion_metrics.csv \
    hardware_analysis/zz4_wave1_distortion_uncertainty.csv \
    hardware_analysis/zz4_wave1_distortion_uncertainty.json \
    scripts/verify_section3_7_support_files.sh \
    README.md \
    MANIFEST.md
fi
