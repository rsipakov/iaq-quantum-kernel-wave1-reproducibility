#!/usr/bin/env bash
set -euo pipefail

REPO=${1:-${REPO:-.}}
if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: repository directory does not exist: ${REPO}" >&2
  exit 2
fi
REPO=$(cd "${REPO}" && pwd)
cd "${REPO}"

for draft in NewSection_3.4.md NewSection_3.4_Revised*.md NewSection_3.4_*Instructions.md; do
  if [[ -e "${draft}" ]]; then
    echo "ERROR: ${draft} is a manuscript draft and must not be committed to the reproducibility repository root." >&2
    exit 1
  fi
done

required_files=(
  "hardware_analysis/zz4_wave1_distortion_metrics.csv"
  "hardware_analysis/zz4_wave1_distortion_uncertainty.csv"
  "hardware_analysis/zz4_wave1_distortion_uncertainty.json"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md"
  "hardware_analysis/zz4_wave1_label_permutation_reference.csv"
  "hardware_analysis/zz4_wave1_label_permutation_reference.json"
  "hardware_analysis/qiskit_kta_cka_permutation_tests.csv"
  "hardware_kernels/zz4_wave1_kernel_entries_long.csv"
  "hardware_kernels/zz4_H0_kernel.csv"
  "hardware_kernels/zz4_H1_kernel.csv"
  "hardware_kernels/zz4_H2_kernel.csv"
  "hardware_kernels/zz4_H0_kernel.npy"
  "hardware_kernels/zz4_H1_kernel.npy"
  "hardware_kernels/zz4_H2_kernel.npy"
  "statevector_reference/zz4_K_all_all.npy"
  "frozen_subset/hardware_subset_event_onset_next_1h.csv"
  "scripts/09b_analyze_wave1_distortion_direct.py"
  "scripts/09c_wave1_distortion_uncertainty.py"
  "scripts/09d_shot_noise_reference_scale_decomposition.py"
  "scripts/09e_label_permutation_reference.py"
)

for f in "${required_files[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: required Section 3.4 support file is missing: ${f}" >&2
    exit 1
  fi
done

${PYTHON_BIN:-python} - <<'PY'
import csv
import json
import math
from pathlib import Path

root = Path.cwd()

def assert_close(name, got, exp, tol=1e-9):
    if not math.isfinite(got) or abs(got - exp) > tol:
        raise SystemExit(f"ERROR: {name}: got {got!r}, expected {exp!r} within {tol}")

def as_float(row, key):
    try:
        return float(row[key])
    except Exception as exc:
        raise SystemExit(f"ERROR: cannot parse {key!r} from row {row}: {exc}")

def read_csv(path):
    with open(root / path, newline="") as fh:
        return list(csv.DictReader(fh))

# Distortion metrics: CKA/KTA tension point estimates.
metrics = read_csv("hardware_analysis/zz4_wave1_distortion_metrics.csv")
if len(metrics) != 3:
    raise SystemExit(f"ERROR: expected 3 distortion metric rows, found {len(metrics)}")
by_regime = {row["regime_id"]: row for row in metrics}
if set(by_regime) != {"H0", "H1", "H2"}:
    raise SystemExit(f"ERROR: metric regimes are {sorted(by_regime)}")

expected_metrics = {
    "H0": dict(cka=0.9333906746578973, kta=0.18330845936020965, kta_sv=0.15851109235208113, rmse=0.08777046763666438),
    "H1": dict(cka=0.9373725928446407, kta=0.18146337847595853, kta_sv=0.15851109235208113, rmse=0.08642753836276364),
    "H2": dict(cka=0.9886681278100088, kta=0.17102484410377672, kta_sv=0.15851109235208113, rmse=0.042727419504658484),
}
for regime, exp in expected_metrics.items():
    row = by_regime[regime]
    if int(float(row["n"])) != 24:
        raise SystemExit(f"ERROR: {regime} n != 24")
    if int(float(row["shots_submitted_per_circuit"])) != 1024:
        raise SystemExit(f"ERROR: {regime} shots_submitted_per_circuit != 1024")
    if row.get("offdiag_spearman_pvalue", "").strip() not in {"", "nan", "NaN", "NA"}:
        raise SystemExit(f"ERROR: {regime} offdiag_spearman_pvalue is not blank/NaN")
    if row.get("offdiag_pearson_pvalue", "").strip() not in {"", "nan", "NaN", "NA"}:
        raise SystemExit(f"ERROR: {regime} offdiag_pearson_pvalue is not blank/NaN")
    assert_close(f"{regime} CKA", as_float(row, "CKA_hardware_vs_statevector"), exp["cka"])
    assert_close(f"{regime} KTA_hw", as_float(row, "KTA_hardware"), exp["kta"])
    assert_close(f"{regime} KTA_sv", as_float(row, "KTA_statevector"), exp["kta_sv"])
    assert_close(f"{regime} RMSE", as_float(row, "kernel_rmse"), exp["rmse"])
    if as_float(row, "min_eigenvalue_before_psd") <= 0:
        raise SystemExit(f"ERROR: {regime} uncorrected minimum eigenvalue is not positive")

cka = {r: as_float(by_regime[r], "CKA_hardware_vs_statevector") for r in by_regime}
kta = {r: as_float(by_regime[r], "KTA_hardware") for r in by_regime}
kta_sv = as_float(by_regime["H0"], "KTA_statevector")
delta_kta = {r: kta[r] - kta_sv for r in kta}
rmse = {r: as_float(by_regime[r], "kernel_rmse") for r in by_regime}

if not (cka["H2"] > cka["H1"] > cka["H0"]):
    raise SystemExit("ERROR: CKA ordering is not H2 > H1 > H0")
if not (kta["H0"] > kta["H1"] > kta["H2"]):
    raise SystemExit("ERROR: hardware centered-KTA ordering is not H0 > H1 > H2")
if not all(delta_kta[r] > 0 for r in delta_kta):
    raise SystemExit("ERROR: not all hardware centered-KTA uplifts are positive")
if not (delta_kta["H2"] < delta_kta["H1"] < delta_kta["H0"]):
    raise SystemExit("ERROR: KTA uplift ordering is not H2 < H1 < H0")
if not (rmse["H2"] < rmse["H1"] and rmse["H2"] < rmse["H0"]):
    raise SystemExit("ERROR: H2 does not have the smallest RMSE")

# Shot-noise reference-scale decomposition for RQ3.
shot = read_csv("hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv")
if len(shot) != 3:
    raise SystemExit(f"ERROR: expected 3 shot-noise rows, found {len(shot)}")
shot_by = {row["regime_id"]: row for row in shot}
if set(shot_by) != {"H0", "H1", "H2"}:
    raise SystemExit(f"ERROR: shot-noise regimes are {sorted(shot_by)}")

expected_shot = {
    "H0": dict(rmse=0.0877704676366643, sigma_global=0.0220970869120796, residual_global=0.0849433560624887, share_global=0.0633830630638512, sigma_matrix=0.00826560716139045, residual_matrix=0.087380402421895, share_matrix=0.00886855159564847),
    "H1": dict(rmse=0.0864275383627636, sigma_global=0.0220970869120796, residual_global=0.0835550006728919, share_global=0.065368084753032, sigma_matrix=0.00824329813608937, residual_matrix=0.0860335249962857, share_matrix=0.00909699021286519),
    "H2": dict(rmse=0.0427274195046584, sigma_global=0.0220970869120796, residual_global=0.0365698116966312, share_global=0.267458693223555, sigma_matrix=0.00852828370583245, residual_matrix=0.0418676576196937, share_matrix=0.0398391395017253),
}
for regime, exp in expected_shot.items():
    row = shot_by[regime]
    if row.get("decomposition_policy") != "diagnostic_quadrature_reference_not_physical_noise_model":
        raise SystemExit(f"ERROR: unexpected decomposition policy for {regime}")
    if int(float(row["n"])) != 24 or int(float(row["shots_observed_per_entry"])) != 1024:
        raise SystemExit(f"ERROR: {regime} shot table n/shots mismatch")
    if int(float(row["omega_size_directed"])) != 552 or int(float(row["omega_size_unique_unordered"])) != 276:
        raise SystemExit(f"ERROR: {regime} omega sizes mismatch")
    assert_close(f"{regime} shot RMSE", as_float(row, "kernel_rmse"), exp["rmse"])
    assert_close(f"{regime} sigma_global", as_float(row, "sigma_shot_global"), exp["sigma_global"])
    assert_close(f"{regime} residual_global", as_float(row, "residual_global"), exp["residual_global"])
    assert_close(f"{regime} share_global", as_float(row, "shot_share_global"), exp["share_global"])
    assert_close(f"{regime} sigma_matrix", as_float(row, "sigma_shot_matrix"), exp["sigma_matrix"])
    assert_close(f"{regime} residual_matrix", as_float(row, "residual_matrix"), exp["residual_matrix"])
    assert_close(f"{regime} share_matrix", as_float(row, "shot_share_matrix"), exp["share_matrix"])
    if as_float(row, "kernel_rmse") <= as_float(row, "sigma_shot_global"):
        raise SystemExit(f"ERROR: {regime} RMSE does not exceed global finite-shot reference")
    if as_float(row, "kernel_rmse") <= as_float(row, "sigma_shot_matrix"):
        raise SystemExit(f"ERROR: {regime} RMSE does not exceed matrix-aware finite-shot reference")
    if as_float(row, "shot_share_matrix") >= 0.05:
        raise SystemExit(f"ERROR: {regime} matrix-aware shot share is not below 5%")

sigma_expected = 1.0 / math.sqrt(2.0 * 1024.0)
assert_close("global reference formula", as_float(shot_by["H0"], "sigma_shot_global"), sigma_expected, tol=1e-15)
if not (as_float(shot_by["H2"], "shot_share_global") > as_float(shot_by["H1"], "shot_share_global") > as_float(shot_by["H0"], "shot_share_global")):
    raise SystemExit("ERROR: global shot-share ordering does not reflect H2's smaller RMSE scale")

# Jackknife/diagonal support: KTA contrasts are not window-resolved, while CKA
# H2 contrasts are resolved as already reported in Section 3.3.
unc = read_csv("hardware_analysis/zz4_wave1_distortion_uncertainty.csv")
contrast_rows = [r for r in unc if r.get("analysis_block") == "paired_jackknife_contrast"]
if not contrast_rows:
    raise SystemExit("ERROR: no paired_jackknife_contrast rows found")

def find_contrast(metric, contrast):
    for row in contrast_rows:
        if row.get("metric") == metric and row.get("contrast") == contrast:
            return row
    raise SystemExit(f"ERROR: missing contrast row for {metric} {contrast}")

for contrast in ["M1-M0", "M2-M1", "M2-M0"]:
    row = find_contrast("kta_centered", contrast)
    if abs(as_float(row, "z_descriptive")) >= 1.0:
        raise SystemExit(f"ERROR: KTA contrast {contrast} unexpectedly window-resolved")
for contrast in ["M2-M1", "M2-M0"]:
    row = find_contrast("cka", contrast)
    if abs(as_float(row, "z_descriptive")) <= 2.0:
        raise SystemExit(f"ERROR: CKA contrast {contrast} not resolved as expected")

kta_diag = [r for r in unc if r.get("analysis_block") == "diagonal_robustness" and r.get("metric") == "kta_centered"]
if len(kta_diag) != 3:
    raise SystemExit("ERROR: expected 3 diagonal robustness rows for kta_centered")
by_diag = {r["artifact_regime"]: as_float(r, "delta") for r in kta_diag}
if not (0 < by_diag["H0"] < 0.004 and 0 < by_diag["H1"] < 0.004 and 0 < by_diag["H2"] < 0.004):
    raise SystemExit("ERROR: unit-diagonal KTA sensitivity is not small and positive for all regimes")

# Label-permutation reference: statevector label alignment is below the random-label reference.
perm = read_csv("hardware_analysis/zz4_wave1_label_permutation_reference.csv")
if len(perm) != 2:
    raise SystemExit(f"ERROR: expected two label-permutation rows, found {len(perm)}")
centered = [r for r in perm if r.get("metric") == "CKA" and r.get("alignment_convention") == "centered_label_alignment"]
if len(centered) != 1:
    raise SystemExit("ERROR: missing centered label-alignment permutation row")
row = centered[0]
assert_close("permutation observed centered KTA", as_float(row, "observed"), 0.15851109235208113)
assert_close("permutation null mean", as_float(row, "null_mean"), 0.17097863873640975)
assert_close("permutation p_upper_tail", as_float(row, "p_upper_tail"), 0.5988, tol=1e-12)
if not (as_float(row, "observed") < as_float(row, "null_mean") < as_float(row, "null_q95") < as_float(row, "null_q99")):
    raise SystemExit("ERROR: centered label alignment is not below the null reference as expected")
if row.get("n_perm") != "5000" or row.get("n_rows") != "24":
    raise SystemExit("ERROR: permutation reference n_perm/n_rows mismatch")

with open(root / "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json") as fh:
    shot_json = json.load(fh)
if shot_json.get("caveat", "").lower().find("diagnostic") < 0:
    raise SystemExit("ERROR: shot-noise JSON caveat does not mark the decomposition as diagnostic")
if shot_json.get("matrix_reference_scale", {}).get("domain", "").find("off-diagonal") < 0:
    raise SystemExit("ERROR: shot-noise JSON does not record the off-diagonal matrix-reference domain")

print("Section 3.4 support verification passed.")
print("  CKA ordering: H2 > H1 > H0")
print("  Hardware KTA ordering: H0 > H1 > H2")
print("  KTA uplift ordering: H2 < H1 < H0")
print("  RMSE exceeds both finite-shot reference scales in all regimes")
print("  Matrix-aware shot share < 5% in all regimes")
print("  Statevector label alignment remains below random-label reference")
PY

# Run the supported script-level check unless explicitly disabled. This validates
# the decomposition against the package's maintained reproduction script.
if [[ "${SKIP_SECTION3_4_SCRIPT_CHECKS:-0}" != "1" ]]; then
  ${PYTHON_BIN:-python} scripts/09d_shot_noise_reference_scale_decomposition.py --project-root "${REPO}" --check
  ${PYTHON_BIN:-python} scripts/09e_label_permutation_reference.py --project-root "${REPO}" --check
fi

echo "All Section 3.4 checks passed for: ${REPO}"
