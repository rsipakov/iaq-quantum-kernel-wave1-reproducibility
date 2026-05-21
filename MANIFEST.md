# Manifest

This manifest lists the curated, non-sensitive artifacts included in the IAQ Quantum Kernel Wave 1 reproducibility package.

The package supports the manuscript subsection "Dataset and prediction context" and the related subsection "Frozen subset".

## Scope

- Domain: real indoor air-quality duplicate-sensor monitoring data
- Prediction target: `event_onset_next_1h` / `y_event_onset_next_1h`
- Feature set: `F_quantum_4`
- Frozen subset: `N=24` fixed observation windows
- Kernel: `ZZ4`
- Hardware scope: Wave 1 / v9 reproduction only
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis

## Frozen subset policy

The reproduction package uses a fixed `N=24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

Within the current Wave 1 / v9 scope, the frozen subset is immutable. No observation window may be added, removed, replaced, reordered, or reweighted after IBM hardware execution authorization.

The current Wave 1 decision-record mechanism does not authorize subset modification. Any future subset modification would require a separate scope-unlock procedure outside the current Wave 1 reproduction scope.

Thresholds used for inclusion, exclusion, hardware feasibility, compile-gate acceptance, subset stability, or pass/fail interpretation are frozen. Post-hoc threshold relaxation is not permitted.

Wave 2 execution is excluded from the current frozen-subset reproduction unless explicitly authorized by a new decision record. Full 300-pair Wave 2 execution is not authorized under the current scope. Any sentinel-only Wave 2 extension must preserve the frozen-subset policy and must not retroactively alter the Wave 1 subset, thresholds, or claims.

## Dataset and preprocessing source files

| Path | Purpose |
|---|---|
| `config/config.py` | Defines allowed targets and compact feature sets, including `F_quantum_4`. |
| `preprocessing/data.py` | Implements dataset loading, valid-label filtering, train-only imputation, train-only scaling to `[0, pi]`, and clipping. |
| `preprocessing/feature_maps.py` | Implements the ZZ feature-map builder used for the `F_quantum_4 / ZZ4` kernel. |
| `metadata/qiskit_stage_v5_scaling_report.csv` | Reports split counts and feature-scaling diagnostics for `event_onset_next_1h` and `F_quantum_4`. |

## Frozen subset and freeze metadata

| Path | Purpose |
|---|---|
| `frozen_subset/hardware_subset_event_onset_next_1h.csv` | Fixed `N=24` subset of observation windows used for the Wave 1 ZZ4 hardware pilot. |
| `metadata/zz_only_pilot_operational_plan.json` | Defines the ZZ-only hardware-pilot scope, frozen-subset policy, allowed claims, pair counts, and Wave 2 restrictions. |
| `metadata/zz_only_step8_execution_manifest.json` | Records the authorized hardware execution scope: `F_quantum_4`, `ZZ4`, frozen `N=24` subset, and Wave 1 regime metadata. |
| `metadata/v9_audit_freeze_manifest.json` | Records the audit/freeze state, allowed subset, allowed feature set, allowed kernel, threshold policy, and immutable scope constraints. |
| `metadata/zz4_subset_seed_stability_summary.json` | Records the subset-stability caveat and confirms that the frozen subset was not changed after hardware results. |

## Statevector reference artifacts

| Path | Purpose |
|---|---|
| `metadata/statevector_reference_metadata.json` | Defines the statevector kernel `K(x,y)=\|<phi(x)\|phi(y)>\|^2` and the ZZ4 feature order. |
| `statevector_reference/zz4_K_all_all.npy` | Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset. |

## Hardware kernel artifacts

| Path | Purpose |
|---|---|
| `hardware_kernels/zz4_H0_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for regime `H0`. |
| `hardware_kernels/zz4_H1_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for regime `H1`. |
| `hardware_kernels/zz4_H2_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for regime `H2`. |
| `hardware_kernels/zz4_H0_kernel.csv` | CSV representation of the `H0` hardware-derived kernel. |
| `hardware_kernels/zz4_H1_kernel.csv` | CSV representation of the `H1` hardware-derived kernel. |
| `hardware_kernels/zz4_H2_kernel.csv` | CSV representation of the `H2` hardware-derived kernel. |
| `hardware_kernels/zz4_wave1_kernel_entries_long.csv` | Long-form Wave 1 kernel-entry table for hardware-kernel inspection and comparison. |

## Hardware execution and retrieval metadata

| Path | Purpose |
|---|---|
| `job_metadata/zz4_wave1_retrieval_manifest.json` | Records retrieval metadata for the Wave 1 hardware results. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.csv` | CSV job manifest for Wave 1 regime `H0` at 1024 shots. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.csv` | CSV job manifest for Wave 1 regime `H1` at 1024 shots. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.csv` | CSV job manifest for Wave 1 regime `H2` at 1024 shots. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.json` | JSON job manifest for Wave 1 regime `H0` at 1024 shots. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.json` | JSON job manifest for Wave 1 regime `H1` at 1024 shots. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.json` | JSON job manifest for Wave 1 regime `H2` at 1024 shots. |

## Hardware analysis artifacts

| Path | Purpose |
|---|---|
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics. |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Tabular Wave 1 distortion metrics for comparing hardware kernels against the statevector reference. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable Wave 1 distortion summary. |

## Reproduction scripts

| Path | Purpose |
|---|---|
| `scripts/00_artifact_lock.py` | Locks and verifies expected artifact paths before execution. |
| `scripts/01_capture_live_backend_metadata.py` | Captures live backend metadata for the hardware execution context. |
| `scripts/02_lock_runtime_options.py` | Locks runtime options used for Wave 1 execution. |
| `scripts/03_optional_backend_compile_confirmation.py` | Optionally confirms backend compile behavior before execution. |
| `scripts/04_validate_wave1_preflight.py` | Validates Wave 1 preflight conditions before job construction or submission. |
| `scripts/05_build_zz4_wave1_circuits.py` | Builds ZZ4 Wave 1 circuits for the frozen subset. |
| `scripts/06_submit_wave1_jobs.py` | Submits Wave 1 hardware jobs. Included for traceability; reproduction should not re-submit jobs unless explicitly authorized. |
| `scripts/07_retrieve_wave1_results.py` | Retrieves Wave 1 hardware results. |
| `scripts/08_build_hardware_kernels.py` | Builds hardware-derived kernels from retrieved Wave 1 results. |
| `scripts/09_analyze_wave1_distortion.py` | Analyzes Wave 1 statevector-to-hardware kernel distortion. |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Direct analysis script for Wave 1 distortion using curated artifacts. |
| `scripts/10_create_wave1_decision_record.py` | Creates the Wave 1 decision record; it does not authorize frozen-subset modification. |
| `scripts/common.py` | Shared utilities for the Wave 1 scripts. |

## Environment and verification artifacts

| Path | Purpose |
|---|---|
| `environment/python_version.txt` | Python version recorded at package creation time. |
| `environment/pip_freeze.txt` | Package-freeze record documenting the Python environment. |
| `checksums/SHA256SUMS.txt` | SHA-256 checksum manifest for verifying the reproduction package state. |

## Repository metadata

| Path | Purpose |
|---|---|
| `README.md` | Main reproduction-package description and frozen-subset policy. |
| `MANIFEST.md` | This artifact manifest. |
| `CITATION.cff` | Citation metadata for the reproduction package. |
| `LICENSE` | License file. |
| `.gitignore` | Local and sensitive-file exclusion rules. |

## Decision-record artifacts

| Path | Purpose |
|---|---|
| `decision_records/zz4_wave1_decision_record.json` | Final Wave 1 decision record with `decision = STOP_AFTER_WAVE1_REPORT_RESULTS`. It records that the Wave 1 ZZ4 pilot is stopped after reporting, that the allowed subset is `frozen N=24 only`, that subset change and threshold relaxation are blocked in v9, and that Wave 2 is not allowed without a new decision record. |

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N=24` subset.