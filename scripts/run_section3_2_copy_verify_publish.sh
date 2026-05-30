#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-/Users/rostyslavsipakov/Documents/GitHub/QuantumKernel/duplicate-sensor-monitoring/notebooks}"
REPRO="${2:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"
COMMIT_MESSAGE="${3:-Add Section 3.2 main distortion metrics support}"

bash "$REPRO/scripts/copy_section3_2_support_files.sh" "$SOURCE" "$REPRO"
python "$REPRO/scripts/09b_analyze_wave1_distortion_direct.py" --project-root "$REPRO"
bash "$REPRO/scripts/verify_section3_2_support_files.sh" "$REPRO"
bash "$REPRO/scripts/publish_section3_2_updates.sh" "$REPRO" "$COMMIT_MESSAGE"
