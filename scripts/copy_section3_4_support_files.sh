#!/usr/bin/env bash
set -euo pipefail

# Idempotently copy Section 3.4 support files from the upstream source tree into
# the flat reproducibility repository. This script copies only repository
# artifacts required to support Section 3.4. It deliberately does not copy
# Section 3.4 manuscript drafts into the reproducibility repository.

SOURCE=${1:-${SOURCE:-}}
REPRO=${2:-${REPRO:-}}

if [[ -z "${SOURCE}" || -z "${REPRO}" ]]; then
  cat >&2 <<'USAGE'
Usage:
  bash scripts/copy_section3_4_support_files.sh SOURCE REPRO

Example:
  SOURCE="/Users/rostyslavsipakov/Documents/GitHub/QuantumKernel/duplicate-sensor-monitoring/notebooks"
  REPRO="/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility"
  bash scripts/copy_section3_4_support_files.sh "$SOURCE" "$REPRO"
USAGE
  exit 2
fi

if [[ ! -d "${SOURCE}" ]]; then
  echo "ERROR: SOURCE directory does not exist: ${SOURCE}" >&2
  exit 2
fi
if [[ ! -d "${REPRO}" ]]; then
  echo "ERROR: REPRO directory does not exist: ${REPRO}" >&2
  exit 2
fi

# Required support inputs/outputs for Section 3.4. Most of these should already
# exist after Sections 3.1--3.3 and 2.12 support updates; the copy operation is
# still useful as a consistency refresh when the upstream tree has missing or
# changed artifacts.
FILES=(
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

copied=0
skipped=0
missing_source_but_present=0

copy_one() {
  local rel="$1"
  local src="${SOURCE}/${rel}"
  local dst="${REPRO}/${rel}"

  if [[ ! -f "${src}" ]]; then
    if [[ -f "${dst}" ]]; then
      echo "source missing; target already present, keeping: ${rel}"
      missing_source_but_present=$((missing_source_but_present + 1))
      return 0
    fi
    echo "ERROR: missing required source and target file: ${rel}" >&2
    echo "       source: ${src}" >&2
    echo "       target: ${dst}" >&2
    exit 1
  fi

  mkdir -p "$(dirname "${dst}")"
  if [[ -f "${dst}" ]] && cmp -s "${src}" "${dst}"; then
    echo "unchanged: ${rel}"
    skipped=$((skipped + 1))
  else
    cp "${src}" "${dst}"
    echo "copied: ${rel}"
    copied=$((copied + 1))
  fi
}

for rel in "${FILES[@]}"; do
  copy_one "${rel}"
done

for draft in \
  "${REPRO}/NewSection_3.4.md" \
  "${REPRO}"/NewSection_3.4_Revised*.md \
  "${REPRO}"/NewSection_3.4_*Instructions.md
do
  if [[ -e "${draft}" ]]; then
    echo "ERROR: ${draft} exists, but manuscript draft files must not be copied into the reproducibility repository." >&2
    exit 1
  fi
done

cat <<SUMMARY
Section 3.4 copy refresh complete.
  copied: ${copied}
  unchanged: ${skipped}
  source-missing but target-present: ${missing_source_but_present}
SUMMARY
