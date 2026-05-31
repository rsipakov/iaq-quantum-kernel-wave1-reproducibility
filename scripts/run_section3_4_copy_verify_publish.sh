#!/usr/bin/env bash
set -euo pipefail

SOURCE=${1:-${SOURCE:-"/Users/rostyslavsipakov/Documents/GitHub/QuantumKernel/duplicate-sensor-monitoring/notebooks"}}
REPO=${2:-${REPO:-"/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility"}}
COMMIT_MSG=${3:-"Add Section 3.4 KTA/CKA tension support"}

if [[ ! -d "${REPO}" ]]; then
  echo "ERROR: reproducibility repository directory does not exist: ${REPO}" >&2
  exit 2
fi

cd "${REPO}"

bash scripts/copy_section3_4_support_files.sh "${SOURCE}" "${REPO}"

# Regenerate/check the numerical artifacts used by Section 3.4. The 09d and 09e
# check modes are intentionally included because Section 3.4 uses both the
# shot-noise decomposition and the label-permutation reference.
${PYTHON_BIN:-python} scripts/09b_analyze_wave1_distortion_direct.py --project-root "${REPO}"
${PYTHON_BIN:-python} scripts/09c_wave1_distortion_uncertainty.py --project-root "${REPO}"
${PYTHON_BIN:-python} scripts/09d_shot_noise_reference_scale_decomposition.py --project-root "${REPO}" --check
${PYTHON_BIN:-python} scripts/09e_label_permutation_reference.py --project-root "${REPO}" --check

bash scripts/verify_section3_4_support_files.sh "${REPO}"
bash scripts/publish_section3_4_updates.sh "${REPO}" "${COMMIT_MSG}"
