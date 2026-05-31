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
    if [[ -f "$dst" ]]; then
      echo "KEEP_EXISTING_SOURCE_MISSING $dst_rel (source candidate missing: $src_rel)"
      return 0
    fi
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

copy_from_candidates() {
  local dst_rel="$1"
  shift
  local dst="$REPRO/$dst_rel"
  local candidate

  for candidate in "$@"; do
    if [[ -f "$SOURCE/$candidate" ]]; then
      copy_if_needed "$candidate" "$dst_rel"
      return $?
    fi
  done

  if [[ -f "$dst" ]]; then
    echo "KEEP_EXISTING_NO_SOURCE_CANDIDATE $dst_rel"
    return 0
  fi

  echo "MISSING_SOURCE_CANDIDATES for $dst_rel" >&2
  printf '  %s\n' "$@" >&2
  return 1
}

# Section 3.3 support inputs. Outputs are regenerated in the reproducibility
# repository by scripts/09b, 09c, and 09e; manuscript draft NewSection_3.3.md
# must not be copied into the repository.
declare -a MAP=(
  "step6b_hardware_subset_package/outputs/subsets/hardware_subset_event_onset_next_1h.csv::frozen_subset/hardware_subset_event_onset_next_1h.csv"
  "step6b_hardware_subset_package/outputs/statevector_reference/zz4_K_all_all.npy::statevector_reference/zz4_K_all_all.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H0_kernel.npy::hardware_kernels/zz4_H0_kernel.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H1_kernel.npy::hardware_kernels/zz4_H1_kernel.npy"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_H2_kernel.npy::hardware_kernels/zz4_H2_kernel.npy"
)

fail=0
for item in "${MAP[@]}"; do
  src_rel="${item%%::*}"
  dst_rel="${item##*::}"
  if ! copy_if_needed "$src_rel" "$dst_rel"; then
    fail=1
  fi
done

# Static source-derived permutation table retained for provenance. The fixed-seed
# manuscript reference is generated in-package by scripts/09e_label_permutation_reference.py.
if ! copy_from_candidates \
  "hardware_analysis/qiskit_kta_cka_permutation_tests.csv" \
  "step6_v6_consolidation/outputs/tables/qiskit_kta_cka_permutation_tests.csv" \
  "step6b_hardware_subset_package/outputs/analysis/qiskit_kta_cka_permutation_tests.csv" \
  "step6b_hardware_subset_package/outputs/tables/qiskit_kta_cka_permutation_tests.csv"; then
  fail=1
fi

if [[ -e "$REPRO/NewSection_3.3.md" ]]; then
  echo "ERROR: NewSection_3.3.md must not be copied into the reproducibility repository root." >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "One or more Section 3.3 support files could not be copied." >&2
  exit 1
fi

cat <<MSG
Section 3.3 support-file copy completed.

Recommended next steps from the repository root:
  python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
  python scripts/09c_wave1_distortion_uncertainty.py --project-root .
  python scripts/09e_label_permutation_reference.py --project-root .
  python scripts/09e_label_permutation_reference.py --project-root . --check
  bash scripts/verify_section3_3_support_files.sh .
MSG
