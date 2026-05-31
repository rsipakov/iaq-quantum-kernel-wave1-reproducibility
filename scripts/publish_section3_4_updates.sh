#!/usr/bin/env bash
set -euo pipefail

REPO=${1:-${REPO:-.}}
COMMIT_MSG=${2:-"Add Section 3.4 KTA/CKA tension support"}

if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: repository directory does not exist: ${REPO}" >&2
  exit 2
fi
REPO=$(cd "${REPO}" && pwd)
cd "${REPO}"

if [[ -e "NewSection_3.4.md" ]]; then
  echo "ERROR: NewSection_3.4.md must remain outside the reproducibility repository." >&2
  exit 1
fi

bash scripts/verify_section3_4_support_files.sh "${REPO}"

mkdir -p checksums
if command -v shasum >/dev/null 2>&1; then
  HASH_CMD=(shasum -a 256)
elif command -v sha256sum >/dev/null 2>&1; then
  HASH_CMD=(sha256sum)
else
  echo "ERROR: neither shasum nor sha256sum is available" >&2
  exit 1
fi

find . \
  -type f \
  ! -path './.git/*' \
  ! -path './.idea/*' \
  ! -path './.venv/*' \
  ! -path './venv/*' \
  ! -path './__pycache__/*' \
  ! -path '*/__pycache__/*' \
  ! -name '.DS_Store' \
  ! -name '*_provenance.json' \
  ! -name 'NewSection_3.4.md' \
  ! -path './checksums/SHA256SUMS.txt' \
  -print0 \
  | sort -z \
  | xargs -0 "${HASH_CMD[@]}" \
  > checksums/SHA256SUMS.txt

"${HASH_CMD[@]}" -c checksums/SHA256SUMS.txt

git status --short

git add \
  README.md \
  MANIFEST.md \
  checksums/SHA256SUMS.txt \
  scripts/copy_section3_4_support_files.sh \
  scripts/verify_section3_4_support_files.sh \
  scripts/publish_section3_4_updates.sh \
  scripts/run_section3_4_copy_verify_publish.sh \
  hardware_analysis/zz4_wave1_distortion_metrics.csv \
  hardware_analysis/zz4_wave1_distortion_uncertainty.csv \
  hardware_analysis/zz4_wave1_distortion_uncertainty.json \
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv \
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json \
  hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md \
  hardware_analysis/zz4_wave1_label_permutation_reference.csv \
  hardware_analysis/zz4_wave1_label_permutation_reference.json \
  hardware_analysis/qiskit_kta_cka_permutation_tests.csv \
  hardware_kernels/zz4_wave1_kernel_entries_long.csv \
  hardware_kernels/zz4_H0_kernel.csv \
  hardware_kernels/zz4_H1_kernel.csv \
  hardware_kernels/zz4_H2_kernel.csv \
  hardware_kernels/zz4_H0_kernel.npy \
  hardware_kernels/zz4_H1_kernel.npy \
  hardware_kernels/zz4_H2_kernel.npy \
  statevector_reference/zz4_K_all_all.npy \
  frozen_subset/hardware_subset_event_onset_next_1h.csv

if git diff --cached --quiet; then
  echo "No staged changes to commit. Repository already contains Section 3.4 support state."
else
  git commit -m "${COMMIT_MSG}"
fi

git push
