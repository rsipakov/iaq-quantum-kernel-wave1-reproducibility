#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-/Users/rostyslavsipakov/Documents/GitHub/QuantumKernel/duplicate-sensor-monitoring/notebooks}"
REPRO="${2:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"

if [[ ! -d "$SOURCE" ]]; then
  echo "ERROR: SOURCE does not exist: $SOURCE" >&2
  exit 1
fi
if [[ ! -d "$REPRO" ]]; then
  echo "ERROR: REPRO does not exist: $REPRO" >&2
  exit 1
fi

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

copy_if_needed() {
  local src_rel="$1"
  local dst_rel="$2"
  local src="$SOURCE/$src_rel"
  local dst="$REPRO/$dst_rel"

  if [[ ! -f "$src" ]]; then
    echo "MISSING_SOURCE $src_rel" >&2
    return 1
  fi

  mkdir -p "$(dirname "$dst")"

  if [[ -f "$dst" ]]; then
    local src_hash dst_hash
    src_hash="$(hash_file "$src")"
    dst_hash="$(hash_file "$dst")"
    if [[ "$src_hash" == "$dst_hash" ]]; then
      echo "SKIP_IDENTICAL $dst_rel"
      return 0
    fi
    echo "UPDATE $dst_rel"
  else
    echo "COPY $dst_rel"
  fi

  cp "$src" "$dst"
}

# Section 3.2 support inputs. Source paths use the upstream step6b/step9 layouts;
# destination paths use the flat dedicated reproducibility-repository layout.
# The main metrics CSV is not copied from the historical source table by default;
# it is generated in the public package by scripts/09b_analyze_wave1_distortion_direct.py
# so that unsupported correlation p-values remain blank/NaN in the curated workflow.
# Keep the in-package analysis script local: the upstream copy may use the
# source repository's nested step6b/step9 layout and would break this flat
# reproducibility package if it overwrote the curated script.
declare -a MAP=(
  "step6b_hardware_subset_package/outputs/subsets/hardware_subset_event_onset_next_1h.csv::frozen_subset/hardware_subset_event_onset_next_1h.csv"
  "step6b_hardware_subset_package/outputs/statevector_reference/zz4_K_all_all.npy::statevector_reference/zz4_K_all_all.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H0_kernel.npy::hardware_kernels/zz4_H0_kernel.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H1_kernel.npy::hardware_kernels/zz4_H1_kernel.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H2_kernel.npy::hardware_kernels/zz4_H2_kernel.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H0_kernel.csv::hardware_kernels/zz4_H0_kernel.csv"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H1_kernel.csv::hardware_kernels/zz4_H1_kernel.csv"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H2_kernel.csv::hardware_kernels/zz4_H2_kernel.csv"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_wave1_kernel_entries_long.csv::hardware_kernels/zz4_wave1_kernel_entries_long.csv"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_kernel_manifest.json::metadata/zz4_wave1_kernel_manifest.json"
)

fail=0
for item in "${MAP[@]}"; do
  src_rel="${item%%::*}"
  dst_rel="${item##*::}"
  if ! copy_if_needed "$src_rel" "$dst_rel"; then
    fail=1
  fi
done

if [[ -e "$REPRO/NewSection_3.2.md" ]]; then
  echo "ERROR: NewSection_3.2.md must not be copied into the reproducibility repository root." >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "One or more Section 3.2 support files could not be copied." >&2
  exit 1
fi

cat <<MSG
Section 3.2 support-file copy completed.

Recommended next steps from the repository root:
  python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
  bash scripts/verify_section3_2_support_files.sh .
MSG
