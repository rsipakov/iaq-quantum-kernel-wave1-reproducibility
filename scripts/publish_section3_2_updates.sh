#!/usr/bin/env bash
set -euo pipefail

REPRO="${1:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"
COMMIT_MESSAGE="${2:-Add Section 3.2 main distortion metrics support}"

if [[ ! -d "$REPRO/.git" ]]; then
  echo "ERROR: REPRO is not a git repository: $REPRO" >&2
  exit 1
fi

cd "$REPRO"

bash scripts/verify_section3_2_support_files.sh "$REPRO"

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
  hardware_analysis/zz4_wave1_distortion_metrics.csv \
  hardware_analysis/zz4_wave1_distortion_summary.json \
  hardware_analysis/zz4_wave1_distortion_summary.md \
  scripts/copy_section3_2_support_files.sh \
  scripts/verify_section3_2_support_files.sh \
  scripts/publish_section3_2_updates.sh \
  scripts/run_section3_2_copy_verify_publish.sh

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

git commit -m "$COMMIT_MESSAGE"
git push
