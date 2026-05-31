# Manifest

This manifest lists the curated, non-sensitive artifacts included in the IAQ Quantum Kernel Wave 1 reproducibility package. It is cumulative through manuscript **Materials and methods** sections 2.1--2.13 and **Results** sections 3.1--3.4.

## Supported manuscript sections

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
- **3.3. Window-level statistical support and label-alignment reference**
- **3.4. Central synthesis: the CKA/KTA tension and the finite-shot reference scale**

## Reproducibility status

This repository is an artifact-level reproducibility package for the frozen Wave 1 ZZ4 hardware analysis. It supports reproduction of the kernel reconstruction audit, geometry-distortion metrics, CKA/KTA diagnostics, jackknife and diagonal-robustness checks, shot-noise reference-scale decomposition, statevector label-permutation reference, Section 2.13 statistical-analysis policy, Section 3.1 hardware-execution summary, Section 3.2 main distortion metrics, Section 3.3 statistical support and label-alignment diagnostics, and Section 3.4 KTA/CKA-tension synthesis.

It is not a full end-to-end raw-data-to-IBM-execution pipeline. The upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission workflow, and original numbered execution pipeline are retained only as provenance where present.

The manuscript files `NewSection_3.1.md`, `NewSection_3.2.md`, `NewSection_3.3.md`, `NewSection_3.4.md`, `NewSection_3.4_Revised*.md`, and `NewSection_3.4_*Instructions.md` are not artifacts to copy into this repository. They are manuscript draft files supplied outside the reproducibility package.

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
- `scripts/copy_section3_3_support_files.sh`
- `scripts/verify_section3_3_support_files.sh`
- `scripts/publish_section3_3_updates.sh`
- `scripts/run_section3_3_copy_verify_publish.sh`
- `scripts/copy_section3_4_support_files.sh`
- `scripts/verify_section3_4_support_files.sh`
- `scripts/publish_section3_4_updates.sh`
- `scripts/run_section3_4_copy_verify_publish.sh`

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

## Static Section 2.13 / Section 3.3 / Section 3.4 support artifact

- `hardware_analysis/qiskit_kta_cka_permutation_tests.csv`

This file is copied from the source artifact `step6_v6_consolidation/outputs/tables/qiskit_kta_cka_permutation_tests.csv` when available. It is a static label-permutation reference table for statevector kernels. Sections 2.13, 3.3, and 3.4 use only the ZZ4 statevector rows; the table also contains RMA6 rows retained for source-level traceability.

The historical table is a static source-derived reference: it is not produced by any script in this package and no permutation seed is preserved. The regenerable in-package reference is `hardware_analysis/zz4_wave1_label_permutation_reference.csv`, produced by `scripts/09e_label_permutation_reference.py` with a fixed reference seed and multi-seed sensitivity. Its persisted CSV/JSON outputs are byte-stable; local write-time provenance is emitted only to the ignored sidecar `hardware_analysis/zz4_wave1_label_permutation_reference_provenance.json`. Its `--check` mode validates the static copy without rewriting the persisted CSV/JSON artifacts.

## Scope

| Field | Value |
| --- | --- |
| Domain | Real indoor-air-quality duplicate-sensor monitoring data |
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
| Section 2.9 CKA point estimates | `M0/H0 = 0.9333906747`, `M1/H1 = 0.9373725928`, `M2/H2 = 0.9886681278` |
| Section 2.10 centered KTA point estimates | `SV = 0.1585110924`, `M0/H0 = 0.1833084594`, `M1/H1 = 0.1814633785`, `M2/H2 = 0.1710248441` |
| Section 2.11 / 3.4 KTA/CKA tension quantities | `CKA loss = 1 - CKA`; `Delta_KTA = KTA_hardware - KTA_statevector` |
| Section 3.4 hardware off-diagonal probability means | `hardware_offdiag_mean` field of `zz4_wave1_shot_noise_reference_scale_decomposition.{csv,json}` |
| Section 2.12 conservative global shot reference | `sigma_ref_global = 1/sqrt(2*1024) = 0.0220970869121` |
| Section 2.12 matrix-aware shot reference | `sqrt(mean_{Omega} p_ij(1-p_ij)/1024)` using reconstructed off-diagonal hardware probabilities |
| Section 2.13 statistical unit | Frozen observation window |
| Section 2.13 jackknife metrics | Spearman, Pearson, MAE, CKA, centered KTA |
| Section 2.13 paired contrasts | `M1-M0`, `M2-M1`, `M2-M0`; descriptive contrast ratios only |
| Section 2.13 label permutation | Static source-derived ZZ4 statevector reference and regenerable fixed-seed in-package reference, both with `n_perm = 5000`; no hardware-regime permutation p-values |
| Hardware scope | Wave 1 / v9 reproduction only |
| Purpose | Statevector-to-hardware kernel-geometry survival/distortion analysis |
| Claim scope | No quantum-advantage claim and no hardware classifier-superiority claim |

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
| `decision_records/zz4_wave1_decision_record.json` | Records the Wave 1 decision boundary and allowed claim scope. |

## Pair inventory and circuit-index artifacts

| Path | Purpose |
| --- | --- |
| `metadata/zz_only_step8_pair_inventory.csv` | Deterministic 300-row upper-triangular pair inventory for the frozen `N = 24` subset. |
| `metadata/zz_only_step8_circuit_inventory.csv` | 900-row circuit inventory obtained by crossing the 300 pair entries with regimes `H0`, `H1`, and `H2`. |
| `metadata/zz4_wave1_circuit_build_manifest.json` | Confirms circuit-build pass status, expected pair count, expected circuit count, regimes, and all-zero measurement interpretation. |
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
| `metadata/zz4_wave1_kernel_manifest.json` | Confirms reconstructed hardware kernels are `24 x 24`, have no missing entries, use measured diagonal, and retain diagnostic PSD metadata. |
| `hardware_kernels/zz4_H0_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H0` / `M0`. |
| `hardware_kernels/zz4_H1_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H1` / `M1`. |
| `hardware_kernels/zz4_H2_kernel.npy` | Wave 1 hardware-derived ZZ4 kernel for `H2` / `M2`. |
| `hardware_kernels/zz4_H0_kernel.csv` | CSV representation of the `H0` / `M0` hardware-derived kernel. |
| `hardware_kernels/zz4_H1_kernel.csv` | CSV representation of the `H1` / `M1` hardware-derived kernel. |
| `hardware_kernels/zz4_H2_kernel.csv` | CSV representation of the `H2` / `M2` hardware-derived kernel. |
| `hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv` | Per-PUB reconstruction-audit table comparing redundant coordinate/pair identifiers against the circuit-index ledger. |
| `metadata/zz4_wave1_kernel_reconstruction_audit.json` | Reconstruction-audit summary; records no coordinate or pair-identifier mismatch across the 900 configurations. |

## Hardware analysis artifacts

| Path | Purpose |
| --- | --- |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Tabular Wave 1 geometry and distortion metrics. Supplies RMSE, CKA, KTA, effective rank, variance, and PSD diagnostics. |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable Wave 1 distortion summary. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` | Robustness diagnostics, including diagonal sensitivity, leave-one-window-out jackknife summaries, and paired descriptive contrasts. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.json` | Machine-readable uncertainty/robustness summary. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv` | Tabular shot-noise reference-scale decomposition, including global and matrix-aware scales, residuals, shot-share values, `hardware_offdiag_mean`, and `hardware_offdiag_variance`. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json` | Machine-readable decomposition with formulas, input paths, output paths, hardware off-diagonal probability summaries, and diagnostic caveat. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md` | Human-readable decomposition summary. |
| `hardware_analysis/qiskit_kta_cka_permutation_tests.csv` | Source-derived label-permutation reference for statevector label alignment. |
| `hardware_analysis/zz4_wave1_label_permutation_reference.csv` | Regenerable statevector ZZ4 label-permutation reference. |
| `hardware_analysis/zz4_wave1_label_permutation_reference.json` | Machine-readable label-permutation reference with multi-seed sensitivity envelope. |

## Section 3.1 billed quantum-second grounding

The inspected repository artifacts record job identifiers, submitted shots, submitted circuit counts, pair coverage, retrieved PUB counts, raw result dictionaries, and `H2` twirling metadata. They also persist the job-level IBM Quantum usage seconds: each raw-result payload carries a top-level `job_metrics` object whose `usage.quantum_seconds` field records the billed quantum seconds.

```text
job_metrics.usage.quantum_seconds == job_metrics.usage.seconds == job_metrics.bss.seconds
H0 = 80, H1 = 80, H2 = 84
```

The total billed usage is therefore:

```text
244 quantum seconds ~= 4.07 minutes
```

`scripts/verify_section3_1_support_files.sh` enforces this as a required invariant and additionally checks that the `job_metrics.timestamps` fields are present and monotonic.

## Section 3.2 main distortion-metric grounding

Section 3.2 uses:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
```

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Centered KTA hw | Eff. rank hw | min eig | PSD rel. Fro. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741 | 0.827 | 0.0490 | 0.0878 | 0.0262 | 0.569 | 0.933 | 0.183 | 21.18 | 0.429 | `<2e-15` |
| `M1` | `H1` | 0.775 | 0.843 | 0.0473 | 0.0864 | 0.0261 | 0.564 | 0.937 | 0.181 | 21.22 | 0.462 | `<2e-15` |
| `M2` | `H2` | 0.944 | 0.986 | 0.0257 | 0.0427 | 0.0162 | 0.264 | 0.989 | 0.171 | 19.79 | 0.232 | `<2e-15` |

The verification script `scripts/verify_section3_2_support_files.sh` enforces the Section 3.2 invariants, including complete metric rows, blank/NaN correlation-test p-value columns, positive uncorrected minimum eigenvalues, roundoff-scale PSD projection diagnostics, and `H2` best observed point-estimate ordering for statevector geometry survival.

## Section 3.3 statistical support and label-alignment grounding

Section 3.3 uses:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_label_permutation_reference.csv
hardware_analysis/zz4_wave1_label_permutation_reference.json
```

Point estimates and leave-one-window-out jackknife standard errors are:

| Metric | Domain | `M0/H0` | `M1/H1` | `M2/H2` |
| --- | --- | ---: | ---: | ---: |
| Spearman | off-diagonal | 0.741297 +/- 0.051669 | 0.774951 +/- 0.045891 | 0.943744 +/- 0.012376 |
| Pearson | off-diagonal | 0.827253 +/- 0.085944 | 0.842774 +/- 0.062777 | 0.986203 +/- 0.004460 |
| MAE | off-diagonal | 0.049036 +/- 0.007897 | 0.047290 +/- 0.008294 | 0.025726 +/- 0.003549 |
| RMSE | off-diagonal | 0.087770 | 0.086428 | 0.042727 |
| CKA | full matrix | 0.933391 +/- 0.021873 | 0.937373 +/- 0.019001 | 0.988668 +/- 0.002567 |
| Centered KTA | full matrix | 0.183308 +/- 0.036223 | 0.181463 +/- 0.035045 | 0.171025 +/- 0.035962 |

RMSE is point-estimate only; no leave-one-window jackknife row or paired contrast is persisted for RMSE.

The fixed-seed statevector permutation reference is:

| Kernel | Source metric label | Alignment convention | Observed | Null mean | Null SD | Null q95 | Null q99 | p_upper_tail | p_two_sided_centered | p_two_sided_2min | n_perm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | centered label alignment | 0.1585110924 | 0.1709786387 | 0.0355291291 | 0.2353874561 | 0.2681052758 | 0.5988 | 0.7294 | 0.8024 | 5000 |
| `zz4` | `KTA` | uncentered label alignment | 0.1329093895 | 0.1433632571 | 0.0297906903 | 0.1973691723 | 0.2248026179 | 0.5988 | 0.7294 | 0.8024 | 5000 |

No hardware-regime label-permutation p-values are persisted or claimed.

## Section 3.4 central synthesis: CKA/KTA tension and shot-noise grounding

Section 3.4 uses the Section 3.2 and 3.3 outputs and the finite-shot reference-scale decomposition to state the central synthesis: the configuration with the highest hardware-vs-statevector fidelity is not the configuration with the largest observed hardware centered KTA.

| Manuscript label | Artifact regime | CKA | CKA loss | Hardware KTA | Statevector KTA | Delta_KTA | RMSE | Matrix residual |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 | 0.0877704676 | 0.0873804024 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 | 0.0864275384 | 0.0860335250 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 | 0.0427274195 | 0.0418676576 |

The geometry-fidelity ordering is `H2` best, while the absolute hardware centered-KTA ordering is `H0 > H1 > H2`. `H2` has the smallest KTA uplift and is closest to the statevector KTA. The CKA (fidelity) ordering is window-resolved (CKA contrasts z_desc = 3.09, 2.83); the absolute centered-KTA ordering is not (|z_desc| <= 0.87).

The shot-noise decomposition used in Section 3.4 is:

| Manuscript label | Artifact regime | RMSE | sigma_ref_global | residual_global | ShotShare_global | sigma_shot_matrix | residual_matrix | ShotShare_matrix |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% | 0.008266 | 0.087380 | 0.89% |
| `M1` | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% | 0.008243 | 0.086034 | 0.91% |
| `M2` | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% | 0.008528 | 0.041868 | 3.98% |

`scripts/verify_section3_4_support_files.sh` enforces the following Section 3.4 invariants:

- required support files and scripts are present;
- manuscript drafts such as `NewSection_3.4.md`, `NewSection_3.4_Revised*.md`, and `NewSection_3.4_*Instructions.md` are not present in the repository root;
- distortion metrics contain exactly three rows for `H0`, `H1`, and `H2`, with `n = 24` and 1024 submitted shots;
- correlation-test p-value columns remain blank/NaN;
- `H2` has the highest CKA and the smallest CKA loss;
- `H0` has the largest absolute hardware centered KTA;
- all hardware centered-KTA uplifts are positive, and `H2` has the smallest uplift;
- `H2` has the smallest RMSE and matrix-aware residual;
- all observed RMSE values exceed both finite-shot reference scales;
- matrix-aware shot share is below 5% for all regimes;
- KTA paired jackknife contrasts are not window-resolved;
- statevector centered label alignment remains below the permutation-null mean, with `p_upper_tail = 0.5988`;
- the shot-noise decomposition is retained as diagnostic quadrature bookkeeping, not a physical noise model.

## Supported and archival scripts

| Path | Purpose |
| --- | --- |
| `scripts/08b_audit_kernel_reconstruction.py` | Audits coordinate and pair-identifier consistency between raw retrieved PUB metadata and the circuit-index ledger. |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Regenerates direct distortion metrics from persisted kernels and statevector reference. |
| `scripts/09c_wave1_distortion_uncertainty.py` | Regenerates leave-one-window-out jackknife, paired descriptive contrasts, diagonal-sensitivity checks, and directed-versus-unique equivalence checks. |
| `scripts/09d_shot_noise_reference_scale_decomposition.py` | Regenerates Section 2.12 / Section 3.4 finite-shot reference-scale decomposition; supports `--check`. |
| `scripts/09e_label_permutation_reference.py` | Regenerates and checks the Section 2.13 / Section 3.3 / Section 3.4 statevector label-permutation reference. |
| `scripts/common.py` | Legacy shared utility module retained for archival/source-context provenance; not required by the supported direct reproduction scripts. |
| `scripts/copy_section3_1_support_files.sh` | Idempotently copies Section 3.1 support artifacts from the upstream source tree into the flat reproducibility layout if files are absent or changed. |
| `scripts/verify_section3_1_support_files.sh` | Verifies job manifests, retrieval manifest, raw-result counts, shot counts, `H2` randomization metadata, billed quantum seconds, and long-form kernel-entry counts needed by Section 3.1. |
| `scripts/publish_section3_1_updates.sh` | Runs Section 3.1 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_1_copy_verify_publish.sh` | Runs Section 3.1 copy, verify, and publish in sequence. |
| `scripts/copy_section3_2_support_files.sh` | Idempotently copies Section 3.2 support inputs from the upstream source tree if files are absent or changed. |
| `scripts/verify_section3_2_support_files.sh` | Verifies the Section 3.2 metric table, point-estimate ordering, PSD diagnostics, KTA-uplift boundary, and off-diagonal variance-retention pattern. |
| `scripts/publish_section3_2_updates.sh` | Runs Section 3.2 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_2_copy_verify_publish.sh` | Runs Section 3.2 copy, direct metric regeneration, verify, and publish in sequence. |
| `scripts/copy_section3_3_support_files.sh` | Idempotently copies Section 3.3 support inputs and the static permutation provenance table if files are absent or changed. |
| `scripts/verify_section3_3_support_files.sh` | Verifies Section 3.3 jackknife table values, paired descriptive contrasts, RMSE point-estimate-only status, KTA/CKA tension, diagonal sensitivity, and label-permutation reference. |
| `scripts/publish_section3_3_updates.sh` | Runs Section 3.3 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_3_copy_verify_publish.sh` | Runs Section 3.3 copy, direct metric regeneration, label-permutation regeneration/check, verify, and publish in sequence. |
| `scripts/copy_section3_4_support_files.sh` | Idempotently copies Section 3.4 support inputs and outputs; excludes Section 3.4 manuscript drafts. |
| `scripts/verify_section3_4_support_files.sh` | Verifies Section 3.4 KTA/CKA-tension ordering, finite-shot reference-scale decomposition, residual-distortion interpretation, and statevector label-permutation boundary. |
| `scripts/publish_section3_4_updates.sh` | Runs Section 3.4 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_4_copy_verify_publish.sh` | Runs Section 3.4 copy, direct metric regeneration, shot-noise check, label-permutation check, verification, and publishing in sequence. |
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
  ! -name 'NewSection_3.4.md' \
  ! -name 'NewSection_3.4_Revised*.md' \
  ! -name 'NewSection_3.4_*Instructions.md' \
  ! -path './checksums/SHA256SUMS.txt' \
  -print0 \
  | sort -z \
  | xargs -0 shasum -a 256 \
  > checksums/SHA256SUMS.txt

shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, Python bytecode caches, environment secrets, `.DS_Store`, local-only transfer scripts, ignored provenance sidecars, manuscript draft files, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival, hardware-distortion analysis, statistical diagnostics, shot-noise reference-scale diagnostics, and repository-grounded Results-section summaries only. It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory.

The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope.

CKA, centered KTA, leave-one-window-out jackknife contrasts, source-derived and regenerable statevector label-permutation diagnostics, shot-noise reference-scale decomposition, Section 3.1 hardware-execution accounting, Section 3.2 main distortion metrics, Section 3.3 statistical support diagnostics, and Section 3.4 KTA/CKA tension are descriptive diagnostics, not classifier-performance metrics.

For Section 3.4, `M2/H2` is the best geometry-preserving configuration and the configuration closest to the statevector KTA; it is not claimed to be a better or worse classifier. Hardware KTA inflation is interpreted as distortion rather than supervised improvement. The shot-noise decomposition indicates that residual hardware distortion dominates the observed RMSE discrepancy, but it is not a physical noise-model fit.

No license update is required for the addition of Section 3.4 documentation or the Section 3.4 support-file verification scripts.
