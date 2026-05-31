#!/usr/bin/env bash
set -euo pipefail

REPRO="${1:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"
COMMIT_MESSAGE="${2:-Add Section 3.3 statistical diagnostics support}"

if [[ ! -d "$REPRO/.git" ]]; then
  echo "ERROR: REPRO is not a git repository: $REPRO" >&2
  exit 1
fi

cd "$REPRO"

bash scripts/verify_section3_3_support_files.sh "$REPRO"

mkdir -p checksums
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
  ! -path './checksums/SHA256SUMS.txt' \
  -print0 \
| sort -z \
| while IFS= read -r -d '' f; do
    if command -v sha256sum >/dev/null 2>&1; then
      sha256sum "$f"
    else
      shasum -a 256 "$f"
    fi
  done > checksums/SHA256SUMS.txt

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -c checksums/SHA256SUMS.txt
else
  shasum -a 256 -c checksums/SHA256SUMS.txt
fi

git status --short

git add \
  README.md \
  MANIFEST.md \
  checksums/SHA256SUMS.txt \
  frozen_subset/hardware_subset_event_onset_next_1h.csv \
  statevector_reference/zz4_K_all_all.npy \
  hardware_kernels/zz4_H0_kernel.npy \
  hardware_kernels/zz4_H1_kernel.npy \
  hardware_kernels/zz4_H2_kernel.npy \
  hardware_analysis/zz4_wave1_distortion_metrics.csv \
  hardware_analysis/zz4_wave1_distortion_uncertainty.csv \
  hardware_analysis/zz4_wave1_distortion_uncertainty.json \
  hardware_analysis/qiskit_kta_cka_permutation_tests.csv \
  hardware_analysis/zz4_wave1_label_permutation_reference.csv \
  hardware_analysis/zz4_wave1_label_permutation_reference.json \
  scripts/09c_wave1_distortion_uncertainty.py \
  scripts/09e_label_permutation_reference.py \
  scripts/copy_section3_3_support_files.sh \
  scripts/verify_section3_3_support_files.sh \
  scripts/publish_section3_3_updates.sh \
  scripts/run_section3_3_copy_verify_publish.sh

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

git commit -m "$COMMIT_MESSAGE"
git push
