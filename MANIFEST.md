# Manifest

This manifest lists the curated, non-sensitive artifacts included in the IAQ Quantum Kernel Wave 1 reproducibility package.

The package supports the manuscript Materials and Methods subsections:

- **2.1. Dataset and prediction context**
- **2.2. Frozen subset**
- **2.3. ZZ4 quantum feature map**
- **2.4. Pair inventory**
- **2.5. IBM Quantum hardware protocol**
- **2.6. Execution configurations**
- **2.7. Kernel reconstruction**
- **2.8. Geometry and distortion metrics**
- **2.9. CKA — centered kernel alignment**
- **2.10. KTA — kernel-target alignment**
- **2.11. KTA/CKA tension analysis**

## Scope

| Field | Value |
| --- | --- |
| Domain | Real indoor air-quality duplicate-sensor monitoring data |
| Prediction target | `event_onset_next_1h` / `y_event_onset_next_1h` |
| Feature set | `F_quantum_4` |
| Feature map / kernel | `ZZ4` |
| Input dimension | 4 train-scaled pollutant features |
| Frozen subset | `N = 24` |
| Frozen hardware split | 16 train windows + 8 test windows |
| KTA label encoding | Binary labels mapped as `0 -> -1`, `1 -> +1` |
| KTA label balance | 12 negative and 12 positive signed labels |
| Statevector reference | Exact ZZ4 squared-fidelity kernel |
| Pair inventory | 300 unordered upper-triangular pairs including diagonal entries |
| Unique unordered off-diagonal pairs | 276 |
| Diagonal entries | 24 |
| Off-diagonal matrix entries used for entrywise distortion metrics | 552 directed entries with `i != j` |
| Full-matrix entries used for CKA and KTA | Complete `24 x 24` centered matrices, including the measured hardware diagonal |
| IBM backend | `ibm_fez` |
| IBM primitive | Qiskit Runtime `SamplerV2` |
| Artifact hardware-regime labels | `H0`, `H1`, `H2` |
| Manuscript execution-configuration labels | `M0`, `M1`, `M2` |
| Label mapping | `M0 = H0`, `M1 = H1`, `M2 = H2` |
| Fidelity circuits | 900 total = 300 pairs x 3 regimes |
| Originally planned shots | 4096 per circuit |
| Actual submitted shots | 1024 per circuit |
| Raw retrieved results | 300 PUB results per regime |
| Kernel-entry rows | 900 long-form entries |
| Hardware kernel matrices | Three complete `24 x 24` matrices |
| Kernel-reconstruction diagonal policy | `measured_diagonal` |
| Kernel-reconstruction symmetrization policy | `average_duplicate_entries_then_mirror` |
| PSD policy | Diagnostic only; uncorrected minimum eigenvalue retained |
| Geometry/distortion metrics | Spearman, Pearson, MAE, RMSE, MedAE, MaxAE, off-diagonal variance, effective rank, CKA, centered KTA |
| Section 2.9 CKA point estimates | `M0/H0 = 0.9333906747`, `M1/H1 = 0.9373725928`, `M2/H2 = 0.9886681278` |
| Section 2.9 CKA robustness | Diagonal sensitivity plus leave-one-window-out CKA jackknife and paired CKA contrasts |
| Section 2.10 centered KTA point estimates | `SV = 0.1585110924`, `M0/H0 = 0.1833084594`, `M1/H1 = 0.1814633785`, `M2/H2 = 0.1710248441` |
| Section 2.10 KTA robustness | Unit-diagonal sensitivity plus leave-one-window-out centered-KTA jackknife and paired KTA contrasts |
| Section 2.11 CKA/KTA tension quantities | `CKA loss = 1 - CKA`; `Delta_KTA = KTA_hardware - KTA_statevector` |
| Section 2.11 CKA/KTA tension result | `M2/H2` has highest CKA and smallest KTA uplift; `M0/H0` has highest absolute centered hardware KTA |
| Section 2.11 robustness | Paired CKA/KTA jackknife contrast synthesis and unit-diagonal rank-stability statement |
| Hardware scope | Wave 1 / v9 reproduction only |
| Purpose | Statevector-to-hardware kernel-geometry survival/distortion analysis |
| Claim scope | No quantum-advantage claim and no hardware classifier-superiority claim |

## Frozen subset policy

The reproduction package uses a fixed `N = 24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

Within the current Wave 1 / v9 scope, the frozen subset is immutable. No observation window may be added, removed, replaced, reordered, or reweighted after IBM hardware execution authorization. Thresholds used for inclusion, exclusion, hardware feasibility, compile-gate acceptance, subset stability, or pass/fail interpretation are frozen. Wave 2 execution is excluded unless explicitly authorized by a new decision record.

## Dataset and preprocessing source files

| Path | Purpose |
| --- | --- |
| `config/config.py` | Defines allowed targets and compact feature sets, including `event_onset_next_1h` and `F_quantum_4`. |
| `preprocessing/data.py` | Implements dataset loading, valid-label filtering, train-only imputation, train-only scaling to `[0, pi]`, and clipping. |
| `preprocessing/feature_maps.py` | Implements the ZZ feature-map builder used for the `F_quantum_4 / ZZ4` kernel. |
| `metadata/qiskit_stage_v5_scaling_report.csv` | Reports split counts and feature-scaling diagnostics for `event_onset_next_1h` and `F_quantum_4`. |

## Frozen subset and freeze metadata

| Path | Purpose |
| --- | --- |
| `frozen_subset/hardware_subset_event_onset_next_1h.csv` | Fixed `N = 24` subset used for the Wave 1 ZZ4 hardware pilot. Contains `hardware_row_order` and `y_event_onset_next_1h`, which are used by the direct analysis script for centered KTA. |
| `metadata/zz_only_pilot_operational_plan.json` | Defines the ZZ-only hardware-pilot scope, frozen-subset policy, allowed claims, pair counts, and Wave 2 restrictions. |
| `metadata/zz_only_step8_execution_manifest.json` | Records the authorized hardware execution scope: `F_quantum_4`, `ZZ4`, frozen `N = 24`, pair counts, planned shots, pair-inventory checksum, and the three allowed regimes. |
| `metadata/v9_audit_freeze_manifest.json` | Records the audit/freeze state, allowed subset, allowed feature set, allowed kernel, threshold policy, and immutable scope constraints. |
| `metadata/zz4_subset_seed_stability_summary.json` | Records the subset-stability caveat and confirms that the frozen subset was not changed after hardware results. |

## Pair inventory and circuit-index artifacts

| Path | Purpose |
| --- | --- |
| `metadata/zz_only_step8_pair_inventory.csv` | Deterministic 300-row upper-triangular pair inventory for the frozen `N = 24` subset. |
| `metadata/zz_only_step8_circuit_inventory.csv` | 900-row circuit inventory obtained by crossing the 300 pair entries with regimes `H0`, `H1`, and `H2`. |
| `metadata/zz4_wave1_circuit_build_manifest.json` | Confirms circuit-build pass status, 900 built circuits, expected pair count 300, expected circuit count 900, regimes `H0`/`H1`/`H2`, and all-zero measurement interpretation. |
| `metadata/zz4_wave1_preflight_report.json` | Confirms selected backend, allowed scope, expected and observed pair/circuit counts, checksums, scope lock, and local secret-scan status. |
| `circuits/zz4_wave1_circuit_index.csv` | Row-order ledger linking circuit order to circuit ID, pair ID, pair row, coordinates, and regime. |
| `circuits/zz4_wave1_circuits.qpy` | QPY archive of the built Wave 1 ZZ4 circuits. |

## Statevector reference and feature-map artifacts

| Path | Purpose |
| --- | --- |
| `metadata/statevector_reference_metadata.json` | Defines the statevector reference metadata for the ZZ4 feature order and the exact squared-fidelity kernel. |
| `statevector_reference/zz4_K_all_all.npy` | Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset; used as the reference matrix for CKA and as the statevector kernel for centered KTA. |
| `config/wave1_scope.json` | Wave 1 scope configuration consumed by circuit-build and kernel-reconstruction workflows. |
| `metadata/zz4_wave1_feature_map_spec.json` | Manuscript-support feature-map specification for ZZ4. |

## Execution configuration label policy

| Manuscript label | Artifact label | Configuration | Runtime distinction |
| --- | ---: | --- | --- |
| `M0` | `H0` | Sampler baseline | Dynamical decoupling off; gate twirling off; measurement twirling off. |
| `M1` | `H1` | Sampler + dynamical decoupling | Dynamical decoupling on with `XX`, `alap`, middle slack; twirling off. |
| `M2` | `H2` | Sampler + gate/Pauli twirling | Gate twirling on with `active-accum` and automatic randomization; dynamical decoupling and measurement twirling off. |

This label map is a reporting convention only; it does not create additional circuits, jobs, kernels, or analysis outputs.

## IBM Quantum hardware protocol artifacts

| Path | Purpose |
| --- | --- |
| `metadata/zz4_wave1_runtime_options.json` | Locked Wave 1 runtime-options artifact for regimes `H0`, `H1`, and `H2`. |
| `metadata/zz4_wave1_runtime_options_sha256.txt` | SHA-256 checksum for the locked runtime-options artifact. |
| `metadata/zz_only_step9_live_backend_metadata.json` | Live backend metadata snapshot for `ibm_fez`. |
| `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json` | Compile-confirmation summary for `ibm_fez`. |
| `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv` | Per-circuit compile records for the 900 compiled circuits. |
| `job_metadata/zz4_wave1_job_manifest.json` | Combined budget-safe Wave 1 job manifest. |
| `job_metadata/zz4_wave1_job_manifest.csv` | CSV representation of the combined Wave 1 job manifest. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.json` | JSON job manifest for `H0` / `M0`. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.csv` | CSV job manifest for `H0` / `M0`. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.json` | JSON job manifest for `H1` / `M1`. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.csv` | CSV job manifest for `H1` / `M1`. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.json` | JSON job manifest for `H2` / `M2`. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.csv` | CSV job manifest for `H2` / `M2`. |
| `job_metadata/zz4_wave1_retrieval_manifest.json` | Retrieval manifest recording all three jobs as `DONE`, 300 retrieved PUB results per regime, and no recorded retrieval failure. |
| `logs/zz4_wave1_submission_log.md` | Human-readable submission log. |
| `logs/zz4_wave1_retrieval_log.md` | Human-readable retrieval log. |

## Raw hardware-result artifacts

| Path | Purpose |
| --- | --- |
| `hardware_results/zz4_H0_raw_results.json` | Raw SamplerV2 count results for `H0` / `M0`. |
| `hardware_results/zz4_H1_raw_results.json` | Raw SamplerV2 count results for `H1` / `M1`. |
| `hardware_results/zz4_H2_raw_results.json` | Raw SamplerV2 count results for `H2` / `M2`, including twirling metadata where present. |

## Hardware kernel-reconstruction artifacts

| Path | Purpose |
| --- | --- |
| `hardware_kernels/zz4_wave1_kernel_entries_long.csv` | Long-form Wave 1 kernel-entry table recording regime, PUB order, circuit ID, pair ID, coordinates, all-zero bitstring, all-zero count, observed shots, and raw kernel value. |
| `metadata/zz4_wave1_kernel_manifest.json` | Confirms that reconstructed hardware kernels are `24 x 24`, have no missing entries, use a measured-diagonal policy, and retain diagnostic PSD metadata. |
| `hardware_kernels/zz4_H0_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H0` / `M0`; input to CKA, centered KTA, and Section 2.11 tension analysis. |
| `hardware_kernels/zz4_H1_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H1` / `M1`; input to CKA, centered KTA, and Section 2.11 tension analysis. |
| `hardware_kernels/zz4_H2_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H2` / `M2`; input to CKA, centered KTA, and Section 2.11 tension analysis. |
| `hardware_kernels/zz4_H0_kernel.csv` | CSV representation of the `H0` / `M0` hardware-derived kernel. |
| `hardware_kernels/zz4_H1_kernel.csv` | CSV representation of the `H1` / `M1` hardware-derived kernel. |
| `hardware_kernels/zz4_H2_kernel.csv` | CSV representation of the `H2` / `M2` hardware-derived kernel. |
| `hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv` | Per-PUB reconstruction-audit table comparing redundant coordinate/pair identifiers against the circuit-index ledger across all 900 retrieved circuit-regime configurations. |
| `metadata/zz4_wave1_kernel_reconstruction_audit.json` | Reconstruction-audit summary; records no coordinate or pair-identifier mismatch across the 900 configurations. |

## Hardware analysis artifacts

| Path | Purpose |
| --- | --- |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Tabular Wave 1 geometry and distortion metrics. For Section 2.9 it contains `CKA_hardware_vs_statevector`, `CKA_statevector_self`, and `CKA_drop_relative_to_statevector`. For Section 2.10 it contains `KTA_hardware`, `KTA_statevector`, and `KTA_drop_relative_to_statevector`. For Section 2.11 it provides `CKA loss = CKA_drop_relative_to_statevector` and `Delta_KTA = -KTA_drop_relative_to_statevector`. |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics. Records `analysis_mode = direct_npy_loader_budget_safe_1024_shots`, all required regimes reported, input/output paths, no failure reasons, and the interpretation policy. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable Wave 1 distortion summary with the primary metric table, including KTA. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` | Robustness diagnostics. For Section 2.9 it contains CKA diagonal-sensitivity and leave-one-window-out CKA jackknife rows. For Section 2.10 it contains `diagonal_robustness`, `leave_one_window_out_jackknife`, and `paired_jackknife_contrast` rows with `metric = kta_centered`. For Section 2.11 it supplies paired CKA/KTA contrast ratios and unit-diagonal rank-stability evidence. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.json` | Machine-readable uncertainty/robustness summary recording the resampling unit, input paths, diagonal-sensitivity policy, CKA jackknife diagnostics, KTA jackknife diagnostics, and descriptive-only inferential policy. |

### Section 2.9 CKA point estimates and robustness summary

| Manuscript label | Artifact regime | CKA | CKA loss = `1 - CKA` | Unit-diagonal CKA sensitivity |
| --- | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.9299004014 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.9335071225 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.9853398979 |

The unit-diagonal CKA values are sensitivity checks only. Reported kernels retain the measured diagonal.

The CKA leave-one-window-out jackknife rows are stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` with `diagonal_policy = measured_diagonal_full_matrix`. The persisted paired CKA contrasts are `M1-M0`, `M2-M1`, and `M2-M0`; they are descriptive robustness diagnostics, not inferential significance tests.

### Section 2.10 centered KTA point estimates and robustness summary

| Kernel / manuscript label | Artifact regime | Centered KTA | Hardware minus statevector | Unit-diagonal KTA sensitivity |
| --- | ---: | ---: | ---: | ---: |
| Statevector reference | `SV` | 0.1585110924 | 0 | not applicable |
| `M0` | `H0` | 0.1833084594 | +0.0247973670 | 0.1856507720 |
| `M1` | `H1` | 0.1814633785 | +0.0229522861 | 0.1839754900 |
| `M2` | `H2` | 0.1710248441 | +0.0125137518 | 0.1741450073 |

The unit-diagonal KTA values are sensitivity checks only. Reported kernels retain the measured diagonal.

| Centered KTA jackknife | `M0` / `H0` | `M1` / `H1` | `M2` / `H2` |
| --- | ---: | ---: | ---: |
| Point estimate ± jackknife SE | 0.1833084594 ± 0.036223 | 0.1814633785 ± 0.035045 | 0.1710248441 ± 0.035962 |

| Paired centered-KTA contrast | Delta | Jackknife SE of delta | Descriptive z |
| --- | ---: | ---: | ---: |
| `M1-M0` | -0.001845 | 0.005621 | -0.328255 |
| `M2-M1` | -0.010439 | 0.013436 | -0.776936 |
| `M2-M0` | -0.012284 | 0.014088 | -0.871930 |

Centered KTA is not classifier accuracy and is not a prediction-performance claim. The KTA paired contrasts are descriptive window-level robustness diagnostics, not inferential significance tests.

### Section 2.11 KTA/CKA tension summary

| Manuscript label | Artifact regime | CKA | CKA loss | Hardware KTA | Statevector KTA | Delta_KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 |

The point-estimate ranks are in tension. `M2/H2` is the best statevector-geometry survivor and has the smallest KTA uplift relative to the statevector reference, while `M0/H0` has the largest absolute hardware KTA. Section 2.11 therefore interprets hardware KTA uplift as class-structured kernel distortion, not as a classifier-performance improvement.

| Paired contrast | Delta CKA | CKA z | Delta centered KTA | KTA z |
| --- | ---: | ---: | ---: | ---: |
| `M1-M0` | +0.0039819182 | 0.626856 | -0.0018450809 | -0.328255 |
| `M2-M1` | +0.0512955350 | 3.086171 | -0.0104385344 | -0.776936 |
| `M2-M0` | +0.0552774532 | 2.828536 | -0.0122836153 | -0.871930 |

The CKA contrast ratios support the `M2` geometry-survival conclusion. The KTA contrast ratios are unresolved at the window scale and are not used as model-selection evidence.

## Reproduction scripts

| Path | Purpose |
| --- | --- |
| `scripts/00_artifact_lock.py` | Locks and verifies expected artifact paths before execution. |
| `scripts/01_capture_live_backend_metadata.py` | Captures live backend metadata for the hardware execution context. |
| `scripts/02_lock_runtime_options.py` | Locks runtime options used for Wave 1 execution. |
| `scripts/03_optional_backend_compile_confirmation.py` | Confirms backend compile behavior before execution. |
| `scripts/04_validate_wave1_preflight.py` | Validates Wave 1 preflight conditions before job construction or submission. |
| `scripts/05_build_zz4_wave1_circuits.py` | Builds ZZ4 Wave 1 fidelity circuits for the frozen subset using the fixed pair and circuit inventories. |
| `scripts/06_submit_wave1_jobs.py` | Submits Wave 1 hardware jobs. Included for traceability only; reproduction should not re-submit jobs unless explicitly authorized. |
| `scripts/07_retrieve_wave1_results.py` | Retrieves Wave 1 hardware results and writes regime-specific raw-result JSON artifacts. |
| `scripts/08_build_hardware_kernels.py` | Builds hardware-derived kernels from retrieved Wave 1 results. |
| `scripts/09_analyze_wave1_distortion.py` | Analyzes Wave 1 statevector-to-hardware kernel distortion in the source repository layout. |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Direct reproduction script. Implements `center_kernel`, `cka`, and centered KTA; reads the frozen subset, statevector kernel, and three hardware-kernel NumPy arrays, then writes the hardware-analysis artifacts. |
| `scripts/09c_wave1_distortion_uncertainty.py` | Computes robustness diagnostics, including CKA diagonal sensitivity, leave-one-window-out CKA jackknife, KTA diagonal sensitivity, leave-one-window-out centered-KTA jackknife, paired KTA contrasts, and the paired CKA/KTA contrast ingredients used by Section 2.11. |
| `scripts/10_create_wave1_decision_record.py` | Creates the Wave 1 decision record; it does not authorize frozen-subset modification. |
| `scripts/common.py` | Shared utilities for the Wave 1 scripts. |
| `scripts/08b_audit_kernel_reconstruction.py` | Independent reconstruction audit; verifies coordinate/pair-identifier consistency between retrieved PUBs and the circuit-index ledger. |

## Environment and verification artifacts

| Path | Purpose |
| --- | --- |
| `environment/python_version.txt` | Python version recorded at package creation time. |
| `environment/pip_freeze.txt` | Package-freeze record documenting the Python environment. |
| `checksums/SHA256SUMS.txt` | SHA-256 checksum manifest for verifying the reproduction package state. |

## Repository metadata

| Path | Purpose |
| --- | --- |
| `README.md` | Main reproduction-package description, updated to include Section 2.11 and the KTA/CKA tension-analysis diagnostics. |
| `MANIFEST.md` | This artifact manifest, updated to include Section 2.11 and the KTA/CKA tension-analysis diagnostics. |
| `CITATION.cff` | Citation metadata for the reproduction package. |
| `LICENSE` | License file. No update is required for the addition of Section 2.11 documentation. |
| `.gitignore` | Local and sensitive-file exclusion rules. |

## Decision-record artifacts

| Path | Purpose |
| --- | --- |
| `decision_records/zz4_wave1_decision_record.json` | Final Wave 1 decision record with `decision = STOP_AFTER_WAVE1_REPORT_RESULTS`; records frozen `N = 24`, blocked subset change, blocked threshold relaxation, and no Wave 2 without a new decision record. |

## Integrity verification

Verify the package state with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, environment secrets, `.DS_Store`, local-only transfer scripts, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory. The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. CKA and centered KTA are descriptive geometry diagnostics, not classifier-performance metrics. Section 2.11 treats KTA uplift as hardware-induced class-structured distortion, not as a prediction-performance improvement.

The leave-one-window-out CKA and centered-KTA jackknife contrasts are descriptive robustness checks on the frozen `N = 24` window scale; they are not formal significance tests.
