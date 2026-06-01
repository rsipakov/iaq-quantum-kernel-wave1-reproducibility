#!/usr/bin/env bash
set -euo pipefail

REPO=${1:-${REPO:-.}}
if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: repository directory does not exist: ${REPO}" >&2
  exit 2
fi
REPO=$(cd "${REPO}" && pwd)
cd "${REPO}"

# Manuscript draft and local transfer bundles should not be committed to the reproducibility root.
for draft in \
  NewSection_3.6.md \
  NewSection_3.6_*.md \
  section3_6_artifacts.zip; do
  if [[ -e "${draft}" ]]; then
    echo "ERROR: ${draft} is manuscript/local material and must not be committed to the reproducibility repository root." >&2
    exit 1
  fi
done

required_files=(
  "config/wave1_scope.json"
  "metadata/zz4_wave1_runtime_options.json"
  "metadata/zz_only_step8_execution_manifest.json"
  "job_metadata/zz4_wave1_job_manifest.json"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv"
  "hardware_analysis/zz4_wave1_4096_shot_projection.csv"
  "hardware_analysis/zz4_wave1_4096_shot_projection.json"
  "hardware_analysis/zz4_wave1_4096_shot_projection.md"
  "scripts/09j_optional_4096_shot_projection.py"
  "README.md"
  "MANIFEST.md"
)

for f in "${required_files[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: required Section 3.6 support file is missing: ${f}" >&2
    exit 1
  fi
done

"${PYTHON_BIN:-python}" scripts/09j_optional_4096_shot_projection.py --project-root . --check

"${PYTHON_BIN:-python}" - <<'PY'
import csv
import json
import math
from pathlib import Path

root = Path.cwd()

def assert_close(name, got, exp, tol=5e-12):
    if not math.isfinite(got) or abs(got - exp) > tol:
        raise SystemExit(f"ERROR: {name}: got {got!r}, expected {exp!r}")

with open(root / "hardware_analysis/zz4_wave1_4096_shot_projection.csv", newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
if len(rows) != 3:
    raise SystemExit(f"ERROR: expected 3 projection rows, observed {len(rows)}")
by = {r["regime_id"]: r for r in rows}
if set(by) != {"H0", "H1", "H2"}:
    raise SystemExit(f"ERROR: unexpected projection regimes: {sorted(by)}")

expected = {
    "H0": {
        "config": "M0",
        "rmse": 0.0877704676366643,
        "sigma_g": 0.011048543456039804,
        "share_g": 0.015845765765962794,
        "frac_g": 0.9841542342340373,
        "sigma_m": 0.004132803580695225,
        "share_m": 0.002217137898912121,
        "frac_m": 0.9977828621010879,
        "R_m": 21.237512483450626,
    },
    "H1": {
        "config": "M1",
        "rmse": 0.0864275383627636,
        "sigma_g": 0.011048543456039804,
        "share_g": 0.016342021188257998,
        "frac_g": 0.983657978811742,
        "sigma_m": 0.004121649068044685,
        "share_m": 0.0022742475532162984,
        "frac_m": 0.9977257524467837,
        "R_m": 20.969164753214887,
    },
    "H2": {
        "config": "M2",
        "rmse": 0.0427274195046584,
        "sigma_g": 0.011048543456039804,
        "share_g": 0.06686467330588872,
        "frac_g": 0.9331353266941113,
        "sigma_m": 0.004264141852916225,
        "share_m": 0.00995978487543135,
        "frac_m": 0.9900402151245686,
        "R_m": 10.02016841335551,
    },
}

for regime, exp in expected.items():
    row = by[regime]
    if row["manuscript_configuration"] != exp["config"]:
        raise SystemExit(f"ERROR: manuscript config mismatch for {regime}")
    if row["projection_policy"] != "fixed_RMSE_shot_reference_rescaled_only_no_new_hardware_kernel":
        raise SystemExit(f"ERROR: projection policy mismatch for {regime}")
    if int(float(row["shots_observed_per_entry"])) != 1024:
        raise SystemExit(f"ERROR: observed shot count mismatch for {regime}")
    if int(float(row["shots_projected_per_entry"])) != 4096:
        raise SystemExit(f"ERROR: projected shot count mismatch for {regime}")
    assert_close(f"{regime} RMSE", float(row["kernel_rmse_fixed"]), exp["rmse"])
    assert_close(f"{regime} sigma_global_4096", float(row["sigma_shot_global_projected"]), exp["sigma_g"])
    assert_close(f"{regime} global share 4096", float(row["shot_share_global_projected"]), exp["share_g"])
    assert_close(f"{regime} global residual fraction 4096", float(row["residual_fraction_global_projected"]), exp["frac_g"])
    assert_close(f"{regime} sigma_matrix_4096", float(row["sigma_shot_matrix_projected"]), exp["sigma_m"])
    assert_close(f"{regime} matrix share 4096", float(row["shot_share_matrix_projected"]), exp["share_m"])
    assert_close(f"{regime} matrix residual fraction 4096", float(row["residual_fraction_matrix_projected"]), exp["frac_m"])
    assert_close(f"{regime} R_matrix 4096", float(row["R_matrix_projected"]), exp["R_m"])

if not (float(by["H2"]["kernel_rmse_fixed"]) < float(by["H1"]["kernel_rmse_fixed"]) < float(by["H0"]["kernel_rmse_fixed"])):
    raise SystemExit("ERROR: fixed RMSE ordering changed")
if not all(float(row["shot_share_matrix_projected"]) <= 0.01 + 1e-12 for row in rows):
    raise SystemExit("ERROR: projected matrix-aware shot share is above 1%")
if not all(float(row["residual_fraction_global_projected"]) > 0.93 for row in rows):
    raise SystemExit("ERROR: projected global residual fraction is not above 93% for every regime")
if not all(float(row["residual_fraction_matrix_projected"]) >= 0.99 - 1e-12 for row in rows):
    raise SystemExit("ERROR: projected matrix-aware residual fraction is not at least 99% for every regime")

with open(root / "config/wave1_scope.json", encoding="utf-8") as fh:
    scope = json.load(fh)
if scope.get("shots_planned_per_circuit") != 4096:
    raise SystemExit("ERROR: wave1_scope planned shots are not 4096")
if scope.get("claims_policy", {}).get("allowed_interpretation") != "kernel-survival / hardware-distortion only":
    raise SystemExit("ERROR: claims-policy boundary changed")

with open(root / "job_metadata/zz4_wave1_job_manifest.json", encoding="utf-8") as fh:
    jobs = json.load(fh)
if jobs.get("shots_submitted_per_circuit") != [1024]:
    raise SystemExit("ERROR: job manifest no longer records the 1024-shot budget-safe execution")
if jobs.get("budget_safe_partial_submission") is not True:
    raise SystemExit("ERROR: job manifest does not record budget_safe_partial_submission=true")

print("[section3.6] projection value and scope checks passed")
PY

grep -q "Section 3.6" README.md
grep -q "3.6. Optional projection: 4096-shot rerun" MANIFEST.md
grep -q "zz4_wave1_4096_shot_projection" README.md
grep -q "zz4_wave1_4096_shot_projection" MANIFEST.md

echo "[section3.6] support files:"
ls -lh \
  hardware_analysis/zz4_wave1_4096_shot_projection.csv \
  hardware_analysis/zz4_wave1_4096_shot_projection.json \
  hardware_analysis/zz4_wave1_4096_shot_projection.md \
  scripts/09j_optional_4096_shot_projection.py

echo "[section3.6] projection CSV:"
head -n 6 hardware_analysis/zz4_wave1_4096_shot_projection.csv

echo "[section3.6] SHA-256 checks:"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum \
    hardware_analysis/zz4_wave1_4096_shot_projection.csv \
    hardware_analysis/zz4_wave1_4096_shot_projection.json \
    hardware_analysis/zz4_wave1_4096_shot_projection.md \
    scripts/09j_optional_4096_shot_projection.py
else
  shasum -a 256 \
    hardware_analysis/zz4_wave1_4096_shot_projection.csv \
    hardware_analysis/zz4_wave1_4096_shot_projection.json \
    hardware_analysis/zz4_wave1_4096_shot_projection.md \
    scripts/09j_optional_4096_shot_projection.py
fi
