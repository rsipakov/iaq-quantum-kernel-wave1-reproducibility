# IAQ Quantum Kernel Wave 1 Reproducibility Package

This repository is a curated reproducibility package for the manuscript Materials and Methods section, including:

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

The package preserves the non-sensitive artifacts required to support the frozen ZZ4 Wave 1 statevector-to-hardware kernel-survival and hardware-distortion analysis. It is derived from the working repository:

```text
rsipakov/QuantumKernel
```

Only non-sensitive files required to support the manuscript claims are included. IBM Quantum tokens, local credentials, IDE state, local virtual environments, and machine-specific artifacts are excluded.

## Reproducibility scope

This repository is an artifact-level reproducibility package for the frozen Wave 1 ZZ4 IBM Quantum hardware analysis. It supports reproduction of the reported kernel reconstruction audit, geometry-distortion metrics, CKA/KTA diagnostics, jackknife and diagonal-robustness checks, shot-noise reference-scale decomposition, and Section 2.13 statistical-analysis policy from persisted frozen artifacts.

This repository is not intended to reproduce the full upstream IAQ dataset construction, preprocessing, feature engineering, IBM Quantum job submission, or original execution environment end-to-end. The original numbered execution scripts are retained only as archival provenance.

The supported reproduction path is:

1. `scripts/08b_audit_kernel_reconstruction.py`
2. `scripts/09b_analyze_wave1_distortion_direct.py`
3. `scripts/09c_wave1_distortion_uncertainty.py`
4. `scripts/09d_shot_noise_reference_scale_decomposition.py --check`
5. `scripts/09e_label_permutation_reference.py --check`

Section 2.13 additionally uses the static source-derived label-permutation reference artifact:

```text
hardware_analysis/qiskit_kta_cka_permutation_tests.csv
```

The historical table is a static source-derived reference: it is not produced by any script in this package and no permutation seed is preserved. The regenerable in-package reference is `hardware_analysis/zz4_wave1_label_permutation_reference.csv`, produced by `scripts/09e_label_permutation_reference.py` (fixed reference seed and multi-seed sensitivity). Its `--check` mode validates the static copy without rewriting the persisted CSV/JSON artifacts.

## Supported reproduction commands

From the repository root:

```bash
python scripts/08b_audit_kernel_reconstruction.py --project-root .
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
python scripts/09e_label_permutation_reference.py --project-root . --check
```

Expected high-level checks:

- kernel reconstruction audit reports coordinate and pair-identifier consistency;
- distortion metrics are regenerated for H0, H1, and H2;
- uncertainty diagnostics are regenerated;
- shot-noise decomposition check passes against the persisted output table;
- label-permutation reference check validates the static source-derived copy against the regenerable in-package reference;
- Section 2.13 statistical statements are traceable to the persisted distortion, uncertainty, and label-permutation artifacts.

These commands verify numerical reproduction, not byte-for-byte identity of regenerated files. Several supported scripts write `created_utc` timestamps and floating-point eigensolver diagnostics that may differ at roundoff scale across machines. Do not use SHA-256 hashes of regenerated timestamped outputs as the numerical-reproduction criterion.

The `offdiag_spearman_pvalue` and `offdiag_pearson_pvalue` columns in `hardware_analysis/zz4_wave1_distortion_metrics.csv` are retained for schema compatibility and intentionally left blank/NaN in the supported minimal workflow. They are not used for any manuscript claim because kernel entries are dependent observations.

## Archival code

The original numbered scripts `scripts/00_*` through `scripts/10_*` are archival records from the source execution environment and have been moved to `scripts/archive_original_execution_pipeline/`. They are not the supported reproduction path for this flat public package unless explicitly restored and documented.

The historical preprocessing code has been moved to `archive_legacy_preprocessing/`. It is retained only as source-context provenance; the supported Wave 1 analysis consumes the frozen prepared artifacts already included in this repository.

## Scope

- Domain: real indoor air-quality duplicate-sensor monitoring data
- Prediction target: `event_onset_next_1h` / `y_event_onset_next_1h`
- Feature set: `F_quantum_4`
- Feature map / kernel family: `ZZ4`
- Input dimension: 4 train-scaled pollutant features
- Frozen subset: `N = 24` fixed observation windows
- Frozen hardware split: 16 train windows + 8 test windows
- Frozen labels for KTA: `0 -> -1` and `1 -> +1`, ordered by `hardware_row_order`
- Frozen signed-label balance: 12 negative labels and 12 positive labels
- Statevector reference: exact ZZ4 squared-fidelity kernel
- Pair inventory: 300 unordered upper-triangular pairs including diagonal entries
- Unique unordered off-diagonal pairs: 276
- Diagonal entries: 24
- Off-diagonal matrix entries used for entrywise distortion metrics: 552 directed entries with `i != j`
- Full-matrix entries used for CKA and centered KTA: complete `24 x 24` centered matrices, including the measured hardware diagonal
- Hardware backend: `ibm_fez`
- Primitive: Qiskit Runtime `SamplerV2`
- Artifact hardware-regime labels: `H0`, `H1`, `H2`
- Manuscript execution-configuration labels: `M0`, `M1`, `M2`
- Label mapping: `M0 = H0`, `M1 = H1`, `M2 = H2`
- Fidelity circuits: 900 total = 300 pairs x 3 regimes
- Originally planned shots: 4096 per circuit
- Submitted shots in the reported Wave 1 execution: 1024 per circuit
- Raw retrieved results: 300 PUB results per regime, three regimes
- Reconstructed hardware kernels: three complete `24 x 24` matrices
- Kernel-reconstruction diagonal policy: measured diagonal
- Kernel-reconstruction symmetrization policy: average duplicate entries, then mirror
- PSD policy: diagnostic only; the uncorrected minimum eigenvalue is retained
- Geometry metrics: Spearman, Pearson, MAE, RMSE, median absolute error, maximum absolute error, off-diagonal variance, effective rank, centered kernel alignment, and centered kernel-target alignment
- RMSE, median and maximum absolute error, off-diagonal variance, and effective rank are reported as point estimates only; no window-level jackknife is persisted for them.
- Section 2.12 finite-shot diagnostic: global shot-noise reference scale plus matrix-aware plug-in shot scale computed from reconstructed off-diagonal all-zero probabilities
- Section 2.13 statistical unit: frozen observation window, not an individual kernel entry
- Section 2.13 resampling: leave-one-window-out jackknife for Spearman, Pearson, MAE, CKA, and centered KTA
- Section 2.13 paired contrasts: `M1-M0`, `M2-M1`, and `M2-M0`, reported as descriptive jackknife contrast ratios, not formal tests
- Section 2.13 label-permutation reference: source-derived static ZZ4/RMA6 statevector label-alignment permutation table with 5,000 permutations; only the ZZ4 statevector rows are used for the manuscript Section 2.13 label-permutation statement
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis
- Claim scope: no quantum-advantage claim and no hardware classifier-superiority claim

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, the frozen subset, the pair inventory, the reconstruction rules, or the distortion-metric definitions.

## Section 2.1: dataset and prediction context

The study uses real duplicate-sensor indoor air-quality data organized as a forecasting dataset with a 30-minute window stride and a one-hour prediction horizon. The prediction task is binary event-onset forecasting: for each eligible time window, the target records whether a new air-quality event onset occurs within the next hour. In the source workflow this target is `event_onset_next_1h`; in the frozen hardware subset it is stored as `y_event_onset_next_1h`.

The hardware pilot uses the compact quantum feature set `F_quantum_4`, comprising four one-hour pollutant summary features:

```text
pm25_mean_last_1h
pm10_mean_last_1h
hcho_mean_last_1h
tvoc_mean_last_1h
```

The preprocessing policy is train-only: missing values are imputed from the training data, features are min-max scaled to `[0, pi]`, and values outside the training range in later splits are clipped. The full event-onset dataset provides the prediction context, but the quantum-hardware analysis is restricted to the pre-authorized frozen `N = 24` subset.

Relevant artifacts:

```text
config/config.py
archive_legacy_preprocessing/preprocessing/data.py
archive_legacy_preprocessing/preprocessing/feature_maps.py
metadata/qiskit_stage_v5_scaling_report.csv
frozen_subset/hardware_subset_event_onset_next_1h.csv
metadata/statevector_reference_metadata.json
```

## Section 2.2: frozen subset

The package uses a fixed `N = 24` subset of observation windows. The subset, inclusion criteria, and acceptance thresholds used for compile-gate and stability checks were fixed before IBM hardware execution authorization and were not modified after hardware results were obtained.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

Relevant artifacts:

```text
frozen_subset/hardware_subset_event_onset_next_1h.csv
metadata/zz_only_pilot_operational_plan.json
metadata/zz_only_step8_execution_manifest.json
metadata/v9_audit_freeze_manifest.json
metadata/zz4_subset_seed_stability_summary.json
decision_records/zz4_wave1_decision_record.json
```

## Section 2.3: ZZ4 quantum feature map

The Wave 1 hardware pilot uses a fixed four-dimensional ZZ feature map, denoted `ZZ4`, applied to the train-scaled `F_quantum_4` pollutant feature vector. The same feature-map configuration defines both the statevector reference and the hardware fidelity circuits. The statevector kernel is the exact squared-fidelity kernel,

```text
K_sv(i,j) = |<phi(x_i)|phi(x_j)>|^2
```

on the frozen `N = 24` subset. Each hardware kernel entry is estimated by a compute-uncompute fidelity circuit using the all-zero probability.

Relevant artifacts:

```text
archive_legacy_preprocessing/preprocessing/feature_maps.py
config/wave1_scope.json
metadata/zz4_wave1_feature_map_spec.json
metadata/statevector_reference_metadata.json
statevector_reference/zz4_K_all_all.npy
circuits/zz4_wave1_circuit_index.csv
circuits/zz4_wave1_circuits.qpy
```

## Section 2.4: pair inventory

The pair inventory is the fixed coordinate ledger for the complete upper triangle:

```text
P = {(i,j): 0 <= i <= j < 24}
276 off-diagonal pairs + 24 diagonal entries = 300 pair entries
```

For Wave 1, all 300 rows are included in the full kernel and no sentinel pairs are designated. Pair inclusion is label-blind by construction.

Relevant artifacts:

```text
metadata/zz_only_step8_pair_inventory.csv
metadata/zz_only_step8_circuit_inventory.csv
metadata/zz4_wave1_circuit_build_manifest.json
circuits/zz4_wave1_circuit_index.csv
```

## Section 2.5: IBM Quantum hardware protocol

Wave 1 was executed on the IBM Quantum backend `ibm_fez` using Qiskit Runtime `SamplerV2`. Three Sampler-level regimes were defined:

| Artifact regime | Manuscript label | Runtime distinction |
| --- | ---: | --- |
| `H0` | `M0` | Baseline Sampler configuration; dynamical decoupling, gate twirling, and measurement twirling off. |
| `H1` | `M1` | Dynamical decoupling only; `XX` sequence, `alap` scheduling, middle extra-slack distribution; twirling off. |
| `H2` | `M2` | Gate/Pauli twirling only; dynamical decoupling and measurement twirling off; `active-accum` accumulation strategy. |

The reported hardware execution used 1024 submitted shots per circuit. The retrieval manifest records all three jobs as `DONE`, with 300 retrieved PUB results per regime.

Relevant artifacts:

```text
metadata/zz4_wave1_runtime_options.json
metadata/zz4_wave1_runtime_options_sha256.txt
metadata/zz_only_step9_live_backend_metadata.json
hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json
hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv
job_metadata/zz4_wave1_job_manifest.json
job_metadata/zz4_wave1_job_manifest.csv
job_metadata/zz4_wave1_job_manifest_H0_1024.json
job_metadata/zz4_wave1_job_manifest_H1_1024.json
job_metadata/zz4_wave1_job_manifest_H2_1024.json
job_metadata/zz4_wave1_retrieval_manifest.json
logs/zz4_wave1_submission_log.md
logs/zz4_wave1_retrieval_log.md
hardware_results/zz4_H0_raw_results.json
hardware_results/zz4_H1_raw_results.json
hardware_results/zz4_H2_raw_results.json
```

## Section 2.6: execution configurations

The persisted artifacts use hardware-regime labels `H0`, `H1`, and `H2`. The manuscript uses `M0`, `M1`, and `M2` to avoid confusion between the artifact label `H0` and conventional null-hypothesis notation.

| Manuscript label | Artifact label | Configuration |
| --- | ---: | --- |
| `M0` | `H0` | Baseline Sampler configuration |
| `M1` | `H1` | Dynamical-decoupling configuration |
| `M2` | `H2` | Gate-twirling configuration |

This alias is a reporting convention only. It does not create additional circuits, jobs, kernels, or analysis outputs.

## Section 2.7: kernel reconstruction

Kernel reconstruction maps retrieved SamplerV2 count dictionaries back to the preserved circuit-index ledger, converts each result into the all-zero probability, and assembles one `24 x 24` matrix per regime.

| Artifact regime | Manuscript label | CSV | NumPy |
| --- | --- | --- | --- |
| `H0` | `M0` | `hardware_kernels/zz4_H0_kernel.csv` | `hardware_kernels/zz4_H0_kernel.npy` |
| `H1` | `M1` | `hardware_kernels/zz4_H1_kernel.csv` | `hardware_kernels/zz4_H1_kernel.npy` |
| `H2` | `M2` | `hardware_kernels/zz4_H2_kernel.csv` | `hardware_kernels/zz4_H2_kernel.npy` |

Relevant artifacts:

```text
scripts/08b_audit_kernel_reconstruction.py
metadata/zz4_wave1_kernel_manifest.json
metadata/zz4_wave1_kernel_reconstruction_audit.json
hardware_kernels/zz4_wave1_kernel_entries_long.csv
hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv
hardware_kernels/zz4_H0_kernel.npy
hardware_kernels/zz4_H1_kernel.npy
hardware_kernels/zz4_H2_kernel.npy
hardware_kernels/zz4_H0_kernel.csv
hardware_kernels/zz4_H1_kernel.csv
hardware_kernels/zz4_H2_kernel.csv
```

## Section 2.8: geometry and distortion metrics

The Wave 1 distortion analysis compares each reconstructed hardware kernel with the fixed ZZ4 statevector reference kernel. Entrywise agreement and error summaries are evaluated on the off-diagonal set `i != j`, giving 552 directed off-diagonal entries for `N = 24`. Matrix-level diagnostics, including CKA, effective rank, and centered KTA, are evaluated on the full symmetric `24 x 24` matrices and therefore include the measured hardware diagonal.

The primary distortion metrics are stored in:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
```

Relevant artifacts:

```text
scripts/09b_analyze_wave1_distortion_direct.py
scripts/09c_wave1_distortion_uncertainty.py
scripts/09e_label_permutation_reference.py
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_summary.json
hardware_analysis/zz4_wave1_distortion_summary.md
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

## Section 2.9: CKA — centered kernel alignment

CKA is evaluated between each hardware kernel and the statevector reference using full centered matrices. The point estimates are:

| Manuscript label | Artifact regime | CKA | CKA loss = `1 - CKA` |
| --- | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 |

Robustness diagnostics are stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`.

## Section 2.10: KTA — kernel-target alignment

Centered KTA maps frozen binary labels as `0 -> -1` and `1 -> +1`, forms `Y = y y^T`, and evaluates the centered alignment between `K` and `Y`. The point estimates are:

| Kernel / manuscript label | Artifact regime | Centered KTA | Hardware minus statevector |
| --- | ---: | ---: | ---: |
| Statevector reference | `SV` | 0.1585110924 | 0 |
| `M0` | `H0` | 0.1833084594 | +0.0247973670 |
| `M1` | `H1` | 0.1814633785 | +0.0229522861 |
| `M2` | `H2` | 0.1710248441 | +0.0125137518 |

KTA is a supervised label-geometry diagnostic. It is not classifier accuracy, not proof of prediction performance, and not evidence of quantum advantage or hardware classifier superiority.

## Section 2.11: KTA/CKA tension analysis

Section 2.11 combines the CKA and centered-KTA results without introducing new data artifacts. It compares the configuration that best preserves the intended statevector geometry with the configuration that maximizes absolute centered hardware label alignment.

| Manuscript label | Artifact regime | CKA | CKA loss | Hardware KTA | Statevector KTA | Delta_KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 |

`M2/H2` best preserves statevector geometry and has the smallest KTA uplift relative to the statevector reference, while `M0/H0` has the largest absolute hardware KTA. The KTA uplift is interpreted as class-structured kernel distortion, not as a classifier-performance improvement.

## Section 2.12: shot-noise reference-scale decomposition

Section 2.12 decomposes the off-diagonal hardware--statevector RMSE using a finite-shot diagnostic reference scale. It uses the same off-diagonal domain as the RMSE calculation, with `|Omega| = 552` directed entries.

For `S = 1024` shots, the conservative global reference scale is:

```text
sigma_shot = 1 / sqrt(2*S) = 0.0220970869121
```

This is a conservative upper reference: it exceeds the maximum per-entry binomial standard error `1/(2*sqrt(S))` by `sqrt(2)` and is not the sampling standard error of an individual kernel entry.

The global quadrature decomposition is:

| Manuscript label | Artifact regime | RMSE | sigma_shot | residual_global | ShotShare_global |
| --- | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% |
| `M1` | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% |
| `M2` | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% |

Because reconstructed hardware probabilities are available, Section 2.12 also provides a matrix-aware plug-in reference:

```text
sigma_shot_matrix = sqrt(mean_{(i,j) in Omega} p_ij * (1 - p_ij) / S)
```

| Manuscript label | Artifact regime | sigma_shot_matrix | residual_matrix | ShotShare_matrix |
| --- | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.008266 | 0.087380 | 0.89% |
| `M1` | `H1` | 0.008243 | 0.086034 | 0.91% |
| `M2` | `H2` | 0.008528 | 0.041868 | 3.98% |

This decomposition is diagnostic only. It assumes a simple finite-shot reference scale and treats shot noise and residual hardware distortion as approximately separable in quadrature. It is not a full physical noise-model decomposition.

Relevant artifacts:

```text
scripts/09d_shot_noise_reference_scale_decomposition.py
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_kernels/zz4_wave1_kernel_entries_long.csv
hardware_kernels/zz4_H0_kernel.csv
hardware_kernels/zz4_H1_kernel.csv
hardware_kernels/zz4_H2_kernel.csv
```

## Section 2.13: statistical analysis

Section 2.13 defines the statistical-analysis policy for the frozen Wave 1 package. The statistical unit is the frozen observation window, not an individual kernel entry. Kernel entries are dependent because multiple entries share the same observation window and because reconstructed kernels are symmetric.

The supported window-level uncertainty artifact is:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
```

This artifact contains:

- leave-one-window-out jackknife standard errors for Spearman, Pearson, MAE, CKA, and centered KTA;
- paired descriptive jackknife contrasts for `M1-M0`, `M2-M1`, and `M2-M0`;
- diagonal-sensitivity rows for CKA, effective rank, and centered KTA;
- directed-versus-unique off-diagonal equivalence checks.

RMSE, median and maximum absolute error, off-diagonal variance, and effective rank are reported as point estimates only; no window-level jackknife is persisted for them.

The descriptive paired contrast ratios are not formal significance tests and are not converted to p-values. No pair-entry bootstrap confidence intervals are reported. No hardware-regime label-permutation p-values are reported. Since no formal hardware-contrast p-values are generated, no Holm-Bonferroni correction is applied.

The source-derived static label-permutation reference artifact is:

```text
hardware_analysis/qiskit_kta_cka_permutation_tests.csv
```

The historical table is a static source-derived reference: it is not produced by any script in this package and no permutation seed is preserved. The regenerable in-package reference is `hardware_analysis/zz4_wave1_label_permutation_reference.csv`, produced by `scripts/09e_label_permutation_reference.py` (fixed reference seed and multi-seed sensitivity). Its `--check` mode validates the static copy without rewriting the persisted CSV/JSON artifacts.

For the ZZ4 statevector centered-alignment row, this artifact records:

| Kernel | Metric row | Observed | Null mean | Null SD | Null q95 | Null q99 | p_perm upper-tail (source field: `p_perm_two_sided`) | n_perm |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | 0.1585110924 | 0.1709625562 | 0.0352334692 | 0.2346692114 | 0.2688889140 | 0.5946810638 | 5000 |

The persisted source field `p_perm_two_sided` records an upper-tail exceedance probability $P(T_{\text{null}} \ge T_{\text{obs}})$, retained under its original name for provenance. The observed alignment lies below the permutation-null mean, so the conclusion (no alignment beyond a random-label reference) holds under both one- and two-sided conventions. An in-package regenerable reference with an explicit symmetric two-sided value is produced by `scripts/09e_label_permutation_reference.py`.

The fixed-seed in-package reference records:

| Kernel | Source metric label | Alignment convention | Observed | Null mean | Null SD | Null q95 | Null q99 | p_upper_tail | p_two_sided_centered | p_two_sided_2min | n_perm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | centered label alignment | 0.1585110924 | 0.1709786387 | 0.0355291291 | 0.2353874561 | 0.2681052758 | 0.5988 | 0.7294 | 0.8024 | 5000 |
| `zz4` | `KTA` | uncentered label alignment | 0.1329093895 | 0.1433632571 | 0.0297906903 | 0.1973691723 | 0.2248026179 | 0.5988 | 0.7294 | 0.8024 | 5000 |

In the manuscript notation, the source metric label `CKA` denotes the centered label-alignment row, equivalent to `KTA_c(K_SV, y) = CKA(K_SV, yy^T)`. The source metric label `KTA` denotes the companion uncentered alignment row and is retained for provenance only. The result is used only as a statevector random-label reference. It is not a hardware-configuration selection test and is not evidence of classifier performance.

Relevant artifacts:

```text
scripts/09c_wave1_distortion_uncertainty.py
scripts/09e_label_permutation_reference.py
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
hardware_analysis/qiskit_kta_cka_permutation_tests.csv
hardware_analysis/zz4_wave1_label_permutation_reference.csv
hardware_analysis/zz4_wave1_label_permutation_reference.json
frozen_subset/hardware_subset_event_onset_next_1h.csv
statevector_reference/zz4_K_all_all.npy
hardware_kernels/zz4_H0_kernel.npy
hardware_kernels/zz4_H1_kernel.npy
hardware_kernels/zz4_H2_kernel.npy
```

## Included materials

### Dataset and preprocessing

- `config/config.py`
- `archive_legacy_preprocessing/preprocessing/data.py`
- `archive_legacy_preprocessing/preprocessing/feature_maps.py`
- `metadata/qiskit_stage_v5_scaling_report.csv`

### Frozen subset and pair/circuit inventories

- `frozen_subset/hardware_subset_event_onset_next_1h.csv`
- `metadata/zz_only_pilot_operational_plan.json`
- `metadata/zz_only_step8_execution_manifest.json`
- `metadata/zz_only_step8_pair_inventory.csv`
- `metadata/zz_only_step8_circuit_inventory.csv`
- `metadata/v9_audit_freeze_manifest.json`
- `metadata/zz4_subset_seed_stability_summary.json`
- `circuits/zz4_wave1_circuit_index.csv`
- `circuits/zz4_wave1_circuits.qpy`

### Feature-map and statevector reference

- `config/wave1_scope.json`
- `metadata/zz4_wave1_feature_map_spec.json`
- `metadata/statevector_reference_metadata.json`
- `statevector_reference/zz4_K_all_all.npy`

### IBM hardware protocol and execution metadata

- `metadata/zz4_wave1_runtime_options.json`
- `metadata/zz4_wave1_runtime_options_sha256.txt`
- `metadata/zz_only_step9_live_backend_metadata.json`
- `metadata/zz4_wave1_circuit_build_manifest.json`
- `metadata/zz4_wave1_preflight_report.json`
- `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json`
- `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv`
- `job_metadata/zz4_wave1_job_manifest.json`
- `job_metadata/zz4_wave1_job_manifest.csv`
- `job_metadata/zz4_wave1_job_manifest_H0_1024.json`
- `job_metadata/zz4_wave1_job_manifest_H0_1024.csv`
- `job_metadata/zz4_wave1_job_manifest_H1_1024.json`
- `job_metadata/zz4_wave1_job_manifest_H1_1024.csv`
- `job_metadata/zz4_wave1_job_manifest_H2_1024.json`
- `job_metadata/zz4_wave1_job_manifest_H2_1024.csv`
- `job_metadata/zz4_wave1_retrieval_manifest.json`
- `logs/zz4_wave1_submission_log.md`
- `logs/zz4_wave1_retrieval_log.md`

### Hardware results and reconstructed kernels

- `hardware_results/zz4_H0_raw_results.json`
- `hardware_results/zz4_H1_raw_results.json`
- `hardware_results/zz4_H2_raw_results.json`
- `metadata/zz4_wave1_kernel_manifest.json`
- `metadata/zz4_wave1_kernel_reconstruction_audit.json`
- `hardware_kernels/zz4_H0_kernel.npy`
- `hardware_kernels/zz4_H1_kernel.npy`
- `hardware_kernels/zz4_H2_kernel.npy`
- `hardware_kernels/zz4_H0_kernel.csv`
- `hardware_kernels/zz4_H1_kernel.csv`
- `hardware_kernels/zz4_H2_kernel.csv`
- `hardware_kernels/zz4_wave1_kernel_entries_long.csv`
- `hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv`

### Hardware analysis and statistical artifacts

- `hardware_analysis/zz4_wave1_distortion_metrics.csv`
- `hardware_analysis/zz4_wave1_distortion_summary.json`
- `hardware_analysis/zz4_wave1_distortion_summary.md`
- `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`
- `hardware_analysis/zz4_wave1_distortion_uncertainty.json`
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv`
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json`
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md`
- `hardware_analysis/qiskit_kta_cka_permutation_tests.csv`
- `hardware_analysis/zz4_wave1_label_permutation_reference.csv`
- `hardware_analysis/zz4_wave1_label_permutation_reference.json`

### Supported reproduction scripts

- `scripts/08b_audit_kernel_reconstruction.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/09d_shot_noise_reference_scale_decomposition.py`
- `scripts/09e_label_permutation_reference.py`
- `scripts/common.py` — legacy shared utility module retained for archival/source-context provenance; the supported direct reproduction scripts `08b`, `09b`, `09c`, `09d`, and `09e` are self-contained and do not require the legacy path/runtime configuration files.

### Archival original execution scripts

- `scripts/archive_original_execution_pipeline/00_artifact_lock.py`
- `scripts/archive_original_execution_pipeline/01_capture_live_backend_metadata.py`
- `scripts/archive_original_execution_pipeline/02_lock_runtime_options.py`
- `scripts/archive_original_execution_pipeline/03_optional_backend_compile_confirmation.py`
- `scripts/archive_original_execution_pipeline/04_validate_wave1_preflight.py`
- `scripts/archive_original_execution_pipeline/05_build_zz4_wave1_circuits.py`
- `scripts/archive_original_execution_pipeline/06_submit_wave1_jobs.py`
- `scripts/archive_original_execution_pipeline/07_retrieve_wave1_results.py`
- `scripts/archive_original_execution_pipeline/08_build_hardware_kernels.py`
- `scripts/archive_original_execution_pipeline/09_analyze_wave1_distortion.py`
- `scripts/archive_original_execution_pipeline/10_create_wave1_decision_record.py`

### Environment, checksums, and repository metadata

- `environment/python_version.txt`
- `environment/pip_freeze.txt`
- `requirements.txt`
- `checksums/SHA256SUMS.txt`
- `README.md`
- `MANIFEST.md`
- `CITATION.cff`
- `LICENSE`
- `.gitignore`

## Reproducing Section 2.12

From the repository root:

```bash
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
```

The first command writes the Section 2.12 CSV/JSON/Markdown artifacts. The second command recomputes the same quantities and verifies that the persisted CSV is unchanged up to numerical tolerance.

## Reproducing Section 2.13

From the repository root:

```bash
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09e_label_permutation_reference.py --project-root .
python scripts/09e_label_permutation_reference.py --project-root . --check
head -n 5 hardware_analysis/qiskit_kta_cka_permutation_tests.csv
```

The first command regenerates the window-level jackknife and paired descriptive contrast artifact. The second command regenerates the in-package label-permutation reference. The third command validates the static source-derived copy without rewriting the persisted CSV/JSON artifacts. The final command verifies that the historical Section 2.13 label-permutation reference artifact is present. Section 2.13 does not require re-submitting IBM Quantum jobs and does not introduce a hardware-regime permutation test.

## Numerical Reproduction Verification

Run:

```bash
python scripts/08b_audit_kernel_reconstruction.py --project-root .
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
python scripts/09e_label_permutation_reference.py --project-root . --check
```

The expected result is successful execution and preservation of the reported scientific values within numerical tolerance. SHA-256 hashes verify the static curated package state, not byte-for-byte identity of regenerated timestamped/numerical outputs.

## Integrity Verification

Before regenerating outputs, verify the curated package state with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

This checksum manifest verifies the static curated repository state. It is not a byte-for-byte reproduction oracle for regenerated analysis outputs. Several supported scripts write `created_utc` timestamps and floating-point eigensolver diagnostics that may differ at roundoff scale across machines.

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, Python bytecode caches, environment secrets, `.DS_Store`, local-only transfer scripts, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only. It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory.

The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. CKA, centered KTA, leave-one-window-out jackknife contrasts, source-derived statevector label-permutation diagnostics, and shot-noise reference-scale decomposition are descriptive diagnostics, not classifier-performance metrics.

## License

This package is released under the MIT License. No license update is required for the addition of Section 2.13 documentation or the source-derived non-sensitive label-permutation reference artifact.
