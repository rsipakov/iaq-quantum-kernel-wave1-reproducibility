#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-/Users/rostyslavsipakov/Documents/GitHub/QuantumKernel/duplicate-sensor-monitoring/notebooks}"
REPRO="${2:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"
COMMIT_MESSAGE="${3:-Add Section 3.1 hardware execution summary support}"

cd "$REPRO"

bash scripts/copy_section3_1_support_files.sh "$SOURCE" "$REPRO"
bash scripts/verify_section3_1_support_files.sh "$REPRO"
bash scripts/publish_section3_1_updates.sh "$REPRO" "$COMMIT_MESSAGE"
