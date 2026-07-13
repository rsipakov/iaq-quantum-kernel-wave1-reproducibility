# IAQ Quantum Kernel Wave 1 Reproducibility Package

This repository is a curated artifact-level reproducibility package for the Wave 1 indoor-air-quality duplicate-sensor quantum-kernel analysis. It supports manuscript **Materials and methods** sections 2.1--2.13 and **Results** sections 3.1--3.7.

The package preserves non-sensitive artifacts required to support the frozen ZZ4 Wave 1 statevector-to-hardware kernel-survival, hardware-distortion, statistical-diagnostic, label-alignment, shot-noise reference-scale, CKA/KTA-tension, dimensionless shot-noise scale-separation, optional 4096-shot finite-shot projection, and effective-rank/PSD diagnostic analyses. It is derived from the working repository:

```text
rsipakov/QuantumKernel
```

Only non-sensitive files required to support manuscript claims are included. IBM Quantum tokens, local credentials, IDE state, local virtual environments, and machine-specific artifacts are excluded.

## Reproducibility scope

This repository supports artifact-level reproduction of the manuscript components listed below.

### Materials and methods

1. Section 2.1 dataset and prediction context;
2. Section 2.2 frozen subset;
3. Section 2.3 ZZ4 quantum feature map;
4. Section 2.4 pair inventory;
5. Section 2.5 IBM Quantum hardware protocol;
6. Section 2.6 execution configurations;
7. Section 2.7 kernel reconstruction;
8. Section 2.8 geometry and distortion metrics;
9. Section 2.9 CKA -- centered kernel alignment;
10. Section 2.10 KTA -- kernel-target alignment;
11. Section 2.11 KTA/CKA tension analysis;
12. Section 2.12 shot-noise reference-scale decomposition;
13. Section 2.13 statistical-analysis policy.

### Results

1. Section 3.1 hardware-execution summary;
2. Section 3.2 main distortion metrics;
3. Section 3.3 window-level statistical support and label-alignment diagnostics;
4. Section 3.4 central synthesis: RQ3 shot-noise reference scale and the CKA/KTA tension;
5. Section 3.5 dimensionless finite-shot scale separation of the off-diagonal RMSE;
6. Section 3.6 optional projection: 4096-shot rerun;
7. Section 3.7 effective-rank and PSD diagnostics.

### Supported analytical modules

The package supports the following reproducible analytical modules: kernel reconstruction audit; statevector-to-hardware geometry-distortion metrics; CKA and centered-KTA diagnostics; leave-one-window-out jackknife, paired descriptive contrasts, and diagonal-robustness checks; statevector label-permutation reference; finite-shot reference-scale decomposition; optional 4096-shot finite-shot projection; and Section 3.7 effective-rank/PSD diagnostics.

This repository is not intended to reproduce the full upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission, or original execution environment end to end. The original numbered execution scripts are retained only as archival provenance. Section 3.6 is not a new hardware execution: it rescales finite-shot reference terms from the realized 1024-shot run to the originally planned 4096-shot budget while keeping the observed RMSE fixed. Section 3.7 introduces no new hardware execution and no new numerical analysis artifact; it reports a focused spectral/PSD reading of existing reconstruction and distortion artifacts.

## Supported numerical reproduction path

### Obtain the package and verify integrity

```bash
git clone https://github.com/rsipakov/iaq-quantum-kernel-wave1-reproducibility.git
cd iaq-quantum-kernel-wave1-reproducibility
shasum -a 256 -c checksums/SHA256SUMS.txt
```

On Linux, use `sha256sum -c checksums/SHA256SUMS.txt`. Every listed file must report `OK` (exit code 0); the manifest covers every tracked file except itself (see the Checksums section).

### Environment

The supported analytical modules require Python 3.11 (`environment/python_version.txt` records the exact version used, Python 3.11.15) and the minimal dependencies in `requirements.txt` (`numpy`, `pandas`, `tabulate`; deliberately unpinned). The exact package versions used for the original analyses are preserved in `environment/pip_freeze.txt`; to reproduce that environment precisely:

```bash
pip install -r environment/pip_freeze.txt
```

The verification commands below check numerical and artifact consistency rather than byte-for-byte regeneration. Depending on platform and library versions, regenerated diagnostics may differ at roundoff or timestamp scale; use the documented tolerances and check modes below.

### Run the supported reproduction

From the repository root:

```bash
python scripts/08b_audit_kernel_reconstruction.py --project-root .
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
python scripts/09e_label_permutation_reference.py --project-root . --check
python scripts/09j_optional_4096_shot_projection.py --project-root .
python scripts/09j_optional_4096_shot_projection.py --project-root . --check
bash scripts/verify_section3_1_support_files.sh .
bash scripts/verify_section3_2_support_files.sh .
bash scripts/verify_section3_3_support_files.sh .
bash scripts/verify_section3_4_support_files.sh .
bash scripts/verify_section3_5_support_files.sh .
bash scripts/verify_section3_6_support_files.sh .
bash scripts/verify_section3_7_support_files.sh .
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
- Section 3.5 verification confirms the dimensionless RMSE-to-shot-reference ratios, quadrature residual fractions, matrix-aware scale ordering, and diagnostic-only decomposition policy;
- Section 3.6 verification confirms the planned/executed shot-count distinction, the 4096-shot finite-shot reference projection, the fixed-RMSE projection policy, and the residual-dominance result under the projected precision budget;
- Section 3.7 verification confirms the effective-rank point estimates, the unit-diagonal effective-rank sensitivity rows, complete finite reconstructed matrices, positive uncorrected minimum eigenvalues, roundoff-scale PSD corrections, diagnostic-only PSD policy, and exclusion of `NewSection_3.7.md` from the reproducibility repository.

These commands verify numerical reproduction and artifact consistency, not byte-for-byte identity of every regenerated diagnostic file. Some supported scripts write timestamps or floating-point eigensolver diagnostics that may differ at roundoff scale across machines. The `09e` reference CSV/JSON artifacts are byte-stable under the fixed seed; its local write timestamp is emitted only to an ignored provenance sidecar.

The Section 3.6 projection artifacts are deterministic functions of the persisted Section 3.4 decomposition and the scope/runtime/job-manifest files. The Section 3.7 manuscript section is supported by existing spectral and PSD columns in `hardware_analysis/zz4_wave1_distortion_metrics.csv`, by the PSD policy and finite-entry metadata in `metadata/zz4_wave1_kernel_manifest.json`, and by the unit-diagonal sensitivity rows in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`.

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
| Full-matrix entries for CKA, centered KTA, and effective rank | Complete `24 x 24` matrices, including measured hardware diagonal |
| Hardware backend | `ibm_fez` |
| Primitive | Qiskit Runtime `SamplerV2` |
| Artifact hardware-regime labels | `H0`, `H1`, `H2` |
| Manuscript execution-configuration labels | `M0`, `M1`, `M2` |
| Label mapping | `M0 = H0`, `M1 = H1`, `M2 = H2` |
| Fidelity circuits | 900 total = 300 pairs x 3 regimes |
| Originally planned shots | 4096 per circuit |
| Submitted shots in reported Wave 1 execution | 1024 per circuit |
| Section 3.6 projected shots | 4096 per circuit, projection only |
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
| Section 3.5 dimensionless scale separation | Off-diagonal RMSE in finite-shot reference units: RMSE-to-reference ratios and quadrature residual fractions |
| Section 3.6 optional 4096-shot projection | Finite-shot reference scales rescaled to 4096 shots, with RMSE fixed to realized 1024-shot values |
| Section 3.7 effective-rank diagnostics | Full-matrix effective rank with measured hardware diagonal; unit-diagonal sensitivity reported as a diagnostic only |
| Section 3.7 PSD diagnostics | Positive uncorrected minimum eigenvalues and roundoff-scale PSD Frobenius corrections; no reported metric depends on PSD replacement |
| Purpose | Statevector-to-hardware kernel-geometry survival and distortion analysis |
| Claim scope | No quantum-advantage claim, no hardware classifier-superiority claim, and no IAQ forecasting-performance claim |

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, the frozen subset, the pair inventory, the reconstruction rules, or the distortion-metric definitions. Section 3.6 uses the planned 4096-shot count only as an optional finite-shot reference projection.

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
job_metadata/zz4_wave1_job_manifest_budget_safe_combined.json
job_metadata/zz4_wave1_job_manifest_budget_safe_combined.csv
job_metadata/zz4_wave1_retrieval_manifest.json
logs/zz4_wave1_submission_log_budget_safe_combined.md
logs/zz4_wave1_submission_log_H2_final_partial_run.md
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

## Section 2.9: CKA -- centered kernel alignment

CKA is evaluated between each hardware kernel and the statevector reference using full centered matrices.

| Manuscript label | Artifact regime | CKA | CKA loss = `1 - CKA` |
| --- | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 |

Robustness diagnostics are stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`.

## Section 2.10: KTA -- kernel-target alignment

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
sigma_shot_matrix = sqrt(mean_{Omega} p_ij * (1 - p_ij) / S)
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

| Manuscript label | Artifact regime | Job ID | Status | Shots/circuit | PUB results | Billed quantum seconds |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `M0` | `H0` | `d7vf6n3ack5s73bfc0eg` | `DONE` | 1024 | 300 | 80 |
| `M1` | `H1` | `d7vf8ocinasc738u1bhg` | `DONE` | 1024 | 300 | 80 |
| `M2` | `H2` | `d7vfbsfmrars73d84u20` | `DONE` | 1024 | 300 | 84 |

Verification script:

```text
scripts/verify_section3_1_support_files.sh
```

## Section 3.2: main distortion metrics

Section 3.2 reports the main statevector-to-hardware distortion metrics.

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | KTA_c hw | Effective rank | lambda_min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741 | 0.827 | 0.0490 | 0.0878 | 0.0262 | 0.569 | 0.933 | 0.183 | 21.18 | 0.429 |
| `M1` | `H1` | 0.775 | 0.843 | 0.0473 | 0.0864 | 0.0261 | 0.564 | 0.937 | 0.181 | 21.22 | 0.462 |
| `M2` | `H2` | 0.944 | 0.986 | 0.0257 | 0.0427 | 0.0162 | 0.264 | 0.989 | 0.171 | 19.79 | 0.232 |

Verification script:

```text
scripts/verify_section3_2_support_files.sh
```

## Section 3.3: window-level statistical support and label-alignment reference

Section 3.3 reports leave-one-window-out jackknife support for Spearman, Pearson, MAE, CKA, and centered KTA; RMSE is point estimate only. It also reports the statevector label-permutation reference.

Relevant artifacts:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
hardware_analysis/zz4_wave1_label_permutation_reference.csv
hardware_analysis/zz4_wave1_label_permutation_reference.json
hardware_analysis/qiskit_kta_cka_permutation_tests.csv
scripts/verify_section3_3_support_files.sh
```

## Section 3.4: central synthesis

Section 3.4 combines the CKA/KTA tension with the finite-shot reference-scale decomposition. It uses no additional hardware execution and no classifier-performance endpoint.

Relevant artifacts:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md
scripts/verify_section3_4_support_files.sh
```

## Section 3.5: dimensionless finite-shot scale separation

Section 3.5 expresses the Section 3.4 off-diagonal RMSE decomposition in finite-shot-reference units. It introduces no new reference scale or new kernel.

| Artifact regime | R_global | R_matrix | Residual fraction, global | Residual fraction, matrix-aware |
| ---: | ---: | ---: | ---: | ---: |
| `H0` | 3.97 | 10.62 | 93.66% | 99.11% |
| `H1` | 3.91 | 10.48 | 93.46% | 99.09% |
| `H2` | 1.93 | 5.01 | 73.25% | 96.02% |

Relevant artifacts:

```text
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md
scripts/verify_section3_5_support_files.sh
```

## Section 3.6: optional projection, 4096-shot rerun

Section 3.6 rescales only the finite-shot reference terms from the executed 1024-shot run to the originally planned 4096-shot budget. The reconstructed kernels and realized RMSE values are held fixed.

Relevant artifacts:

```text
scripts/09j_optional_4096_shot_projection.py
hardware_analysis/zz4_wave1_4096_shot_projection.csv
hardware_analysis/zz4_wave1_4096_shot_projection.json
hardware_analysis/zz4_wave1_4096_shot_projection.md
scripts/verify_section3_6_support_files.sh
```

## Section 3.7: Effective-rank and PSD diagnostics

Section 3.7 isolates the spectral and PSD diagnostics already generated by the reconstruction and distortion workflow. It introduces no new kernel, no new hardware execution, no new resampling unit, and no new classifier endpoint.

These effective-rank and PSD findings are descriptive diagnostics. They do not constitute a physical hardware-noise model or classifier result and do not provide evidence of quantum advantage.

### Effective-rank support values

| Kernel / manuscript label | Artifact regime | Effective rank, measured diagonal | Change vs statevector | Unit-diagonal sensitivity |
| --- | ---: | ---: | ---: | ---: |
| Statevector reference | `SV` | 17.9718916987 | 0 | not applicable |
| `M0` baseline | `H0` | 21.1842093174 | +3.2123176186 | +0.3053244263 |
| `M1` dynamical decoupling | `H1` | 21.2170261549 | +3.2451344562 | +0.3087419099 |
| `M2` gate twirling | `H2` | 19.7881695506 | +1.8162778519 | +0.4138341967 |

Effective rank is a full-matrix point-estimate diagnostic. No leave-one-window-out jackknife or paired effective-rank contrast is persisted, and effective rank is outside the window-level resampling scope (the persisted jackknife covers Spearman, Pearson, MAE, CKA, and centered KTA only).

### PSD support values

| Manuscript label | Artifact regime | Finite entries | Missing entries | lambda_min before clip | lambda_min after clip | PSD Frobenius abs / rel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 576 | 0 | 0.4287631111 | 0.4287631111 | `8.58e-15 / 1.63e-15` |
| `M1` | `H1` | 576 | 0 | 0.4621559357 | 0.4621559357 | `9.26e-15 / 1.76e-15` |
| `M2` | `H2` | 576 | 0 | 0.2321643891 | 0.2321643891 | `1.07e-14 / 1.91e-15` |

All three uncorrected hardware matrices are positive semidefinite at the reported precision. PSD projection is diagnostic only; the reported hardware kernels retain the measured diagonal and the uncorrected matrices.

Relevant artifacts:

```text
metadata/zz4_wave1_kernel_manifest.json
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
hardware_kernels/zz4_H0_kernel.csv
hardware_kernels/zz4_H1_kernel.csv
hardware_kernels/zz4_H2_kernel.csv
hardware_kernels/zz4_H0_kernel.npy
hardware_kernels/zz4_H1_kernel.npy
hardware_kernels/zz4_H2_kernel.npy
statevector_reference/zz4_K_all_all.npy
scripts/verify_section3_7_support_files.sh
```

## Manuscript draft exclusion

The manuscript draft file `NewSection_3.7.md` and any local Section 3.7 transfer bundles are not reproducibility artifacts and must not be committed to this repository. The Section 3.7 verifier fails if `NewSection_3.7.md`, `NewSection_3.7_*.md`, `section3_7_artifacts.zip`, or `section3_7_update_bundle.zip` is present in the repository root.

## Copy/update command sequence for Section 3.7

Set the local source repository path:

```bash
SOURCE="/path/to/source/notebooks"
```

Set the dedicated reproducibility repository path:

```bash
REPO="/path/to/iaq-quantum-kernel-wave1-reproducibility"
```

Run from the unpacked Section 3.7 update bundle:

```bash
bash scripts/run_section3_7_copy_verify_publish.sh "$SOURCE" "$REPO" "$(pwd)"
```

The copy helper skips existing dependency artifacts in the reproducibility repository and copies them from `SOURCE` only if missing. It installs the Section 3.7 verification script (`scripts/verify_section3_7_support_files.sh`) and updates `README.md` and `MANIFEST.md`. The `copy_/publish_/run_` helper scripts are shipped with the Section 3.7 update bundle and are **not** part of the published repository tree; they are therefore not listed in `checksums/SHA256SUMS.txt`. It does not copy `NewSection_3.7.md`.

## Checksums

The checksum file is:

```text
checksums/SHA256SUMS.txt
```

Regenerate from the repository root after intentional updates. This command enumerates tracked files only and excludes the checksum manifest itself:

```bash
mkdir -p checksums
git ls-files -z \
  --format='./%(path)' \
  -- . ':(exclude)checksums/SHA256SUMS.txt' \
  | xargs -0 shasum -a 256 > checksums/SHA256SUMS.txt
```

On Linux, `sha256sum` may be used instead of `shasum -a 256`.

Review `git status` and `git diff` before regeneration: every tracked file in its current state is hashed. Ignored and untracked local files are not included.

Verify a checkout against the manifest:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

On Linux: `sha256sum -c checksums/SHA256SUMS.txt`. The check must report `OK` for every listed file and exit 0.

## License

See [`LICENSE`](LICENSE) for the repository license.

## Claim boundary

The package supports kernel-geometry survival and hardware-distortion analysis only. It does not support claims of quantum advantage, hardware classifier superiority, IAQ forecasting performance, post hoc subset optimization, post hoc threshold relaxation, or uncontrolled Wave 2 expansion.
