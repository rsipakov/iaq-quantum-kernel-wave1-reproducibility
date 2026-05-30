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

# Section 3.1 support artifacts. Source paths use the upstream step6b package layout;
# destination paths use the flat dedicated reproducibility-repository layout.
declare -a MAP=(
  "step6b_hardware_subset_package/outputs/metadata/zz_only_step8_execution_manifest.json::metadata/zz_only_step8_execution_manifest.json"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_runtime_options.json::metadata/zz4_wave1_runtime_options.json"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_runtime_options_sha256.txt::metadata/zz4_wave1_runtime_options_sha256.txt"
  "step6b_hardware_subset_package/outputs/metadata/zz_only_step9_live_backend_metadata.json::metadata/zz_only_step9_live_backend_metadata.json"
  "step6b_hardware_subset_package/outputs/hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json::hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json"
  "step6b_hardware_subset_package/outputs/hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv::hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest.json::job_metadata/zz4_wave1_job_manifest.json"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest.csv::job_metadata/zz4_wave1_job_manifest.csv"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest_H0_1024.json::job_metadata/zz4_wave1_job_manifest_H0_1024.json"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest_H0_1024.csv::job_metadata/zz4_wave1_job_manifest_H0_1024.csv"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest_H1_1024.json::job_metadata/zz4_wave1_job_manifest_H1_1024.json"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest_H1_1024.csv::job_metadata/zz4_wave1_job_manifest_H1_1024.csv"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest_H2_1024.json::job_metadata/zz4_wave1_job_manifest_H2_1024.json"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_job_manifest_H2_1024.csv::job_metadata/zz4_wave1_job_manifest_H2_1024.csv"
  "step6b_hardware_subset_package/outputs/metadata/zz4_wave1_retrieval_manifest.json::job_metadata/zz4_wave1_retrieval_manifest.json"
  "step6b_hardware_subset_package/outputs/logs/zz4_wave1_submission_log.md::logs/zz4_wave1_submission_log.md"
  "step6b_hardware_subset_package/outputs/logs/zz4_wave1_retrieval_log.md::logs/zz4_wave1_retrieval_log.md"
  "step6b_hardware_subset_package/outputs/hardware_results/zz4_H0_raw_results.json::hardware_results/zz4_H0_raw_results.json"
  "step6b_hardware_subset_package/outputs/hardware_results/zz4_H1_raw_results.json::hardware_results/zz4_H1_raw_results.json"
  "step6b_hardware_subset_package/outputs/hardware_results/zz4_H2_raw_results.json::hardware_results/zz4_H2_raw_results.json"
  "step6b_hardware_subset_package/outputs/hardware_kernels/zz4_wave1_kernel_entries_long.csv::hardware_kernels/zz4_wave1_kernel_entries_long.csv"
)

fail=0
for item in "${MAP[@]}"; do
  src_rel="${item%%::*}"
  dst_rel="${item##*::}"
  if ! copy_if_needed "$src_rel" "$dst_rel"; then
    fail=1
  fi
done

if [[ -e "$REPRO/NewSection_3.1.md" ]]; then
  echo "ERROR: NewSection_3.1.md must not be copied into the reproducibility repository root." >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "One or more Section 3.1 support files could not be copied." >&2
  exit 1
fi

echo "Section 3.1 support-file copy completed."
