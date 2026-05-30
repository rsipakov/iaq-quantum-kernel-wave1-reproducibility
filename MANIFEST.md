# Manifest

This manifest lists the curated, non-sensitive artifacts included in the IAQ Quantum Kernel Wave 1 reproducibility package.

The package supports the manuscript sections:

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
- **2.12. Shot-noise reference-scale decomposition**
- **2.13. Statistical analysis**
- **3.1. Hardware execution summary**
- **3.2. Main distortion metrics**

## Reproducibility status

This repository is an artifact-level reproducibility package for the frozen Wave 1 ZZ4 hardware analysis. It supports reproduction of the kernel reconstruction audit, geometry-distortion metrics, CKA/KTA diagnostics, jackknife and diagonal-robustness checks, shot-noise reference-scale decomposition, Section 2.13 statistical-analysis policy, Section 3.1 hardware-execution summary, and Section 3.2 main distortion metrics from the persisted frozen artifacts listed below.

It is not a full end-to-end raw-data-to-IBM-execution pipeline. The upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission workflow, and original numbered execution pipeline are retained only as provenance where present.

The manuscript files `NewSection_3.1.md` and `NewSection_3.2.md` are not artifacts to copy into this repository. They are manuscript draft files supplied outside the reproducibility package.

## Supported input artifacts

- `frozen_subset/hardware_subset_event_onset_next_1h.csv`
- `statevector_reference/zz4_K_all_all.npy`
- `hardware_results/zz4_H0_raw_results.json`
- `hardware_results/zz4_H1_raw_results.json`
- `hardware_results/zz4_H2_raw_results.json`
- `hardware_kernels/zz4_wave1_kernel_entries_long.csv`
- `hardware_kernels/zz4_H0_kernel.csv`
- `hardware_kernels/zz4_H1_kernel.csv`
- `hardware_kernels/zz4_H2_kernel.csv`
- `hardware_kernels/zz4_H0_kernel.npy`
- `hardware_kernels/zz4_H1_kernel.npy`
- `hardware_kernels/zz4_H2_kernel.npy`
- `hardware_analysis/qiskit_kta_cka_permutation_tests.csv`

## Supported analysis scripts

- `scripts/08b_audit_kernel_reconstruction.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/09d_shot_noise_reference_scale_decomposition.py`
- `scripts/09e_label_permutation_reference.py`

## Results-section support scripts

These shell scripts are operational helpers for copying, verifying, and publishing Results-section support state. They do not submit IBM Quantum jobs and do not alter the frozen scientific scope.

- `scripts/copy_section3_1_support_files.sh`
- `scripts/verify_section3_1_support_files.sh`
- `scripts/publish_section3_1_updates.sh`
- `scripts/run_section3_1_copy_verify_publish.sh`
- `scripts/copy_section3_2_support_files.sh`
- `scripts/verify_section3_2_support_files.sh`
- `scripts/publish_section3_2_updates.sh`
- `scripts/run_section3_2_copy_verify_publish.sh`

## Supported output artifacts

- `metadata/zz4_wave1_kernel_reconstruction_audit.json`
- `hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv`
- `hardware_analysis/zz4_wave1_distortion_metrics.csv`
- `hardware_analysis/zz4_wave1_distortion_summary.json`
- `hardware_analysis/zz4_wave1_distortion_summary.md`
- `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`
- `hardware_analysis/zz4_wave1_distortion_uncertainty.json`
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv`
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json`
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md`
- `hardware_analysis/zz4_wave1_label_permutation_reference.csv`
- `hardware_analysis/zz4_wave1_label_permutation_reference.json`

## Static Section 2.13 support artifact

- `hardware_analysis/qiskit_kta_cka_permutation_tests.csv`

This file is copied from the source artifact `step6_v6_consolidation/outputs/tables/qiskit_kta_cka_permutation_tests.csv`. It is a static label-permutation reference table for statevector kernels. Section 2.13 uses only the ZZ4 statevector rows; the table also contains RMA6 rows retained for source-level traceability.

The historical table is a static source-derived reference: it is not produced by any script in this package and no permutation seed is preserved. The regenerable in-package reference is `hardware_analysis/zz4_wave1_label_permutation_reference.csv`, produced by `scripts/09e_label_permutation_reference.py` with a fixed reference seed and multi-seed sensitivity. Its persisted CSV/JSON outputs are byte-stable; local write-time provenance is emitted only to the ignored sidecar `hardware_analysis/zz4_wave1_label_permutation_reference_provenance.json`. Its `--check` mode validates the static copy without rewriting the persisted CSV/JSON artifacts.

## Section 3.1 billed quantum-second grounding

The inspected repository artifacts record job identifiers, submitted shots, submitted circuit counts, pair coverage, retrieved PUB counts, raw result dictionaries, and `H2` twirling metadata. They also persist the job-level IBM Quantum usage seconds: each raw-result payload carries a top-level `job_metrics` object whose `usage.quantum_seconds` field records the billed quantum seconds. For every regime the three reported sub-fields agree:

```text
job_metrics.usage.quantum_seconds == job_metrics.usage.seconds == job_metrics.bss.seconds
H0 = 80, H1 = 80, H2 = 84
```

The total billed usage is therefore:

```text
244 quantum seconds ≈ 4.07 minutes
```

and is a repository-grounded result, read directly from the persisted telemetry rather than transcribed from the manuscript skeleton. `scripts/verify_section3_1_support_files.sh` enforces this as a required invariant and additionally checks that the `job_metrics.timestamps` (`created`, `running`, `finished`) are present and monotonic.

A hand-entered usage-seconds artifact is not required. If a convenience file such as

```text
hardware_analysis/zz4_wave1_quantum_usage_seconds.csv
```

is nonetheless added, it is treated as a derived copy and the verification script requires it to agree with the `job_metrics` telemetry.

## Section 3.2 main distortion-metric grounding

Section 3.2 uses the supported direct-workflow metrics table:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
```

The point estimates reported at manuscript precision are:

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Centered KTA hw | Eff. rank hw | PSD rel. Fro. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741 | 0.827 | 0.0490 | 0.0878 | 0.0262 | 0.569 | 0.933 | 0.183 | 21.18 | `<2e-15` |
| `M1` | `H1` | 0.775 | 0.843 | 0.0473 | 0.0864 | 0.0261 | 0.564 | 0.937 | 0.181 | 21.22 | `<2e-15` |
| `M2` | `H2` | 0.944 | 0.986 | 0.0257 | 0.0427 | 0.0162 | 0.264 | 0.989 | 0.171 | 19.79 | `<2e-15` |

The verification script `scripts/verify_section3_2_support_files.sh` enforces the following Section 3.2 invariants:

- exactly three metric rows are present, one each for `H0`, `H1`, and `H2`;
- `n = 24` and `shots_submitted_per_circuit = 1024` for every row;
- correlation-test p-value columns remain blank/NaN in the supported minimal workflow;
- `H2` has the highest Spearman, Pearson, and CKA point estimates;
- `H2` has the lowest MAE, RMSE, MedAE, and MaxAE point estimates;
- all uncorrected hardware matrices have positive minimum eigenvalues;
- PSD relative Frobenius corrections remain below `5e-15`;
- all hardware centered-KTA values exceed the statevector KTA, and `H2` has the smallest uplift;
- `H0` and `H1` retain less than 30% of the statevector off-diagonal variance, while `H2` retains approximately 52%.

The historical source metric table in `rsipakov/QuantumKernel` contains conventional Spearman/Pearson p-value columns and slightly different roundoff-scale PSD Frobenius diagnostics. The public reproducibility package uses the direct workflow instead: p-values are blank/NaN because kernel entries are dependent, and PSD correction values are interpreted only at order-of-magnitude precision.

## Archival code

The original numbered execution scripts are retained for provenance only in `scripts/archive_original_execution_pipeline/`. They are not the supported reproduction path for this flat public artifact-level package.

The historical preprocessing code is retained in `archive_legacy_preprocessing/` for source-context provenance. It is not part of the supported Wave 1 artifact-level reproduction path.

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
| Section 3.1 completed jobs | 3 |
| Section 3.1 retrieved PUB total | 900 |
| Section 3.1 observed hardware shots | `3 * 300 * 1024 = 921600` |
| Section 3.1 billed quantum seconds | `80 + 80 + 84 = 244` (`~4.07` min), from `job_metrics.usage.quantum_seconds` |
| Section 3.2 main distortion metrics | Spearman, Pearson, MAE, RMSE, MedAE, MaxAE, CKA, centered KTA, effective rank, off-diagonal variance, PSD relative Frobenius |
| Geometry/distortion metrics | Spearman, Pearson, MAE, RMSE, MedAE, MaxAE, off-diagonal variance, effective rank, CKA, centered KTA |
| Section 2.9 CKA point estimates | `M0/H0 = 0.9333906747`, `M1/H1 = 0.9373725928`, `M2/H2 = 0.9886681278` |
| Section 2.10 centered KTA point estimates | `SV = 0.1585110924`, `M0/H0 = 0.1833084594`, `M1/H1 = 0.1814633785`, `M2/H2 = 0.1710248441` |
| Section 2.11 CKA/KTA tension quantities | `CKA loss = 1 - CKA`; `Delta_KTA = KTA_hardware - KTA_statevector` |
| Section 2.12 conservative global shot reference | `sigma_shot = 1/sqrt(2*1024) = 0.0220970869121`; conservative upper reference, not an individual-entry sampling SE |
| Section 2.12 matrix-aware shot reference | `sqrt(mean_{Omega} p_ij(1-p_ij)/1024)` using reconstructed off-diagonal hardware probabilities |
| Section 2.13 statistical unit | Frozen observation window |
| Section 2.13 jackknife metrics | Spearman, Pearson, MAE, CKA, centered KTA |
| Section 2.13 paired contrasts | `M1-M0`, `M2-M1`, `M2-M0`; descriptive contrast ratios only |
| Section 2.13 label permutation | Static source-derived ZZ4 statevector random-label reference with `n_perm = 5000`; no hardware-regime permutation p-values |
| Hardware scope | Wave 1 / v9 reproduction only |
| Purpose | Statevector-to-hardware kernel-geometry survival/distortion analysis |
| Claim scope | No quantum-advantage claim and no hardware classifier-superiority claim |

## Frozen subset policy

The reproduction package uses a fixed `N = 24` subset of observation windows from the duplicate-sensor indoor-air-quality monitoring dataset.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

Within the current Wave 1 / v9 scope, the frozen subset is immutable. No observation window may be added, removed, replaced, reordered, or reweighted after IBM hardware execution authorization.

## Dataset and preprocessing source files

| Path | Purpose |
| --- | --- |
| `config/config.py` | Defines allowed targets and compact feature sets, including `event_onset_next_1h` and `F_quantum_4`. |
| `archive_legacy_preprocessing/preprocessing/data.py` | Historical preprocessing code retained for provenance; not part of the supported artifact-level reproduction path. |
| `archive_legacy_preprocessing/preprocessing/feature_maps.py` | Historical feature-map builder code retained for provenance; not part of the supported artifact-level reproduction path. |
| `metadata/qiskit_stage_v5_scaling_report.csv` | Reports split counts and feature-scaling diagnostics for `event_onset_next_1h` and `F_quantum_4`. |

## Frozen subset and freeze metadata

| Path | Purpose |
| --- | --- |
| `frozen_subset/hardware_subset_event_onset_next_1h.csv` | Fixed `N = 24` subset used for the Wave 1 ZZ4 hardware pilot. Contains `hardware_row_order` and `y_event_onset_next_1h`. |
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
| `metadata/statevector_reference_metadata.json` | Defines the statevector reference metadata for the ZZ4 feature order and exact squared-fidelity kernel. |
| `statevector_reference/zz4_K_all_all.npy` | Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset. |
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

## Section 3.1 hardware execution summary

| Configuration | Artifact label | Job ID | Status | Shots/circuit | Pair/PUB entries | Billed quantum seconds |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | `d7vf6n3ack5s73bfc0eg` | `DONE` | 1024 | 300 | 80 |
| `M1` dynamical decoupling | `H1` | `d7vf8ocinasc738u1bhg` | `DONE` | 1024 | 300 | 80 |
| `M2` gate twirling | `H2` | `d7vfbsfmrars73d84u20` | `DONE` | 1024 | 300 | 84 |

Repository-grounded totals:

```text
Completed jobs: 3
Retrieved PUB results: 900 = 300 x 3
Observed hardware shots: 921600 = 300 x 3 x 1024
Billed quantum seconds: 244 = 80 + 80 + 84 (from job_metrics.usage.quantum_seconds; three sub-fields agree)
```

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
| `hardware_kernels/zz4_H0_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H0` / `M0`. |
| `hardware_kernels/zz4_H1_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H1` / `M1`. |
| `hardware_kernels/zz4_H2_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H2` / `M2`. |
| `hardware_kernels/zz4_H0_kernel.csv` | CSV representation of the `H0` / `M0` hardware-derived kernel. |
| `hardware_kernels/zz4_H1_kernel.csv` | CSV representation of the `H1` / `M1` hardware-derived kernel. |
| `hardware_kernels/zz4_H2_kernel.csv` | CSV representation of the `H2` / `M2` hardware-derived kernel. |
| `hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv` | Per-PUB reconstruction-audit table comparing redundant coordinate/pair identifiers against the circuit-index ledger across all 900 retrieved circuit-regime configurations. |
| `metadata/zz4_wave1_kernel_reconstruction_audit.json` | Reconstruction-audit summary; records no coordinate or pair-identifier mismatch across the 900 configurations. |

## Hardware analysis artifacts

| Path | Purpose |
| --- | --- |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Tabular Wave 1 geometry and distortion metrics. Supplies the Section 3.2 main distortion metrics and the RMSE values used in Section 2.12. |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable Wave 1 distortion summary. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` | Robustness diagnostics, including diagonal-sensitivity, leave-one-window-out jackknife summaries, directed-versus-unique checks, and paired descriptive contrasts. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.json` | Machine-readable uncertainty/robustness summary. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv` | Section 2.12 tabular shot-noise reference-scale decomposition, including global and matrix-aware scales, residuals, and shot-share values. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json` | Machine-readable Section 2.12 decomposition with formulas, input paths, output paths, and diagnostic caveat. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md` | Human-readable Section 2.12 decomposition summary. |
| `hardware_analysis/qiskit_kta_cka_permutation_tests.csv` | Source-derived Section 2.13 label-permutation reference for statevector label alignment. |
| `hardware_analysis/zz4_wave1_label_permutation_reference.csv` | Regenerable statevector ZZ4 label-permutation reference for Section 2.13. |
| `hardware_analysis/zz4_wave1_label_permutation_reference.json` | Machine-readable label-permutation reference with multi-seed sensitivity envelope. |

### Section 2.8 / 3.2 primary distortion metrics

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Effective rank | Centered KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741297 | 0.827253 | 0.049036 | 0.087770 | 0.026154 | 0.568666 | 0.933391 | 21.184209 | 0.183308 |
| `M1` | `H1` | 0.774951 | 0.842774 | 0.047290 | 0.086428 | 0.026143 | 0.563897 | 0.937373 | 21.217026 | 0.181463 |
| `M2` | `H2` | 0.943744 | 0.986203 | 0.025726 | 0.042727 | 0.016161 | 0.263978 | 0.988668 | 19.788170 | 0.171025 |

`M2/H2` has the best observed point estimates for statevector-geometry survival among the three executed configurations. This statement is descriptive and fixed-subset only; it is not a formal significance claim.

### Section 2.9 CKA point estimates and robustness summary

| Manuscript label | Artifact regime | CKA | CKA loss = `1 - CKA` | Unit-diagonal CKA sensitivity |
| --- | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.9299004014 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.9335071225 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.9853398979 |

The unit-diagonal CKA values are sensitivity checks only. Reported kernels retain the measured diagonal.

### Section 2.10 centered KTA point estimates and robustness summary

| Kernel / manuscript label | Artifact regime | Centered KTA | Hardware minus statevector | Unit-diagonal KTA sensitivity |
| --- | ---: | ---: | ---: | ---: |
| Statevector reference | `SV` | 0.1585110924 | 0 | not applicable |
| `M0` | `H0` | 0.1833084594 | +0.0247973670 | 0.1856507720 |
| `M1` | `H1` | 0.1814633785 | +0.0229522861 | 0.1839754900 |
| `M2` | `H2` | 0.1710248441 | +0.0125137518 | 0.1741450073 |

Centered KTA is not classifier accuracy and is not a prediction-performance claim.

### Section 2.11 KTA/CKA tension summary

| Manuscript label | Artifact regime | CKA | CKA loss | Hardware KTA | Statevector KTA | Delta_KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 |

The point-estimate ranks are in tension. `M2/H2` is the best statevector-geometry survivor and has the smallest KTA uplift relative to the statevector reference, while `M0/H0` has the largest absolute hardware KTA.

### Section 2.12 shot-noise reference-scale decomposition summary

| Manuscript label | Artifact regime | RMSE | sigma_shot global | residual_global | ShotShare global | sigma_shot matrix | residual_matrix | ShotShare matrix |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% | 0.008266 | 0.087380 | 0.89% |
| `M1` | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% | 0.008243 | 0.086034 | 0.91% |
| `M2` | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% | 0.008528 | 0.041868 | 3.98% |

The matrix-aware scale is computed from reconstructed hardware all-zero probabilities on the off-diagonal domain. The decomposition is diagnostic, not a full physical noise-model decomposition. The global scale is a conservative upper reference that exceeds the maximum per-entry binomial standard error by `sqrt(2)`, not the sampling standard error of an individual kernel entry.

### Section 2.13 statistical analysis summary

| Item | Status |
| --- | --- |
| Statistical unit | Frozen observation window |
| Pair-entry bootstrap CI | Not reported; no 10,000-replicate hardware-bootstrap CI artifact is present, and kernel entries are dependent observations |
| Jackknife | Leave-one-window-out jackknife for Spearman, Pearson, MAE, CKA, and centered KTA |
| Paired contrasts | `M1-M0`, `M2-M1`, `M2-M0`; descriptive `z = delta / SE_delta`, not formal tests |
| Point-estimate-only metrics | RMSE, MedAE, MaxAE, off-diagonal variance, and effective rank are reported as point estimates; no window-level jackknife is persisted for any of them |
| Correlation p-values | Blank/NaN and not used |
| Hardware label permutation | Not persisted or claimed |
| Statevector label permutation | Static source-derived ZZ4 reference, `n_perm = 5000` |
| Multiple-comparison correction | Not applied because no formal hardware-contrast p-values are generated |

| Kernel | Metric row | Observed | Null mean | Null SD | Null q95 | Null q99 | p_perm upper-tail (source field: `p_perm_two_sided`) | n_perm |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | 0.1585110924 | 0.1709625562 | 0.0352334692 | 0.2346692114 | 0.2688889140 | 0.5946810638 | 5000 |
| `zz4` | `KTA` | 0.1329093895 | 0.1433497722 | 0.0295427835 | 0.1967669338 | 0.2254596879 | 0.5946810638 | 5000 |

The persisted source field `p_perm_two_sided` records an upper-tail exceedance probability $P(T_{\text{null}} \ge T_{\text{obs}})$, retained under its original name for provenance. The observed alignment lies below the permutation-null mean, so the conclusion, no alignment beyond a random-label reference, holds under both one- and two-sided conventions. An in-package regenerable reference with an explicit symmetric two-sided value is produced by `scripts/09e_label_permutation_reference.py`.

The fixed-seed in-package reference records:

| Kernel | Source metric label | Alignment convention | Observed | Null mean | Null SD | Null q95 | Null q99 | p_upper_tail | p_two_sided_centered | p_two_sided_2min | n_perm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | centered label alignment | 0.1585110924 | 0.1709786387 | 0.0355291291 | 0.2353874561 | 0.2681052758 | 0.5988 | 0.7294 | 0.8024 | 5000 |
| `zz4` | `KTA` | uncentered label alignment | 0.1329093895 | 0.1433632571 | 0.0297906903 | 0.1973691723 | 0.2248026179 | 0.5988 | 0.7294 | 0.8024 | 5000 |

In the manuscript notation, the source metric label `CKA` denotes the centered label-alignment row, equivalent to `KTA_c(K_SV, y) = CKA(K_SV, yy^T)`. The source metric label `KTA` denotes the companion uncentered alignment row and is retained for provenance only. It is a statevector random-label reference, not a hardware-regime permutation test.

## Supported and archival scripts

| Path | Purpose |
| --- | --- |
| `scripts/08b_audit_kernel_reconstruction.py` | Audits coordinate and pair-identifier consistency between raw retrieved PUB metadata and the circuit-index ledger. |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Regenerates the direct distortion metrics from persisted kernels and statevector reference. |
| `scripts/09c_wave1_distortion_uncertainty.py` | Regenerates leave-one-window-out jackknife, paired descriptive contrasts, diagonal-sensitivity checks, and directed-versus-unique equivalence checks. |
| `scripts/09d_shot_noise_reference_scale_decomposition.py` | Regenerates Section 2.12 finite-shot reference-scale decomposition; supports `--check`. |
| `scripts/09e_label_permutation_reference.py` | Regenerates and checks the Section 2.13 statevector label-permutation reference. |
| `scripts/common.py` | Legacy shared utility module retained for archival/source-context provenance; not required by the supported direct reproduction scripts. |
| `scripts/copy_section3_1_support_files.sh` | Idempotently copies the Section 3.1 support artifacts from the upstream source tree into the flat reproducibility layout if files are absent or changed. |
| `scripts/verify_section3_1_support_files.sh` | Verifies job manifests, retrieval manifest, raw-result counts, shot counts, `H2` randomization metadata, billed quantum seconds, and long-form kernel-entry counts needed by Section 3.1. |
| `scripts/publish_section3_1_updates.sh` | Runs Section 3.1 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_1_copy_verify_publish.sh` | Runs Section 3.1 copy, verify, and publish in sequence. |
| `scripts/copy_section3_2_support_files.sh` | Idempotently copies Section 3.2 support inputs and the supported direct-analysis script from the upstream source tree if files are absent or changed. |
| `scripts/verify_section3_2_support_files.sh` | Verifies the Section 3.2 metric table, point-estimate ordering, PSD roundoff-scale diagnostics, KTA-uplift interpretation boundary, and off-diagonal variance-retention pattern. |
| `scripts/publish_section3_2_updates.sh` | Runs Section 3.2 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_2_copy_verify_publish.sh` | Runs Section 3.2 copy, direct metric regeneration, verify, and publish in sequence. |
| `scripts/archive_original_execution_pipeline/00_artifact_lock.py` through `scripts/archive_original_execution_pipeline/10_create_wave1_decision_record.py` | Original numbered execution scripts retained as archival provenance only. |

## Environment and integrity artifacts

| Path | Purpose |
| --- | --- |
| `environment/python_version.txt` | Pinned Python-version record for the source environment. |
| `environment/pip_freeze.txt` | Pinned Python package environment record. |
| `requirements.txt` | Minimal package-reproduction requirements. |
| `checksums/SHA256SUMS.txt` | SHA-256 checksum manifest for static curated files. |
| `README.md` | Human-readable repository overview and reproduction instructions. |
| `MANIFEST.md` | This file. |
| `CITATION.cff` | Citation metadata. |
| `LICENSE` | MIT License. |

## Integrity verification

Before regenerating outputs, verify the curated package state with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

After copying or updating repository files, regenerate checksums from the repository root with:

```bash
find . -type f \
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
  | xargs -0 shasum -a 256 \
  > checksums/SHA256SUMS.txt

shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, Python bytecode caches, environment secrets, `.DS_Store`, local-only transfer scripts, ignored provenance sidecars, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only. It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory.

The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. CKA, centered KTA, leave-one-window-out jackknife contrasts, source-derived statevector label-permutation diagnostics, shot-noise reference-scale decomposition, Section 3.1 hardware-execution accounting, and Section 3.2 main distortion metrics are descriptive diagnostics, not classifier-performance metrics.

For Section 3.1, the billed quantum seconds are repository-grounded: the values 80, 80, and 84 quantum seconds (total 244) are read from `job_metrics.usage.quantum_seconds` in the raw-result payloads, with the agreeing sub-fields `usage.seconds` and `bss.seconds`, and are verified by `scripts/verify_section3_1_support_files.sh`. They are reported as a resource-usage accounting only and carry no kernel-survival, classifier-performance, or quantum-advantage meaning.

For Section 3.2, `M2/H2` is reported only as the best observed point-estimate kernel-survival configuration among the three executed Wave 1 jobs. The package does not support wording that `M2/H2 significantly outperformed` the other configurations unless a separate inferential analysis is specified and reported.
