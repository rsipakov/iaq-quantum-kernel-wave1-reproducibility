# IAQ Quantum Kernel Wave 1 Reproducibility Package

This repository is a curated artifact-level reproducibility package for the Wave 1 indoor-air-quality duplicate-sensor quantum-kernel analysis. It supports manuscript **Materials and methods** sections 2.1--2.13 and **Results** sections 3.1--3.5.

The package preserves non-sensitive artifacts required to support the frozen ZZ4 Wave 1 statevector-to-hardware kernel-survival, hardware-distortion, statistical-diagnostic, label-alignment, shot-noise reference-scale, CKA/KTA-tension, and Section 3.5 dimensionless shot-noise scale-separation analyses. It is derived from the working repository:

```text
rsipakov/QuantumKernel
```

Only non-sensitive files required to support manuscript claims are included. IBM Quantum tokens, local credentials, IDE state, local virtual environments, and machine-specific artifacts are excluded.

## Reproducibility scope

This repository supports reproduction of:

1. kernel reconstruction audit;
2. statevector-to-hardware geometry-distortion metrics;
3. CKA and centered-KTA diagnostics;
4. leave-one-window-out jackknife, paired descriptive contrasts, and diagonal-robustness checks;
5. statevector label-permutation reference;
6. finite-shot reference-scale decomposition;
7. Section 2.13 statistical-analysis policy;
8. Section 3.1 hardware-execution summary;
9. Section 3.2 main distortion metrics;
10. Section 3.3 statistical support and label-alignment diagnostics;
11. Section 3.4 central synthesis: RQ3 shot-noise reference scale and the CKA/KTA tension;
12. Section 3.5 new diagnostic result: dimensionless shot-noise reference-scale decomposition.

This repository is not intended to reproduce the full upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission, or original execution environment end to end. The original numbered execution scripts are retained only as archival provenance.

The supported numerical reproduction path is:

```bash
python scripts/08b_audit_kernel_reconstruction.py --project-root .
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
python scripts/09e_label_permutation_reference.py --project-root . --check
bash scripts/verify_section3_1_support_files.sh .
bash scripts/verify_section3_2_support_files.sh .
bash scripts/verify_section3_3_support_files.sh .
bash scripts/verify_section3_4_support_files.sh .
bash scripts/verify_section3_5_support_files.sh .
```

Expected high-level checks:

- the kernel reconstruction audit reports coordinate and pair-identifier consistency;
- distortion metrics are regenerated for `H0`, `H1`, and `H2`;
- uncertainty diagnostics are regenerated;
- shot-noise decomposition check passes against the persisted output table;
- label-permutation reference check validates the static source-derived copy against the regenerable in-package reference;
- Section 3.1 verification reports three `DONE` jobs, 300 retrieved PUB results per regime, 1024 shots per retrieved entry, 900 long-form kernel-entry rows, and billed quantum seconds `H0=80`, `H1=80`, `H2=84`;
- Section 3.2 verification reports the main distortion metrics, the `M2/H2` best observed point-estimate ordering for statevector geometry survival, and roundoff-scale PSD diagnostics;
- Section 3.3 verification reports the window-level jackknife support table, confirms that no adjusted hardware-contrast p-values are generated, verifies that RMSE is point-estimate only, validates the statevector label-permutation reference, and confirms that CKA/KTA tension is interpreted as distortion rather than supervised improvement;
- Section 3.4 verification confirms the CKA/KTA-tension ordering, the finite-shot reference-scale decomposition, the residual-distortion interpretation, matrix-aware shot share below 5% in all regimes, non-window-resolved centered-KTA paired jackknife contrasts, and the absence of a hardware-regime label-permutation claim;
- Section 3.5 verification confirms the dimensionless RMSE-to-shot-reference ratios, residual variance fractions, matrix-aware scale ordering, and diagnostic-only decomposition policy.

These commands verify numerical reproduction and artifact consistency, not byte-for-byte identity of every regenerated diagnostic file. Some supported scripts write timestamps or floating-point eigensolver diagnostics that may differ at roundoff scale across machines. The `09e` reference CSV/JSON artifacts are byte-stable under the fixed seed; its local write timestamp is emitted only to an ignored provenance sidecar.

The `offdiag_spearman_pvalue` and `offdiag_pearson_pvalue` columns in `hardware_analysis/zz4_wave1_distortion_metrics.csv` are retained for schema compatibility and intentionally left blank/NaN in the supported minimal workflow. They are not used for any manuscript claim because kernel entries are dependent observations.

## Scope

| Field | Value |
| --- | --- |
| Domain | Real indoor-air-quality duplicate-sensor monitoring data |
| Prediction target | `event_onset_next_1h` / `y_event_onset_next_1h` |
| Feature set | `F_quantum_4` |
| Feature map / kernel family | `ZZ4` |
| Input dimension | Four train-scaled pollutant features |
| Frozen subset | `N = 24` fixed observation windows |
| Frozen hardware split | 16 train windows + 8 test windows |
| Frozen labels for KTA | `0 -> -1`, `1 -> +1`, ordered by `hardware_row_order` |
| Frozen signed-label balance | 12 negative labels and 12 positive labels |
| Statevector reference | Exact ZZ4 squared-fidelity kernel |
| Pair inventory | 300 unordered upper-triangular pairs including diagonal entries |
| Unique unordered off-diagonal pairs | 276 |
| Diagonal entries | 24 |
| Off-diagonal matrix entries for entrywise metrics | 552 directed entries with `i != j` |
| Full-matrix entries for CKA and centered KTA | Complete `24 x 24` centered matrices, including measured hardware diagonal |
| Hardware backend | `ibm_fez` |
| Primitive | Qiskit Runtime `SamplerV2` |
| Artifact hardware-regime labels | `H0`, `H1`, `H2` |
| Manuscript execution-configuration labels | `M0`, `M1`, `M2` |
| Label mapping | `M0 = H0`, `M1 = H1`, `M2 = H2` |
| Fidelity circuits | 900 total = 300 pairs x 3 regimes |
| Originally planned shots | 4096 per circuit |
| Submitted shots in reported Wave 1 execution | 1024 per circuit |
| Raw retrieved results | 300 PUB results per regime, three regimes |
| Reconstructed hardware kernels | Three complete `24 x 24` matrices |
| Kernel-reconstruction diagonal policy | Measured diagonal |
| Kernel-reconstruction symmetrization policy | Average duplicate entries, then mirror |
| PSD policy | Diagnostic only; uncorrected minimum eigenvalue retained |
| Section 3.1 execution jobs | One backend-mode job per executed regime |
| Section 3.1 retrieved PUB total | `3 x 300 = 900` |
| Section 3.1 observed hardware-shot total | `3 x 300 x 1024 = 921600` |
| Section 3.1 billed quantum seconds | `80 + 80 + 84 = 244` (`~4.07` min), read from `job_metrics.usage.quantum_seconds` |
| Section 3.2 main distortion metrics | Spearman, Pearson, MAE, RMSE, MedAE, MaxAE, CKA, centered KTA, effective rank, off-diagonal variance, and PSD diagnostics |
| Section 3.3 statistical support diagnostics | Jackknife SEs and paired descriptive contrasts for Spearman, Pearson, MAE, CKA, and centered KTA; RMSE point estimate only; statevector label-permutation reference |
| Section 3.4 central synthesis | KTA/CKA tension plus finite-shot reference-scale support for residual hardware distortion |
| Section 3.5 new diagnostic result | Dimensionless finite-shot scale separation: RMSE-to-reference ratios and residual variance fractions |
| Purpose | Statevector-to-hardware kernel-geometry survival and distortion analysis |
| Claim scope | No quantum-advantage claim, no hardware classifier-superiority claim, and no IAQ forecasting-performance claim |

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, the frozen subset, the pair inventory, the reconstruction rules, or the distortion-metric definitions.

## Section 2.1: dataset and prediction context

The study uses real duplicate-sensor indoor-air-quality data organized as a forecasting dataset with a 30-minute window stride and a one-hour prediction horizon. The prediction task is binary event-onset forecasting. In the source workflow the target is `event_onset_next_1h`; in the frozen hardware subset it is stored as `y_event_onset_next_1h`.

The hardware pilot uses the compact quantum feature set `F_quantum_4`:

```text
pm25_mean_last_1h
pm10_mean_last_1h
hcho_mean_last_1h
tvoc_mean_last_1h
```

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

The Wave 1 hardware pilot uses a fixed four-dimensional ZZ feature map, denoted `ZZ4`, applied to the train-scaled `F_quantum_4` pollutant feature vector. The same feature-map configuration defines both the statevector reference and the hardware fidelity circuits. The statevector kernel is the exact squared-fidelity kernel on the frozen subset.

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

Wave 1 was executed on the IBM Quantum backend `ibm_fez` using Qiskit Runtime `SamplerV2`.

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
job_metadata/zz4_wave1_job_manifest_H0_1024.csv
job_metadata/zz4_wave1_job_manifest_H1_1024.json
job_metadata/zz4_wave1_job_manifest_H1_1024.csv
job_metadata/zz4_wave1_job_manifest_H2_1024.json
job_metadata/zz4_wave1_job_manifest_H2_1024.csv
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

Section 2.8 defines the Wave 1 distortion metrics used to compare each reconstructed hardware kernel with the fixed ZZ4 statevector reference kernel. Entrywise agreement and error summaries are evaluated on the off-diagonal set `i != j`, giving 552 directed off-diagonal entries for `N = 24`. Matrix-level diagnostics, including CKA, effective rank, and centered KTA, are evaluated on the full symmetric `24 x 24` matrices and therefore include the measured hardware diagonal.

Primary distortion-metric artifact:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
```

Relevant scripts and outputs:

```text
scripts/09b_analyze_wave1_distortion_direct.py
scripts/09c_wave1_distortion_uncertainty.py
scripts/09e_label_permutation_reference.py
hardware_analysis/zz4_wave1_distortion_summary.json
hardware_analysis/zz4_wave1_distortion_summary.md
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

## Section 2.9: CKA — centered kernel alignment

CKA is evaluated between each hardware kernel and the statevector reference using full centered matrices.

| Manuscript label | Artifact regime | CKA | CKA loss = `1 - CKA` |
| --- | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 |

Robustness diagnostics are stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`.

## Section 2.10: KTA — kernel-target alignment

Centered KTA maps frozen binary labels as `0 -> -1` and `1 -> +1`, forms `Y = y y^T`, and evaluates the centered alignment between `K` and `Y`.

| Kernel / manuscript label | Artifact regime | Centered KTA | Hardware minus statevector |
| --- | ---: | ---: | ---: |
| Statevector reference | `SV` | 0.1585110924 | 0 |
| `M0` | `H0` | 0.1833084594 | +0.0247973670 |
| `M1` | `H1` | 0.1814633785 | +0.0229522861 |
| `M2` | `H2` | 0.1710248441 | +0.0125137518 |

KTA is a supervised label-geometry diagnostic. It is not classifier accuracy, not proof of prediction performance, and not evidence of quantum advantage or hardware classifier superiority.

## Section 2.11: KTA/CKA tension analysis

Section 2.11 combines CKA and centered-KTA results without introducing new data artifacts.

| Manuscript label | Artifact regime | CKA | CKA loss | Hardware KTA | Statevector KTA | Delta_KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 |

`M2/H2` best preserves statevector geometry and has the smallest KTA uplift relative to the statevector reference, while `M0/H0` has the largest absolute hardware KTA. The KTA uplift is interpreted as non-affine, label-correlated kernel distortion, not as classifier-performance improvement.

## Section 2.12: shot-noise reference-scale decomposition

Section 2.12 decomposes the off-diagonal hardware--statevector RMSE using a finite-shot diagnostic reference scale. It uses the same off-diagonal domain as the RMSE calculation, with `|Omega| = 552` directed entries.

For `S = 1024` shots, the conservative global reference scale is:

```text
sigma_ref_global = 1 / sqrt(2*S) = 0.0220970869121
```

The global quadrature decomposition is:

| Manuscript label | Artifact regime | RMSE | sigma_ref_global | residual_global | ShotShare_global |
| --- | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% |
| `M1` | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% |
| `M2` | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% |

The matrix-aware plug-in reference is:

```text
sigma_shot_matrix = sqrt(mean_{(i,j) in Omega} p_ij * (1 - p_ij) / S)
```

| Manuscript label | Artifact regime | sigma_shot_matrix | residual_matrix | ShotShare_matrix |
| --- | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.008266 | 0.087380 | 0.89% |
| `M1` | `H1` | 0.008243 | 0.086034 | 0.91% |
| `M2` | `H2` | 0.008528 | 0.041868 | 3.98% |

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

The statistical unit is the frozen observation window, not an individual kernel entry. Kernel entries are dependent because multiple entries share the same observation window and because reconstructed kernels are symmetric.

The supported window-level uncertainty artifact is:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
```

This artifact contains:

- leave-one-window-out jackknife standard errors for Spearman, Pearson, MAE, CKA, and centered KTA;
- paired descriptive jackknife contrasts for `M1-M0`, `M2-M1`, and `M2-M0`;
- diagonal-sensitivity rows for CKA, effective rank, and centered KTA;
- directed-versus-unique off-diagonal equivalence checks.

RMSE, median and maximum absolute error, off-diagonal variance, and effective rank are reported as point estimates only; no window-level jackknife is persisted for them. No formal hardware-contrast p-values are generated, so no Holm--Bonferroni correction is applied to hardware contrasts.

The source-derived static label-permutation reference artifact is:

```text
hardware_analysis/qiskit_kta_cka_permutation_tests.csv
```

The regenerable in-package reference is `hardware_analysis/zz4_wave1_label_permutation_reference.csv`, produced by `scripts/09e_label_permutation_reference.py`.

## Section 3.1: hardware execution summary

Section 3.1 reports the realized hardware-execution ledger for the three executed Wave 1 configurations.

| Configuration | Artifact label | Job ID | Status | Shots/circuit | Pair/PUB entries | Billed quantum seconds |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | `d7vf6n3ack5s73bfc0eg` | `DONE` | 1024 | 300 | 80 |
| `M1` dynamical decoupling | `H1` | `d7vf8ocinasc738u1bhg` | `DONE` | 1024 | 300 | 80 |
| `M2` gate twirling | `H2` | `d7vfbsfmrars73d84u20` | `DONE` | 1024 | 300 | 84 |

Repository-grounded Section 3.1 totals:

```text
completed jobs = 3
retrieved PUB results = 3 x 300 = 900
observed hardware shots = 3 x 300 x 1024 = 921600
billed quantum seconds = 80 + 80 + 84 = 244 (~4.07 min)
```

Relevant artifacts include job manifests, retrieval manifests, raw-result payloads, hardware-kernel entries, and `scripts/verify_section3_1_support_files.sh`.

## Section 3.2: main distortion metrics

Section 3.2 reports the main statevector-to-hardware distortion metrics for the three Wave 1 configurations.

| Configuration | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | KTA_c hw | Eff. rank hw | min eig | PSD rel. Fro. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | 0.741 | 0.827 | 0.0490 | 0.0878 | 0.0262 | 0.569 | 0.933 | 0.183 | 21.18 | 0.429 | `<2e-15` |
| `M1` dynamical decoupling | `H1` | 0.775 | 0.843 | 0.0473 | 0.0864 | 0.0261 | 0.564 | 0.937 | 0.181 | 21.22 | 0.462 | `<2e-15` |
| `M2` gate twirling | `H2` | 0.944 | 0.986 | 0.0257 | 0.0427 | 0.0162 | 0.264 | 0.989 | 0.171 | 19.79 | 0.232 | `<2e-15` |

`M2/H2` has the best observed point estimates for statevector-geometry survival. This is a descriptive fixed-subset result, not a formal significance claim.

Relevant artifacts include `scripts/09b_analyze_wave1_distortion_direct.py`, `scripts/09c_wave1_distortion_uncertainty.py`, `hardware_analysis/zz4_wave1_distortion_metrics.csv`, `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`, the statevector reference, hardware kernels, and Section 3.2 helper scripts.

## Section 3.3: statistical support and label-alignment diagnostics

Section 3.3 reports the supported pre-submission statistical support table and RQ4 label-alignment diagnostics. The table uses leave-one-window-out jackknife standard errors and paired descriptive contrast ratios, not 95% confidence intervals or adjusted p-values.

### Section 3.3 support table

| Metric | Domain | `M0/H0` | `M1/H1` | `M2/H2` | `M1-M0` paired contrast | `M2-M1` paired contrast | `M2-M0` paired contrast |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Spearman | off-diagonal | 0.7413 ± 0.0517 | 0.7750 ± 0.0459 | 0.9437 ± 0.0124 | +0.0337 ± 0.0171 (`z=1.96`) | +0.1688 ± 0.0428 (`z=3.94`) | +0.2024 ± 0.0499 (`z=4.06`) |
| Pearson | off-diagonal | 0.8273 ± 0.0859 | 0.8428 ± 0.0628 | 0.9862 ± 0.0045 | +0.0155 ± 0.0263 (`z=0.59`) | +0.1434 ± 0.0598 (`z=2.40`) | +0.1590 ± 0.0829 (`z=1.92`) |
| MAE | off-diagonal | 0.04904 ± 0.00790 | 0.04729 ± 0.00829 | 0.02573 ± 0.00355 | -0.00175 ± 0.00175 (`z=-1.00`) | -0.02156 ± 0.00501 (`z=-4.30`) | -0.02331 ± 0.00472 (`z=-4.94`) |
| RMSE | off-diagonal | 0.08777 | 0.08643 | 0.04273 | not persisted | not persisted | not persisted |
| CKA | full matrix | 0.9334 ± 0.0219 | 0.9374 ± 0.0190 | 0.9887 ± 0.0026 | +0.00398 ± 0.00635 (`z=0.63`) | +0.05130 ± 0.01662 (`z=3.09`) | +0.05528 ± 0.01954 (`z=2.83`) |
| Centered KTA | full matrix | 0.1833 ± 0.0362 | 0.1815 ± 0.0350 | 0.1710 ± 0.0360 | -0.00185 ± 0.00562 (`z=-0.33`) | -0.01044 ± 0.01344 (`z=-0.78`) | -0.01228 ± 0.01409 (`z=-0.87`) |

RMSE is point-estimate only because no window-level jackknife is persisted for it. No adjusted hardware-contrast p-values are reported because no formal hardware-contrast p-values are generated.

### Statevector label-permutation reference

The fixed-seed (`seed = 0`) in-package statevector label-permutation reference uses 5000 permutations of the balanced frozen label vector.

| Kernel | Source row | Alignment convention | Observed | Null mean | Null SD | Null q95 | Null q99 | p_upper_tail | p_two_sided_centered | p_two_sided_2min |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | centered label alignment | 0.158511 | 0.170979 | 0.035529 | 0.235387 | 0.268105 | 0.5988 | 0.7294 | 0.8024 |
| `zz4` | `KTA` | uncentered label alignment | 0.132909 | 0.143363 | 0.029791 | 0.197369 | 0.224803 | 0.5988 | 0.7294 | 0.8024 |

The observed centered statevector alignment lies below the permutation-null mean and below the 95th and 99th percentile reference values. The result does not support label alignment beyond the random-label reference.

### Section 3.3 CKA/KTA tension

| Configuration | Artifact regime | CKA loss | Hardware KTA_c | Statevector KTA_c | Delta_KTA | Unit-diagonal KTA sensitivity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | 0.066609 | 0.183308 | 0.158511 | +0.024797 | +0.002342 |
| `M1` dynamical decoupling | `H1` | 0.062627 | 0.181463 | 0.158511 | +0.022952 | +0.002512 |
| `M2` gate twirling | `H2` | 0.011332 | 0.171025 | 0.158511 | +0.012514 | +0.003120 |

`M2/H2` has the smallest CKA loss and smallest KTA uplift. The baseline has the largest hardware KTA but also the largest CKA loss. This pattern is interpreted as non-affine, label-correlated hardware distortion, not as supervised improvement.

## Section 3.4: Central synthesis — the CKA/KTA tension and the finite-shot reference scale

Section 3.4 gives the central synthesis of RQ3 and RQ4. It uses the point estimates and statistical support established in Sections 3.2 and 3.3, adds the finite-shot reference-scale decomposition, and states the interpretation boundary.

### Shot-noise reference-scale support

| Configuration | Artifact regime | RMSE | sigma_ref_global | residual_global | ShotShare_global | sigma_shot_matrix | residual_matrix | ShotShare_matrix |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% | 0.008266 | 0.087380 | 0.89% |
| `M1` dynamical decoupling | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% | 0.008243 | 0.086034 | 0.91% |
| `M2` gate twirling | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% | 0.008528 | 0.041868 | 3.98% |

All three observed RMSE values exceed both finite-shot reference scales. Under the matrix-aware plug-in calculation, finite-shot variance accounts for less than 1% of squared off-diagonal RMSE in `H0` and `H1`, and 3.98% in `H2`. The residual discrepancy is therefore dominated by hardware distortion rather than by finite-shot sampling alone.

### Cross-RQ synthesis bridge

| Configuration | Artifact regime | L_CKA | Delta_KTA | RMSE | Matrix-aware shot share |
| --- | ---: | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | 0.066609 | +0.024797 | 0.087770 | 0.89% |
| `M1` dynamical decoupling | `H1` | 0.062627 | +0.022952 | 0.086428 | 0.91% |
| `M2` gate twirling | `H2` | 0.011332 | +0.012514 | 0.042727 | 3.98% |

`M2/H2` best preserved the intended statevector geometry and had the smallest centered-KTA uplift. The configuration with the largest observed hardware centered KTA is therefore not the configuration with the smallest geometry loss, and the matrix-aware shot shares show that finite-shot variance is too small to explain the residual RMSE discrepancy by itself.

Relevant artifacts:

```text
scripts/09b_analyze_wave1_distortion_direct.py
scripts/09c_wave1_distortion_uncertainty.py
scripts/09d_shot_noise_reference_scale_decomposition.py
scripts/09e_label_permutation_reference.py
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md
hardware_analysis/qiskit_kta_cka_permutation_tests.csv
hardware_analysis/zz4_wave1_label_permutation_reference.csv
hardware_analysis/zz4_wave1_label_permutation_reference.json
frozen_subset/hardware_subset_event_onset_next_1h.csv
statevector_reference/zz4_K_all_all.npy
hardware_kernels/zz4_H0_kernel.npy
hardware_kernels/zz4_H1_kernel.npy
hardware_kernels/zz4_H2_kernel.npy
scripts/verify_section3_4_support_files.sh
```

## Section 3.5: New diagnostic result — shot-noise reference-scale decomposition

Section 3.5 isolates the finite-shot diagnostic as a dimensionless scale-separation result, avoiding duplication of the absolute decomposition already reported in Section 3.4. It reports RMSE in units of the conservative global and matrix-aware finite-shot reference scales, and reports the residual variance fraction left after quadrature subtraction of each reference.

| Configuration | Artifact regime | RMSE | sigma_shot_matrix | RMSE / sigma_ref_global | residual variance after global reference | RMSE / sigma_shot_matrix | residual variance after matrix reference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` baseline | `H0` | 0.087770 | 0.008266 | 3.97 | 93.66% | 10.62 | 99.11% |
| `M1` dynamical decoupling | `H1` | 0.086428 | 0.008243 | 3.91 | 93.46% | 10.48 | 99.09% |
| `M2` gate twirling | `H2` | 0.042727 | 0.008528 | 1.93 | 73.25% | 5.01 | 96.02% |

Section 3.5 support is checked by:

```bash
bash scripts/verify_section3_5_support_files.sh .
```

This check recomputes the decomposition with `scripts/09d_shot_noise_reference_scale_decomposition.py --check`, validates the persisted rows, verifies the scale-ratio and residual-variance values used in the manuscript section, and confirms the diagnostic-only decomposition policy.

The manuscript draft file `NewSection_3.5.md` is not an artifact to copy into this repository.

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

### Supported reproduction and Results-section helper scripts

- `scripts/08b_audit_kernel_reconstruction.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/09d_shot_noise_reference_scale_decomposition.py`
- `scripts/09e_label_permutation_reference.py`
- `scripts/verify_privacy_cleanup.sh`
- `scripts/verify_section3_1_support_files.sh`
- `scripts/verify_section3_2_support_files.sh`
- `scripts/verify_section3_3_support_files.sh`
- `scripts/verify_section3_4_support_files.sh`
- `scripts/verify_section3_5_support_files.sh`
- `scripts/common.py` — legacy shared utility module retained for archival/source-context provenance

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

## Reproducing Section 3.5

From the repository root:

```bash
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
bash scripts/verify_section3_5_support_files.sh .
```

## Numerical reproduction verification

Run:

```bash
python scripts/08b_audit_kernel_reconstruction.py --project-root .
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
python scripts/09e_label_permutation_reference.py --project-root . --check
bash scripts/verify_section3_1_support_files.sh .
bash scripts/verify_section3_2_support_files.sh .
bash scripts/verify_section3_3_support_files.sh .
bash scripts/verify_section3_4_support_files.sh .
bash scripts/verify_section3_5_support_files.sh .
```

The expected result is successful execution and preservation of the reported scientific values within numerical tolerance. SHA-256 hashes verify the static curated package state, not byte-for-byte identity of regenerated timestamped/numerical outputs.

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
  ! -name 'NewSection_3.5.md' \
  ! -name 'NewSection_3.5_*.md' \
  ! -name 'copy_section3_5_support_files.sh' \
  ! -name 'publish_section3_5_updates.sh' \
  ! -name 'run_section3_5_update_all.sh' \
  ! -path './checksums/SHA256SUMS.txt' \
  -print0 \
  | sort -z \
  | xargs -0 shasum -a 256 \
  > checksums/SHA256SUMS.txt

shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, Python bytecode caches, environment secrets, `.DS_Store`, ignored provenance sidecars, local-only transfer scripts, manuscript draft files, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival, hardware-distortion analysis, statistical diagnostics, finite-shot reference-scale diagnostics, dimensionless shot-noise scale-separation diagnostics, and repository-grounded Results-section summaries only. It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory.

The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope.

CKA, centered KTA, leave-one-window-out jackknife contrasts, source-derived and regenerable statevector label-permutation diagnostics, shot-noise reference-scale decomposition, Section 3.1 execution-summary checks, Section 3.2 main distortion metrics, Section 3.3 statistical support diagnostics, Section 3.4 KTA/CKA-tension diagnostics, and Section 3.5 scale-ratio diagnostics are descriptive diagnostics, not classifier-performance metrics.

For Section 3.5, `M2/H2` has the smallest RMSE and residual distortion term, but the residual remains the dominant variance component under both shot-noise references. This is a diagnostic scale accounting, not a physical noise-model fit and not a classifier-performance result.

## License

This package is released under the MIT License. No license update is required for the addition of Section 3.5 documentation or the Section 3.5 support-file verification script.
