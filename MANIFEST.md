# Manifest

This manifest lists the curated, non-sensitive artifacts included in the IAQ Quantum Kernel Wave 1 reproducibility package.

The package supports the manuscript Materials and Methods subsections:

- **2.1. Dataset and prediction context**
- **2.2. Frozen subset**
- **2.3. ZZ4 quantum feature map**
- **2.4. Pair inventory**

## Scope

- Domain: real indoor air-quality duplicate-sensor monitoring data
- Prediction target: `event_onset_next_1h` / `y_event_onset_next_1h`
- Feature set: `F_quantum_4`
- Feature map / kernel family: `ZZ4`
- Input dimension: 4 train-scaled pollutant features
- Frozen subset: `N = 24` fixed observation windows
- Frozen hardware split: 16 train windows + 8 test windows
- Statevector reference: exact ZZ4 squared-fidelity kernel
- Pair inventory: 300 unordered upper-triangular pairs including diagonal entries
- Unique off-diagonal pairs: 276
- Diagonal entries: 24
- Hardware regimes: `H0`, `H1`, `H2`
- Fidelity circuits: 900 total, i.e. 300 pairs × 3 regimes
- Submitted shots: 1024 per circuit for `H0`, `H1`, and `H2`
- Hardware scope: Wave 1 / v9 reproduction only
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis
- Claim scope: no quantum-advantage claim and no hardware classifier-superiority claim

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This shot count affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, or the 300-row pair inventory.

## Frozen subset policy

The reproduction package uses a fixed `N = 24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset.

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

| Path                                          | Purpose                                                                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `config/config.py`                            | Defines allowed targets and compact feature sets, including `event_onset_next_1h` and `F_quantum_4`.                     |
| `preprocessing/data.py`                       | Implements dataset loading, valid-label filtering, train-only imputation, train-only scaling to `[0, pi]`, and clipping. |
| `preprocessing/feature_maps.py`               | Implements the ZZ feature-map builder used for the `F_quantum_4 / ZZ4` kernel.                                           |
| `metadata/qiskit_stage_v5_scaling_report.csv` | Reports split counts and feature-scaling diagnostics for `event_onset_next_1h` and `F_quantum_4`.                        |

## Frozen subset and freeze metadata

| Path                                                    | Purpose                                                                                                                                 |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `frozen_subset/hardware_subset_event_onset_next_1h.csv` | Fixed `N = 24` subset of observation windows used for the Wave 1 ZZ4 hardware pilot.                                                    |
| `metadata/zz_only_pilot_operational_plan.json`          | Defines the ZZ-only hardware-pilot scope, frozen-subset policy, allowed claims, pair counts, and Wave 2 restrictions.                   |
| `metadata/zz_only_step8_execution_manifest.json`        | Records the authorized hardware execution scope: `F_quantum_4`, `ZZ4`, frozen `N = 24` subset, pair-count metadata, and pair-inventory checksum. |
| `metadata/v9_audit_freeze_manifest.json`                | Records the audit/freeze state, allowed subset, allowed feature set, allowed kernel, threshold policy, and immutable scope constraints. |
| `metadata/zz4_subset_seed_stability_summary.json`       | Records the subset-stability caveat and confirms that the frozen subset was not changed after hardware results.                         |

## Pair inventory and circuit-index artifacts

| Path                                           | Purpose                                                                                                                                      |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `metadata/zz_only_step8_pair_inventory.csv`    | Deterministic 300-row upper-triangular pair inventory for the frozen `N = 24` subset: 276 unique off-diagonal pairs plus 24 diagonal entries. |
| `metadata/zz_only_step8_circuit_inventory.csv` | 900-row circuit inventory obtained by crossing the 300 pair entries with regimes `H0`, `H1`, and `H2`.                                       |
| `metadata/zz4_wave1_circuit_build_manifest.json` | Confirms circuit-build pass status, expected pair count of 300, expected circuit count of 900, and the path to the pair inventory.          |
| `metadata/zz4_wave1_preflight_report.json`     | Confirms expected and observed pair/circuit counts and records the pair-inventory checksum used at preflight.                                |
| `metadata/zz4_wave1_kernel_manifest.json`      | Confirms that the reconstructed hardware kernels are `24 x 24`, have no missing entries, use a measured-diagonal policy, and retain diagnostic PSD metadata. |

The compiled circuit bundle `zz4_wave1_circuits.qpy` is not redistributed in this package; it is regenerable via `scripts/05_build_zz4_wave1_circuits.py` from `config/wave1_scope.json`, and its integrity is pinned by `qpy_sha256` in `metadata/zz4_wave1_preflight_report.json`.

The configured symmetrization policy (`average_duplicate_entries_then_mirror`) reduced to mirror-only in Wave 1, because each unordered pair was measured exactly once and no duplicate entries existed to average; the reduction is recorded in `metadata/zz4_wave1_feature_map_spec.json` (`symmetrization_status_wave1`).

### Pair-inventory column schema

`metadata/zz_only_step8_pair_inventory.csv` contains 300 rows (276 `off_diagonal` + 24 `diagonal`) and the following 18 columns:

| Column                         | Description                                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| `pair_id`                      | Stable pair identifier (e.g. `zz4_pair_0000`).                                                                 |
| `pair_order`                   | Integer enumeration order, `0`–`299`.                                                                          |
| `pair_mode`                    | Enumeration mode; constant `upper_triangle_including_diagonal`.                                                |
| `kernel_i`                     | First kernel coordinate (row index, `0`–`23`).                                                                 |
| `kernel_j`                     | Second kernel coordinate (column index, `0`–`23`), with `kernel_i <= kernel_j`.                               |
| `sample_i_id`                  | Frozen-subset sample identifier for `i`; opaque `row_id` digest from the frozen-subset file.                  |
| `sample_j_id`                  | Frozen-subset sample identifier for `j`; opaque `row_id` digest from the frozen-subset file.                  |
| `sample_i_split`               | Reserved split-membership field for `i`; unpopulated in Wave 1.                                               |
| `sample_j_split`               | Reserved split-membership field for `j`; unpopulated in Wave 1.                                               |
| `sample_i_target`              | Reserved target-label field for `i`; unpopulated in Wave 1.                                                   |
| `sample_j_target`              | Reserved target-label field for `j`; unpopulated in Wave 1.                                                   |
| `pair_type`                    | Pair type label: `diagonal` or `off_diagonal`.                                                                |
| `split_pair`                   | Reserved derived split-pair field; unpopulated in Wave 1.                                                     |
| `target_pair`                  | Reserved derived target-pair field; unpopulated in Wave 1.                                                    |
| `expected_symmetry_mirror`     | `true` for off-diagonal rows (mirrored under `K_r(j,i) = K_r(i,j)`), `false` for diagonal rows.               |
| `include_in_wave1_full_kernel` | Wave 1 full-kernel inclusion flag; `true` for all 300 rows.                                                   |
| `sentinel_pair`                | Sentinel-pair designation; `false` for all 300 rows (no sentinel pairs designated in Wave 1).                 |
| `notes`                        | Free-text field; non-empty only on the 24 diagonal rows, recording the diagonal execution-policy note.        |

The reserved split- and target-label columns (`sample_i_split`, `sample_j_split`, `sample_i_target`, `sample_j_target`, `split_pair`, `target_pair`) are present in the schema but unpopulated, so pair rows reference samples only by opaque identifiers and carry no split membership or class label. Combined with the exhaustive upper-triangular enumeration, this makes pair inclusion label-blind by construction.

## Statevector reference artifacts

| Path                                           | Purpose                                                                                                     |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `metadata/statevector_reference_metadata.json` | Defines the statevector reference metadata for the ZZ4 feature order and the exact squared-fidelity kernel. |
| `statevector_reference/zz4_K_all_all.npy`      | Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset.                                      |

## Feature-map and execution-scope configuration

| Path | Purpose |
| --- | --- |
| `config/wave1_scope.json` | Wave 1 scope configuration consumed by the circuit-build workflow. It records the fixed ZZ4 hardware scope, including feature dimension 4, two repetitions, linear entanglement, compute--uncompute fidelity-circuit policy, all-zero bitstring policy, frozen subset size `N = 24`, 16/8 train/test split, 300 expected pair entries, and 900 expected circuits. |
| `metadata/zz4_wave1_feature_map_spec.json` | Manuscript-support feature-map specification for ZZ4. It records the Qiskit ZZFeatureMap class, feature dimension, repetitions, linear nearest-neighbor coupling pairs, data-map terms, `alpha = 2.0` manuscript convention, fidelity-circuit policy, all-zero bitstring policy, and the symmetrization policy with its Wave 1 mirror-only reduction (`symmetrization_status_wave1`). |

## Hardware kernel artifacts

| Path                                                 | Purpose                                                                            |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `hardware_kernels/zz4_H0_kernel.npy`                 | Wave 1 hardware-derived ZZ4 kernel for regime `H0`.                                |
| `hardware_kernels/zz4_H1_kernel.npy`                 | Wave 1 hardware-derived ZZ4 kernel for regime `H1`.                                |
| `hardware_kernels/zz4_H2_kernel.npy`                 | Wave 1 hardware-derived ZZ4 kernel for regime `H2`.                                |
| `hardware_kernels/zz4_H0_kernel.csv`                 | CSV representation of the `H0` hardware-derived kernel.                            |
| `hardware_kernels/zz4_H1_kernel.csv`                 | CSV representation of the `H1` hardware-derived kernel.                            |
| `hardware_kernels/zz4_H2_kernel.csv`                 | CSV representation of the `H2` hardware-derived kernel.                            |
| `hardware_kernels/zz4_wave1_kernel_entries_long.csv` | Long-form Wave 1 kernel-entry table for hardware-kernel inspection and comparison. |

## Hardware execution and retrieval metadata

| Path                                               | Purpose                                                           |
| -------------------------------------------------- | ----------------------------------------------------------------- |
| `job_metadata/zz4_wave1_job_manifest.json`         | Combined Wave 1 job manifest recording regimes `H0`, `H1`, and `H2`, 1024 submitted shots per circuit, 300 covered pairs per regime, and 900 total submitted circuits. |
| `job_metadata/zz4_wave1_retrieval_manifest.json`   | Records retrieval metadata for the Wave 1 hardware results.       |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.csv`  | CSV job manifest for Wave 1 regime `H0` at 1024 submitted shots.  |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.csv`  | CSV job manifest for Wave 1 regime `H1` at 1024 submitted shots.  |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.csv`  | CSV job manifest for Wave 1 regime `H2` at 1024 submitted shots.  |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.json` | JSON job manifest for Wave 1 regime `H0` at 1024 submitted shots. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.json` | JSON job manifest for Wave 1 regime `H1` at 1024 submitted shots. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.json` | JSON job manifest for Wave 1 regime `H2` at 1024 submitted shots. |

## Hardware analysis artifacts

| Path                                                  | Purpose                                                                                             |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics.                                |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv`  | Tabular Wave 1 distortion metrics for comparing hardware kernels against the statevector reference. |
| `hardware_analysis/zz4_wave1_distortion_summary.md`   | Human-readable Wave 1 distortion summary.                                                           |

## Reproduction scripts

| Path                                                  | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `scripts/00_artifact_lock.py`                         | Locks and verifies expected artifact paths before execution.                                                                                                                                                                                                                                                                                                                                                                   |
| `scripts/01_capture_live_backend_metadata.py`         | Captures live backend metadata for the hardware execution context.                                                                                                                                                                                                                                                                                                                                                             |
| `scripts/02_lock_runtime_options.py`                  | Locks runtime options used for Wave 1 execution.                                                                                                                                                                                                                                                                                                                                                                               |
| `scripts/03_optional_backend_compile_confirmation.py` | Optionally confirms backend compile behavior before execution.                                                                                                                                                                                                                                                                                                                                                                 |
| `scripts/04_validate_wave1_preflight.py`              | Validates Wave 1 preflight conditions before job construction or submission.                                                                                                                                                                                                                                                                                                                                                   |
| `scripts/05_build_zz4_wave1_circuits.py`              | Builds ZZ4 Wave 1 fidelity circuits for the frozen subset using the fixed 300-row pair inventory and the 900-row circuit inventory.                                                                                                                                                                                                                                                                                            |
| `scripts/06_submit_wave1_jobs.py`                     | Submits Wave 1 hardware jobs. Included for traceability only; reproduction should not re-submit jobs unless explicitly authorized.                                                                                                                                                                                                                                                                                             |
| `scripts/07_retrieve_wave1_results.py`                | Retrieves Wave 1 hardware results.                                                                                                                                                                                                                                                                                                                                                                                             |
| `scripts/08_build_hardware_kernels.py`                | Builds hardware-derived kernels from retrieved Wave 1 results.                                                                                                                                                                                                                                                                                                                                                                 |
| `scripts/09_analyze_wave1_distortion.py`              | Analyzes Wave 1 statevector-to-hardware kernel distortion.                                                                                                                                                                                                                                                                                                                                                                     |
| `scripts/09b_analyze_wave1_distortion_direct.py`      | Direct Wave 1 distortion-analysis script adapted for the curated reproduction layout. It reads labels from `frozen_subset/hardware_subset_event_onset_next_1h.csv` using `y_event_onset_next_1h`, loads the statevector reference from `statevector_reference/`, loads hardware kernels from `hardware_kernels/`, and writes outputs to `hardware_analysis/`. No separate `zz4_frozen_subset_labels.csv` artifact is required. |
| `scripts/10_create_wave1_decision_record.py`          | Creates the Wave 1 decision record; it does not authorize frozen-subset modification.                                                                                                                                                                                                                                                                                                                                          |
| `scripts/common.py`                                   | Shared utilities for the Wave 1 scripts.                                                                                                                                                                                                                                                                                                                                                                                       |

## Environment and verification artifacts

| Path                             | Purpose                                                                 |
| -------------------------------- | ----------------------------------------------------------------------- |
| `environment/python_version.txt` | Python version recorded at package creation time.                       |
| `environment/pip_freeze.txt`     | Package-freeze record documenting the Python environment.               |
| `checksums/SHA256SUMS.txt`       | SHA-256 checksum manifest for verifying the reproduction package state. |

## Manuscript support artifacts

| Path                                      | Purpose                                                      |
| ----------------------------------------- | ------------------------------------------------------------ |
| `manuscript/section_2_4_pair_inventory.md` | Manuscript-ready text for Section 2.4, Pair inventory.      |

## Repository metadata

| Path           | Purpose                                                         |
| -------------- | --------------------------------------------------------------- |
| `README.md`    | Main reproduction-package description, frozen-subset policy, and pair-inventory policy. |
| `MANIFEST.md`  | This artifact manifest.                                         |
| `CITATION.cff` | Citation metadata for the reproduction package.                 |
| `LICENSE`      | License file.                                                   |
| `.gitignore`   | Local and sensitive-file exclusion rules.                       |

## Decision-record artifacts

| Path                                              | Purpose                                                                                                                                                                                                                                         |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `decision_records/zz4_wave1_decision_record.json` | Final Wave 1 decision record with `decision = STOP_AFTER_WAVE1_REPORT_RESULTS`. It records the frozen `N = 24` subset scope, blocked subset change, blocked threshold relaxation, and that Wave 2 is not allowed without a new decision record. |

## Integrity verification

The package state can be verified with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, environment secrets, `.DS_Store`, local-only transfer scripts, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory.
