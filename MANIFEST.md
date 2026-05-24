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
| Statevector reference | Exact ZZ4 squared-fidelity kernel |
| Pair inventory | 300 unordered upper-triangular pairs including diagonal entries |
| Unique unordered off-diagonal pairs | 276 |
| Diagonal entries | 24 |
| Off-diagonal matrix entries used for distortion metrics | 552 directed entries with `i != j` |
| IBM backend | `ibm_fez` |
| IBM primitive | Qiskit Runtime `SamplerV2` |
| Artifact hardware-regime labels | `H0`, `H1`, `H2` |
| Manuscript execution-configuration labels | `M0`, `M1`, `M2` |
| Label mapping | `M0 = H0`, `M1 = H1`, `M2 = H2` |
| Fidelity circuits | 900 total = 300 pairs x 3 regimes |
| Originally planned shots | 4096 per circuit |
| Actual submitted shots | 1024 per circuit |
| Total submitted circuit-configuration rows | 900 |
| Raw retrieved results | 300 PUB results per regime |
| Kernel-entry rows | 900 long-form entries |
| Hardware kernel matrices | Three complete `24 x 24` matrices |
| Kernel-reconstruction diagonal policy | `measured_diagonal` |
| Kernel-reconstruction symmetrization policy | `average_duplicate_entries_then_mirror` |
| PSD policy | Diagnostic only; uncorrected minimum eigenvalue retained |
| Geometry/distortion metrics | Spearman, Pearson, MAE, RMSE, MedAE, MaxAE, off-diagonal variance, effective rank, CKA, KTA |
| Hardware scope | Wave 1 / v9 reproduction only |
| Purpose | Statevector-to-hardware kernel-geometry survival/distortion analysis |
| Claim scope | No quantum-advantage claim and no hardware classifier-superiority claim |

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This shot count affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, the frozen subset, the 300-row pair inventory, the kernel-reconstruction rules, or the distortion-metric definitions.

## Frozen subset policy

The reproduction package uses a fixed `N = 24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

Within the current Wave 1 / v9 scope, the frozen subset is immutable. No observation window may be added, removed, replaced, reordered, or reweighted after IBM hardware execution authorization.

Thresholds used for inclusion, exclusion, hardware feasibility, compile-gate acceptance, subset stability, or pass/fail interpretation are frozen. Post-hoc threshold relaxation is not permitted.

Wave 2 execution is excluded from the current frozen-subset reproduction unless explicitly authorized by a new decision record. Full 300-pair Wave 2 execution is not authorized under the current scope. Any sentinel-only Wave 2 extension must preserve the frozen-subset policy and must not retroactively alter the Wave 1 subset, thresholds, or claims.

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
| `frozen_subset/hardware_subset_event_onset_next_1h.csv` | Fixed `N = 24` subset of observation windows used for the Wave 1 ZZ4 hardware pilot. Contains `hardware_row_order` and `y_event_onset_next_1h`, which are used by the direct distortion-analysis script for label alignment. |
| `metadata/zz_only_pilot_operational_plan.json` | Defines the ZZ-only hardware-pilot scope, frozen-subset policy, allowed claims, pair counts, and Wave 2 restrictions. |
| `metadata/zz_only_step8_execution_manifest.json` | Records the authorized hardware execution scope: `F_quantum_4`, `ZZ4`, frozen `N = 24`, pair counts, planned shots, pair-inventory checksum, and the three allowed regimes. |
| `metadata/v9_audit_freeze_manifest.json` | Records the audit/freeze state, allowed subset, allowed feature set, allowed kernel, threshold policy, and immutable scope constraints. |
| `metadata/zz4_subset_seed_stability_summary.json` | Records the subset-stability caveat and confirms that the frozen subset was not changed after hardware results. |

## Pair inventory and circuit-index artifacts

| Path | Purpose |
| --- | --- |
| `metadata/zz_only_step8_pair_inventory.csv` | Deterministic 300-row upper-triangular pair inventory for the frozen `N = 24` subset: 276 unique off-diagonal pairs plus 24 diagonal entries. |
| `metadata/zz_only_step8_circuit_inventory.csv` | 900-row circuit inventory obtained by crossing the 300 pair entries with regimes `H0`, `H1`, and `H2`. |
| `metadata/zz4_wave1_circuit_build_manifest.json` | Confirms circuit-build pass status, 900 built circuits, expected pair count 300, expected circuit count 900, regimes `H0`/`H1`/`H2`, and all-zero measurement interpretation. |
| `metadata/zz4_wave1_preflight_report.json` | Confirms selected backend, allowed scope, expected and observed pair/circuit counts, checksums, scope lock, and local secret-scan status. |
| `circuits/zz4_wave1_circuit_index.csv` | Row-order ledger linking circuit order to `circuit_inventory_id`, `pair_id`, pair row, coordinates, and regime; used directly during kernel reconstruction. |
| `circuits/zz4_wave1_circuits.qpy` | QPY archive of the built Wave 1 ZZ4 circuits. |

### Pair-inventory column schema

`metadata/zz_only_step8_pair_inventory.csv` contains 300 rows and the following 18 columns:

| Column | Description |
| --- | --- |
| `pair_id` | Stable pair identifier, e.g. `zz4_pair_0000`. |
| `pair_order` | Integer enumeration order, `0`-`299`. |
| `pair_mode` | Enumeration mode; constant `upper_triangle_including_diagonal`. |
| `kernel_i` | First kernel coordinate, `0`-`23`. |
| `kernel_j` | Second kernel coordinate, `0`-`23`, with `kernel_i <= kernel_j`. |
| `sample_i_id` | Frozen-subset sample identifier for `i`; opaque row identifier. |
| `sample_j_id` | Frozen-subset sample identifier for `j`; opaque row identifier. |
| `sample_i_split` | Reserved split-membership field for `i`; unpopulated in Wave 1. |
| `sample_j_split` | Reserved split-membership field for `j`; unpopulated in Wave 1. |
| `sample_i_target` | Reserved target-label field for `i`; unpopulated in Wave 1. |
| `sample_j_target` | Reserved target-label field for `j`; unpopulated in Wave 1. |
| `pair_type` | Pair type label: `diagonal` or `off_diagonal`. |
| `split_pair` | Reserved derived split-pair field; unpopulated in Wave 1. |
| `target_pair` | Reserved derived target-pair field; unpopulated in Wave 1. |
| `expected_symmetry_mirror` | `true` for off-diagonal rows and `false` for diagonal rows. |
| `include_in_wave1_full_kernel` | Wave 1 full-kernel inclusion flag; `true` for all 300 rows. |
| `sentinel_pair` | Sentinel-pair designation; `false` for all 300 rows. |
| `notes` | Free-text field; non-empty only on diagonal rows. |

The reserved split- and target-label columns are present in the schema but unpopulated, so pair rows reference samples only by opaque identifiers and carry no split membership or class label. Combined with the exhaustive upper-triangular enumeration, this makes pair inclusion label-blind by construction.

The configured kernel-reconstruction symmetrization policy is `average_duplicate_entries_then_mirror`. In Wave 1 it reduced to mirror-only, because each unordered pair was measured exactly once and no duplicate entries existed to average.

## Statevector reference artifacts

| Path | Purpose |
| --- | --- |
| `metadata/statevector_reference_metadata.json` | Defines the statevector reference metadata for the ZZ4 feature order and the exact squared-fidelity kernel. |
| `statevector_reference/zz4_K_all_all.npy` | Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset; used as the reference matrix in the distortion analysis. |

## Feature-map and execution-scope configuration

| Path | Purpose |
| --- | --- |
| `config/wave1_scope.json` | Wave 1 scope configuration consumed by the circuit-build and kernel-reconstruction workflows. It records the fixed ZZ4 hardware scope, including feature dimension 4, two repetitions, linear entanglement, compute--uncompute fidelity-circuit policy, all-zero bitstring policy, frozen subset size `N = 24`, 16/8 train/test split, 300 expected pair entries, 900 expected circuits, and kernel-reconstruction policies. |
| `metadata/zz4_wave1_feature_map_spec.json` | Manuscript-support feature-map specification for ZZ4. It records the Qiskit ZZFeatureMap class, feature dimension, repetitions, linear nearest-neighbor coupling pairs, data-map terms, `alpha = 2.0` manuscript convention, fidelity-circuit policy, and all-zero bitstring policy. |

## Execution configuration label policy

The source artifacts retain the hardware-regime labels H0, H1, and H2. The manuscript uses manuscript-level execution-configuration labels M0, M1, and M2 to avoid confusion between the artifact label H0 and the conventional null-hypothesis symbol H_0. This label map is a reporting convention only; it does not create additional circuits, jobs, kernels, or analysis outputs.

| Manuscript label | Artifact label | Configuration | Runtime distinction |
| --- | ---: | --- | --- |
| `M0` | `H0` | Sampler baseline | Dynamical decoupling off; gate twirling off; measurement twirling off. |
| `M1` | `H1` | Sampler + dynamical decoupling | Dynamical decoupling on with `XX`, `alap`, middle slack; twirling off. |
| `M2` | `H2` | Sampler + gate/Pauli twirling | Gate twirling on with `active-accum` and automatic randomization; dynamical decoupling and measurement twirling off. |

All artifact filenames, JSON fields, CSV regime columns, raw-result files, kernel matrices, and checksum records remain keyed by `H0`, `H1`, and `H2`. Manuscript tables may report both labels for traceability.

## IBM Quantum hardware protocol artifacts

| Path | Purpose |
| --- | --- |
| `metadata/zz4_wave1_runtime_options.json` | Locked Wave 1 runtime-options artifact for artifact regimes `H0`, `H1`, and `H2`, corresponding to manuscript execution configurations `M0`, `M1`, and `M2`. Records `SamplerV2`, planned 4096 shots, selected backend `ibm_fez`, expected 300 pairs, expected 900 circuits, per-regime runtime options, and per-regime SHA-256 digests. |
| `metadata/zz4_wave1_runtime_options_sha256.txt` | SHA-256 checksum for the locked runtime-options artifact. |
| `metadata/zz_only_step9_live_backend_metadata.json` | Live backend metadata snapshot for `ibm_fez`: backend version, qubit count, operational status, primitive class, runtime options, package versions, metadata-gate status, and scope-drift status. |
| `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json` | Compile-confirmation summary for `ibm_fez`: compiled-circuit count, maximum depth, maximum two-qubit count, active-qubit resource gate, and pass/fail status. |
| `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv` | Per-circuit compile records for the 900 compiled circuits. |
| `job_metadata/zz4_wave1_job_manifest.json` | Combined budget-safe Wave 1 job manifest recording `H0`, `H1`, `H2`, 1024 submitted shots per circuit, three IBM job IDs, 300 circuits/pairs per regime, and 900 total submitted circuits. |
| `job_metadata/zz4_wave1_job_manifest.csv` | CSV representation of the combined Wave 1 job manifest. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.json` | JSON job manifest for `H0` / manuscript `M0` at 1024 submitted shots per circuit. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.csv` | CSV job manifest for `H0` / manuscript `M0` at 1024 submitted shots per circuit. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.json` | JSON job manifest for `H1` / manuscript `M1` at 1024 submitted shots per circuit. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.csv` | CSV job manifest for `H1` / manuscript `M1` at 1024 submitted shots per circuit. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.json` | JSON job manifest for `H2` / manuscript `M2` at 1024 submitted shots per circuit. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.csv` | CSV job manifest for `H2` / manuscript `M2` at 1024 submitted shots per circuit. |
| `job_metadata/zz4_wave1_retrieval_manifest.json` | Retrieval manifest recording all three jobs as `DONE`, 300 retrieved PUB results per regime, and no recorded retrieval failure. |
| `logs/zz4_wave1_submission_log.md` | Human-readable submission log. |
| `logs/zz4_wave1_retrieval_log.md` | Human-readable retrieval log. |

### IBM Quantum job inventory

| Manuscript label | Artifact regime | Runtime mode | Mitigation/twirling policy | Job ID | Submitted shots | Circuits | Retrieved PUBs |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `M0` | `H0` | `SamplerV2` | Baseline, no DD, no twirling | `d7vf6n3ack5s73bfc0eg` | 1024 | 300 | 300 |
| `M1` | `H1` | `SamplerV2` | Dynamical decoupling only | `d7vf8ocinasc738u1bhg` | 1024 | 300 | 300 |
| `M2` | `H2` | `SamplerV2` | Gate/Pauli twirling only | `d7vfbsfmrars73d84u20` | 1024 | 300 | 300 |

## Raw hardware-result artifacts

| Path | Purpose |
| --- | --- |
| `hardware_results/zz4_H0_raw_results.json` | Raw SamplerV2 count results for `H0` / manuscript `M0`; stores per-PUB count dictionaries, observed shots, and circuit metadata. |
| `hardware_results/zz4_H1_raw_results.json` | Raw SamplerV2 count results for `H1` / manuscript `M1`; stores per-PUB count dictionaries, observed shots, and circuit metadata. |
| `hardware_results/zz4_H2_raw_results.json` | Raw SamplerV2 count results for `H2` / manuscript `M2`; stores per-PUB count dictionaries, observed shots, circuit metadata, and twirling metadata where present. |

## Hardware kernel-reconstruction artifacts

| Path | Purpose |
| --- | --- |
| `hardware_kernels/zz4_wave1_kernel_entries_long.csv` | Long-form Wave 1 kernel-entry table recording regime, PUB order, circuit ID, pair ID, coordinates, all-zero bitstring, all-zero count, observed shots, and raw kernel value. |
| `metadata/zz4_wave1_kernel_manifest.json` | Confirms that the reconstructed hardware kernels are `24 x 24`, have no missing entries, use a measured-diagonal policy, and retain diagnostic PSD metadata. |
| `hardware_kernels/zz4_H0_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H0` / manuscript `M0`; input to distortion analysis. |
| `hardware_kernels/zz4_H1_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H1` / manuscript `M1`; input to distortion analysis. |
| `hardware_kernels/zz4_H2_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H2` / manuscript `M2`; input to distortion analysis. |
| `hardware_kernels/zz4_H0_kernel.csv` | CSV representation of the `H0` / `M0` hardware-derived kernel. |
| `hardware_kernels/zz4_H1_kernel.csv` | CSV representation of the `H1` / `M1` hardware-derived kernel. |
| `hardware_kernels/zz4_H2_kernel.csv` | CSV representation of the `H2` / `M2` hardware-derived kernel. |

### Kernel-reconstruction diagnostics

| Artifact regime | Manuscript label | Shape | Finite entries | Missing entries | Diagonal policy | Minimum eigenvalue before PSD diagnostic | PSD correction Frobenius norm |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| `H0` | `M0` | `24 x 24` | 576 | 0 | `measured_diagonal` | 0.428763111071851 | 8.583547173776992e-15 |
| `H1` | `M1` | `24 x 24` | 576 | 0 | `measured_diagonal` | 0.46215593566687874 | 9.259630923313487e-15 |
| `H2` | `M2` | `24 x 24` | 576 | 0 | `measured_diagonal` | 0.23216438914772836 | 1.070945942310601e-14 |

The PSD calculation is diagnostic only. The uncorrected kernels remain the reported hardware kernels, and the uncorrected minimum eigenvalue is retained in the manifest.

## Hardware analysis artifacts

| Path | Purpose |
| --- | --- |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Tabular Wave 1 geometry and distortion metrics. Contains one row per artifact regime (`H0`, `H1`, `H2`) and columns for Spearman, Pearson, MAE, RMSE, median absolute error, maximum absolute error, off-diagonal variance, effective rank, centered kernel alignment, centered kernel-target alignment, and PSD diagnostics. |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics. Records `analysis_mode = direct_npy_loader_budget_safe_1024_shots`, all required regimes reported, input/output paths, no failure reasons, and the interpretation policy. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable Wave 1 distortion summary with the primary metric table. |

### Geometry-distortion metric summary

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Effective rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741297 | 0.827253 | 0.049036 | 0.087770 | 0.026154 | 0.568666 | 0.933391 | 21.184209 |
| `M1` | `H1` | 0.774951 | 0.842774 | 0.047290 | 0.086428 | 0.026143 | 0.563897 | 0.937373 | 21.217026 |
| `M2` | `H2` | 0.943744 | 0.986203 | 0.025726 | 0.042727 | 0.016161 | 0.263978 | 0.988668 | 19.788170 |

Additional persisted values:

| Metric | Statevector | H0 / M0 | H1 / M1 | H2 / M2 |
| --- | ---: | ---: | ---: | ---: |
| Off-diagonal variance | 0.0186558 | 0.0053865 | 0.0052842 | 0.0097585 |
| Effective rank | 17.971892 | 21.184209 | 21.217026 | 19.788170 |
| Centered kernel-target alignment | 0.158511 | 0.183308 | 0.181463 | 0.171025 |

The centered kernel-target alignment values are diagnostic label-geometry summaries only. They are not hardware classifier-performance metrics and do not support a hardware-superiority or quantum-advantage claim.

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
| `scripts/09b_analyze_wave1_distortion_direct.py` | Direct Wave 1 distortion-analysis script adapted for the curated reproduction layout. Reads the frozen subset, statevector kernel, and three hardware-kernel NumPy arrays, then writes the hardware-analysis artifacts. |
| `scripts/10_create_wave1_decision_record.py` | Creates the Wave 1 decision record; it does not authorize frozen-subset modification. |
| `scripts/common.py` | Shared utilities for the Wave 1 scripts, including all-zero probability extraction, matrix CSV writing, and PSD diagnostic routines. |

## Environment and verification artifacts

| Path | Purpose |
| --- | --- |
| `environment/python_version.txt` | Python version recorded at package creation time. |
| `environment/pip_freeze.txt` | Package-freeze record documenting the Python environment. |
| `checksums/SHA256SUMS.txt` | SHA-256 checksum manifest for verifying the reproduction package state. |

## Repository metadata

| Path | Purpose |
| --- | --- |
| `README.md` | Main reproduction-package description. |
| `MANIFEST.md` | This artifact manifest. |
| `CITATION.cff` | Citation metadata for the reproduction package. |
| `LICENSE` | License file. No update is required for the addition of Section 2.8 documentation. |
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

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory. The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. The centered kernel-target alignment values in the distortion analysis are descriptive geometry diagnostics on the frozen subset and are not classifier-performance claims.
