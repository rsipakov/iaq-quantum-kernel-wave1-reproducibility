#!/usr/bin/env bash
set -euo pipefail

REPO=${1:-${REPO:-.}}
if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: repository directory does not exist: ${REPO}" >&2
  exit 2
fi
REPO=$(cd "${REPO}" && pwd)
cd "${REPO}"

# Manuscript drafts and local transfer helpers should not be committed to the
# reproducibility repository root.
for draft in \
  NewSection_3.5.md \
  NewSection_3.5_*.md \
  copy_section3_5_support_files.sh \
  publish_section3_5_updates.sh \
  run_section3_5_update_all.sh; do
  if [[ -e "${draft}" ]]; then
    echo "ERROR: ${draft} is local manuscript/transfer material and must not be committed to the reproducibility repository root." >&2
    exit 1
  fi
done

required_files=(
  "hardware_analysis/zz4_wave1_distortion_metrics.csv"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json"
  "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md"
  "hardware_kernels/zz4_wave1_kernel_entries_long.csv"
  "hardware_kernels/zz4_H0_kernel.csv"
  "hardware_kernels/zz4_H1_kernel.csv"
  "hardware_kernels/zz4_H2_kernel.csv"
  "scripts/09d_shot_noise_reference_scale_decomposition.py"
  "README.md"
  "MANIFEST.md"
)

for f in "${required_files[@]}"; do
  if [[ ! -f "${f}" ]]; then
    echo "ERROR: required Section 3.5 support file is missing: ${f}" >&2
    exit 1
  fi
done

${PYTHON_BIN:-python} scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check

${PYTHON_BIN:-python} - <<'PY'
import csv
import json
import math
from pathlib import Path

root = Path.cwd()

def assert_close(name, got, exp, tol=5e-12):
    if not math.isfinite(got) or abs(got - exp) > tol:
        raise SystemExit(f"ERROR: {name}: got {got!r}, expected {exp!r} within {tol}")

def read_csv(rel):
    with open(root / rel, newline="") as fh:
        return list(csv.DictReader(fh))

def f(row, key):
    try:
        return float(row[key])
    except Exception as exc:
        raise SystemExit(f"ERROR: cannot parse {key!r} from {row}: {exc}")

rows = read_csv("hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv")
if len(rows) != 3:
    raise SystemExit(f"ERROR: expected 3 shot-noise decomposition rows, observed {len(rows)}")
by = {r["regime_id"]: r for r in rows}
if set(by) != {"H0", "H1", "H2"}:
    raise SystemExit(f"ERROR: unexpected regimes: {sorted(by)}")

expected = {
    "H0": dict(
        manuscript_configuration="M0", n=24, shots=1024, omega_directed=552, omega_unique=276,
        rmse=0.0877704676366643,
        sigma_global=0.0220970869120796,
        residual_global=0.0849433560624887,
        shot_share_global=0.0633830630638512,
        sigma_matrix=0.00826560716139045,
        residual_matrix=0.087380402421895,
        shot_share_matrix=0.00886855159564847,
        hardware_offdiag_mean=0.082084324048913,
        hardware_offdiag_variance=0.00538653976600277,
        R_global=3.972037942643184,
        R_matrix=10.618756241725313,
        F_global=0.9366169369361488,
        F_matrix=0.9911314484043515,
    ),
    "H1": dict(
        manuscript_configuration="M1", n=24, shots=1024, omega_directed=552, omega_unique=276,
        rmse=0.0864275383627636,
        sigma_global=0.0220970869120796,
        residual_global=0.0835550006728919,
        shot_share_global=0.065368084753032,
        sigma_matrix=0.00824329813608937,
        residual_matrix=0.0860335249962857,
        shot_share_matrix=0.00909699021286519,
        hardware_offdiag_mean=0.0815111243206522,
        hardware_offdiag_variance=0.00528424963233001,
        R_global=3.911263901284521,
        R_matrix=10.484582376607444,
        F_global=0.934631915246968,
        F_matrix=0.9909030097871349,
    ),
    "H2": dict(
        manuscript_configuration="M2", n=24, shots=1024, omega_directed=552, omega_unique=276,
        rmse=0.0427274195046584,
        sigma_global=0.0220970869120796,
        residual_global=0.0365698116966312,
        shot_share_global=0.267458693223555,
        sigma_matrix=0.00852828370583245,
        residual_matrix=0.0418676576196937,
        shot_share_matrix=0.0398391395017253,
        hardware_offdiag_mean=0.0928583559782609,
        hardware_offdiag_variance=0.00975849978489626,
        R_global=1.9336222767581646,
        R_matrix=5.010084206677755,
        F_global=0.732541306776445,
        F_matrix=0.9601608604982746,
    ),
}

for regime, exp in expected.items():
    row = by[regime]
    if row["manuscript_configuration"] != exp["manuscript_configuration"]:
        raise SystemExit(f"ERROR: {regime} manuscript configuration mismatch")
    if row.get("decomposition_policy") != "diagnostic_quadrature_reference_not_physical_noise_model":
        raise SystemExit(f"ERROR: {regime} decomposition policy mismatch")
    if int(float(row["n"])) != exp["n"]:
        raise SystemExit(f"ERROR: {regime} n mismatch")
    if int(float(row["shots_observed_per_entry"])) != exp["shots"]:
        raise SystemExit(f"ERROR: {regime} shots mismatch")
    if int(float(row["omega_size_directed"])) != exp["omega_directed"]:
        raise SystemExit(f"ERROR: {regime} directed omega size mismatch")
    if int(float(row["omega_size_unique_unordered"])) != exp["omega_unique"]:
        raise SystemExit(f"ERROR: {regime} unique omega size mismatch")

    assert_close(f"{regime} RMSE", f(row, "kernel_rmse"), exp["rmse"])
    assert_close(f"{regime} sigma_global", f(row, "sigma_shot_global"), exp["sigma_global"])
    assert_close(f"{regime} residual_global", f(row, "residual_global"), exp["residual_global"])
    assert_close(f"{regime} shot_share_global", f(row, "shot_share_global"), exp["shot_share_global"])
    assert_close(f"{regime} sigma_matrix", f(row, "sigma_shot_matrix"), exp["sigma_matrix"])
    assert_close(f"{regime} residual_matrix", f(row, "residual_matrix"), exp["residual_matrix"])
    assert_close(f"{regime} shot_share_matrix", f(row, "shot_share_matrix"), exp["shot_share_matrix"])
    assert_close(f"{regime} hardware_offdiag_mean", f(row, "hardware_offdiag_mean"), exp["hardware_offdiag_mean"])
    assert_close(f"{regime} hardware_offdiag_variance", f(row, "hardware_offdiag_variance"), exp["hardware_offdiag_variance"])

    Rg = f(row, "kernel_rmse") / f(row, "sigma_shot_global")
    Rm = f(row, "kernel_rmse") / f(row, "sigma_shot_matrix")
    Fg = 1.0 - f(row, "shot_share_global")
    Fm = 1.0 - f(row, "shot_share_matrix")
    assert_close(f"{regime} R_global", Rg, exp["R_global"])
    assert_close(f"{regime} R_matrix", Rm, exp["R_matrix"])
    assert_close(f"{regime} F_global", Fg, exp["F_global"])
    assert_close(f"{regime} F_matrix", Fm, exp["F_matrix"])

    if f(row, "kernel_rmse") <= f(row, "sigma_shot_global"):
        raise SystemExit(f"ERROR: {regime} RMSE does not exceed the conservative global finite-shot reference")
    if f(row, "kernel_rmse") <= f(row, "sigma_shot_matrix"):
        raise SystemExit(f"ERROR: {regime} RMSE does not exceed the matrix-aware finite-shot reference")

# Diagnostic ordering used in Section 3.5 narrative.
if not (f(by["H2"], "kernel_rmse") < f(by["H1"], "kernel_rmse") < f(by["H0"], "kernel_rmse")):
    raise SystemExit("ERROR: RMSE ordering is not H2 < H1 < H0")
if not (f(by["H2"], "sigma_shot_matrix") > f(by["H0"], "sigma_shot_matrix") > f(by["H1"], "sigma_shot_matrix")):
    raise SystemExit("ERROR: matrix-aware shot-scale ordering changed")
if not all(1.0 - f(row, "shot_share_matrix") > 0.96 for row in rows):
    raise SystemExit("ERROR: matrix-aware residual variance share is not above 96% for every regime")
if not (1.0 - f(by["H2"], "shot_share_global") > 0.73):
    raise SystemExit("ERROR: H2 global residual variance share is not above 73%")

# JSON consistency and declared formulas.
with open(root / "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json", encoding="utf-8") as fh:
    js = json.load(fh)
if js.get("artifact_type") != "zz4_wave1_shot_noise_reference_scale_decomposition":
    raise SystemExit("ERROR: unexpected JSON artifact_type")
if js.get("n") != 24 or js.get("shots_observed_per_entry") != 1024:
    raise SystemExit("ERROR: JSON n/shots mismatch")
if js.get("global_reference_scale", {}).get("formula") != "1/sqrt(2*S)":
    raise SystemExit("ERROR: JSON global reference formula mismatch")
if "not a full physical noise-model decomposition" not in js.get("caveat", ""):
    raise SystemExit("ERROR: JSON caveat does not state diagnostic/non-physical-noise-model scope")

print("[section3.5] shot-noise reference-scale support checks passed")
PY

# Human-readable verification output useful for copy/publish logs.
echo "[section3.5] support files:"
ls -lh \
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv \
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json \
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md \
  scripts/09d_shot_noise_reference_scale_decomposition.py

echo "[section3.5] decomposition CSV head:"
head -n 6 hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv

echo "[section3.5] SHA-256 checks:"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum \
    hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv \
    hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json \
    hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md \
    scripts/09d_shot_noise_reference_scale_decomposition.py
else
  shasum -a 256 \
    hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv \
    hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json \
    hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md \
    scripts/09d_shot_noise_reference_scale_decomposition.py
fi
