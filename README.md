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

The package preserves the non-sensitive artifacts required to support the frozen ZZ4 Wave 1 statevector-to-hardware kernel-survival and hardware-distortion analysis. It is derived from the working repository:

```text
rsipakov/QuantumKernel
```

Only non-sensitive files required to support the manuscript claims are included. IBM Quantum tokens, local credentials, IDE state, local virtual environments, and machine-specific artifacts are excluded.

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
- Section 2.9 focus: centered kernel alignment between each hardware kernel and the statevector reference
- Section 2.9 robustness: CKA diagonal sensitivity plus leave-one-window-out CKA jackknife and paired CKA contrasts
- Section 2.10 focus: centered kernel-target alignment between each kernel and the signed label Gram matrix
- Section 2.10 robustness: KTA diagonal sensitivity plus leave-one-window-out centered-KTA jackknife and paired KTA contrasts
- Section 2.11 focus: joint CKA/KTA tension analysis comparing statevector-geometry preservation with centered label alignment
- Section 2.11 derived quantities: `CKA loss = 1 - CKA` and `Delta_KTA = KTA_hardware - KTA_statevector`
- Section 2.11 result: `M2/H2` best preserves statevector geometry and has the smallest KTA uplift, while `M0/H0` has the largest absolute centered hardware KTA
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

The statevector reference metadata records the frozen subset as 16 training observation windows and 8 test observation windows. For this subset, the ZZ4 kernel scope contains 300 unordered upper-triangular kernel evaluations, including 24 diagonal entries and 276 unique off-diagonal pairs. The experiment is therefore a statevector-to-hardware kernel-geometry survival and distortion analysis, not a quantum-advantage or hardware classifier-superiority test.

Relevant artifacts:

```text
config/config.py
preprocessing/data.py
metadata/qiskit_stage_v5_scaling_report.csv
frozen_subset/hardware_subset_event_onset_next_1h.csv
metadata/statevector_reference_metadata.json
```

## Section 2.2: frozen subset

The package uses a fixed `N = 24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset. The subset, inclusion criteria, and acceptance thresholds used for compile-gate and stability checks were fixed before IBM hardware execution authorization and were not modified after hardware results were obtained.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

Within the current Wave 1 / v9 scope, the frozen subset is not an adjustable analysis input. No observation window may be added, removed, replaced, reordered, or reweighted after hardware execution authorization. This restriction applies regardless of missingness, intermediate model behavior, hardware results, kernel distortion, diagnostic outcomes, reviewer preference, or downstream performance.

The current Wave 1 decision record reports `STOP_AFTER_WAVE1_REPORT_RESULTS`. It records the allowed subset as frozen `N = 24` only, blocks subset change and threshold relaxation within the v9 scope, and does not authorize Wave 2 execution without a new decision record.

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

The Wave 1 hardware pilot uses a fixed four-dimensional ZZ feature map, denoted `ZZ4`, applied to the train-scaled `F_quantum_4` pollutant feature vector. The four input dimensions correspond to PM2.5, PM10, HCHO, and TVOC one-hour summary features.

ZZ4 is implemented as a four-qubit ZZFeatureMap with one qubit per feature. The same feature-map configuration defines both the statevector reference and the hardware fidelity circuits. The statevector kernel is the exact squared-fidelity kernel,

```text
K_sv(i,j) = |<phi(x_i)|phi(x_j)>|^2
```

on the frozen `N = 24` subset.

Each hardware kernel entry is estimated by a compute-uncompute fidelity circuit. For a pair `(i,j)`, the hardware circuit estimates the all-zero probability after applying the feature-map inverse/product circuit. In the noiseless limit, this all-zero probability equals the squared state overlap. In the hardware execution it is estimated from SamplerV2 counts as:

```text
K_hat_r(i,j) = n_0000,r(i,j) / N_r(i,j)
```

where `r` is one of `H0`, `H1`, or `H2`. The reported Wave 1 artifacts use 1024 submitted shots per circuit rather than the originally planned 4096.

The frozen subset contains `N = 24` windows, so the upper-triangular pair inventory contains `N(N+1)/2 = 300` kernel evaluations. Wave 1 evaluates these 300 pairs under each of three regimes, producing 900 circuit-regime configurations. The hardware diagonal is retained as measured rather than forced to one. Positive-semidefinite projection is diagnostic only and does not replace the reported hardware kernels.

Relevant artifacts:

```text
preprocessing/feature_maps.py
config/wave1_scope.json
metadata/zz4_wave1_feature_map_spec.json
metadata/statevector_reference_metadata.json
statevector_reference/zz4_K_all_all.npy
circuits/zz4_wave1_circuit_index.csv
circuits/zz4_wave1_circuits.qpy
```

## Section 2.4: pair inventory

The pair inventory is the fixed coordinate ledger that determines which entries of the frozen-subset kernel were evaluated and how each entry is traced back to its circuit and samples. It is a deterministic complete upper-triangular enumeration:

```text
P = {(i,j): 0 <= i <= j < 24}
276 off-diagonal pairs + 24 diagonal entries = 300 pair entries
```

The inventory is not a random sample, not a class-balanced sample, and not an adaptive subset selected after hardware execution. Each row carries a stable pair identifier, a pair order, kernel coordinates, frozen-subset sample identifiers, a diagonal/off-diagonal type label, a symmetry-mirror flag, a Wave 1 full-kernel inclusion flag, and a sentinel-pair flag.

For Wave 1, all 300 rows are included in the full kernel and no sentinel pairs are designated. The inventory carries no active split membership or class-label information used to determine pair inclusion. Pair inclusion is therefore label-blind by construction.

The companion circuit inventory crosses the same 300 pair entries with regimes `H0`, `H1`, and `H2`, producing 900 circuit-regime records. In Wave 1 each unordered pair was measured once per regime, so the configured reconstruction policy `average_duplicate_entries_then_mirror` reduced to mirroring the measured upper triangle.

Relevant artifacts:

```text
metadata/zz_only_step8_pair_inventory.csv
metadata/zz_only_step8_circuit_inventory.csv
metadata/zz4_wave1_circuit_build_manifest.json
circuits/zz4_wave1_circuit_index.csv
```

## Section 2.5: IBM Quantum hardware protocol

Wave 1 was executed on the IBM Quantum backend `ibm_fez` using Qiskit Runtime `SamplerV2`. A live backend snapshot was recorded before submission and passed the metadata gate with no detected scope drift. The compile-confirmation artifact records a successful resource gate, with maximum compiled depth 102, maximum two-qubit-gate count 22, and at most four active data qubits.

Three Sampler-level regimes were defined:

| Artifact regime | Manuscript label | Runtime distinction |
| --- | ---: | --- |
| `H0` | `M0` | Baseline Sampler configuration; dynamical decoupling, gate twirling, and measurement twirling off. |
| `H1` | `M1` | Dynamical decoupling only; `XX` sequence, `alap` scheduling, middle extra-slack distribution; twirling off. |
| `H2` | `M2` | Gate/Pauli twirling only; dynamical decoupling and measurement twirling off; `active-accum` accumulation strategy. |

Dynamical decoupling and gate twirling were intentionally not combined in Wave 1. The actual reported hardware execution used one IBM Quantum job per regime:

| Regime | Job ID | Submitted shots per circuit | Circuits | Pairs |
| --- | --- | ---: | ---: | ---: |
| `H0` | `d7vf6n3ack5s73bfc0eg` | 1024 | 300 | 300 |
| `H1` | `d7vf8ocinasc738u1bhg` | 1024 | 300 | 300 |
| `H2` | `d7vfbsfmrars73d84u20` | 1024 | 300 | 300 |

The retrieval manifest records all three jobs as `DONE`, with 300 retrieved PUB results per regime. The raw-result artifacts store per-PUB count dictionaries and circuit metadata. The long-form kernel-entry table stores all-zero counts, observed shot counts, and raw finite-shot kernel values.

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

The persisted artifacts use hardware-regime labels `H0`, `H1`, and `H2`. The manuscript uses `M0`, `M1`, and `M2` to avoid confusion between the artifact label `H0` and the conventional null-hypothesis notation `H_0`.

| Manuscript label | Artifact label | Configuration |
| --- | ---: | --- |
| `M0` | `H0` | Baseline Sampler configuration |
| `M1` | `H1` | Dynamical-decoupling configuration |
| `M2` | `H2` | Gate-twirling configuration |

This alias is a reporting convention only. It does not create additional circuits, jobs, kernels, or analysis outputs. All persisted reconstruction and analysis artifacts remain keyed by `H0`, `H1`, and `H2`.

Relevant artifacts:

```text
metadata/zz4_wave1_runtime_options.json
job_metadata/zz4_wave1_job_manifest.json
hardware_kernels/zz4_H0_kernel.npy
hardware_kernels/zz4_H1_kernel.npy
hardware_kernels/zz4_H2_kernel.npy
```

## Section 2.7: kernel reconstruction

Kernel reconstruction was performed after IBM Quantum job retrieval and did not modify the frozen subset, the pair inventory, the execution configurations, or the circuit definitions. Retrieved SamplerV2 payloads are mapped back to the preserved circuit-index ledger, converted into all-zero probabilities, and assembled into one `24 x 24` matrix per regime.

The reconstructed matrices are persisted in both CSV and NumPy formats:

| Artifact regime | Manuscript label | CSV | NumPy |
| --- | --- | --- | --- |
| `H0` | `M0` | `hardware_kernels/zz4_H0_kernel.csv` | `hardware_kernels/zz4_H0_kernel.npy` |
| `H1` | `M1` | `hardware_kernels/zz4_H1_kernel.csv` | `hardware_kernels/zz4_H1_kernel.npy` |
| `H2` | `M2` | `hardware_kernels/zz4_H2_kernel.csv` | `hardware_kernels/zz4_H2_kernel.npy` |

The long-form table `hardware_kernels/zz4_wave1_kernel_entries_long.csv` records one row per retrieved circuit-regime configuration, including regime, PUB order, circuit identifier, pair identifier, kernel coordinates, all-zero key, all-zero count, observed shots, and raw kernel value.

The kernel manifest confirms that all three matrices are present, each has shape `24 x 24`, each has 576 finite entries, and each has zero missing entries. The diagonal is retained as measured rather than overwritten by unity. Positive-semidefinite projection is diagnostic only. The uncorrected minimum eigenvalues of the hardware kernels are positive, and the PSD correction magnitude is at float64 roundoff scale.

Relevant artifacts:

```text
scripts/08_build_hardware_kernels.py
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

The Wave 1 distortion analysis compares each reconstructed hardware kernel with the fixed ZZ4 statevector reference kernel. Entrywise agreement and error summaries are evaluated on the off-diagonal set `i != j`, giving 552 directed off-diagonal entries for `N = 24`. Matrix-level diagnostics, including centered kernel alignment (CKA), effective rank, and centered kernel-target alignment (KTA), are evaluated on the full symmetric `24 x 24` matrices and therefore include the measured hardware diagonal.

The direct reproduction script computes Spearman, Pearson, MAE, RMSE, median absolute error, maximum absolute error, off-diagonal variance, effective rank, CKA, centered KTA, and PSD diagnostics.

The persisted Wave 1 distortion metrics are:

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Effective rank | Centered KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741297 | 0.827253 | 0.049036 | 0.087770 | 0.026154 | 0.568666 | 0.933391 | 21.184209 | 0.183308 |
| `M1` | `H1` | 0.774951 | 0.842774 | 0.047290 | 0.086428 | 0.026143 | 0.563897 | 0.937373 | 21.217026 | 0.181463 |
| `M2` | `H2` | 0.943744 | 0.986203 | 0.025726 | 0.042727 | 0.016161 | 0.263978 | 0.988668 | 19.788170 | 0.171025 |

The gate-twirling configuration `M2` retains the statevector geometry most strongly across the reported agreement and error metrics: it has the largest Spearman, Pearson, and CKA values and the smallest MAE, RMSE, median absolute error, and maximum absolute error.

Effective rank and KTA are interpreted as diagnostic geometry summaries rather than agreement metrics. Both are inflated on hardware relative to the statevector reference, and the inflation is smallest under `M2`. This pattern is read as hardware-induced geometric distortion, not as evidence of improved prediction.

The robustness script records directed-versus-unique off-diagonal equivalence checks, unit-diagonal sensitivity checks, and leave-one-window-out jackknife summaries. CKA and centered KTA are full-matrix centered diagnostics; Spearman, Pearson, and entrywise errors are off-diagonal diagnostics.

Relevant artifacts:

```text
scripts/09b_analyze_wave1_distortion_direct.py
scripts/09c_wave1_distortion_uncertainty.py
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_summary.json
hardware_analysis/zz4_wave1_distortion_summary.md
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

## Section 2.9: centered kernel alignment

Section 2.9 isolates the CKA diagnostic. For any kernel matrix `K`, the implementation forms the centering matrix `H = I - 11^T/N`, computes `H K H`, and returns the Frobenius-normalized inner product between the centered hardware kernel and the centered statevector reference.

The primary CKA columns are stored in:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
```

with columns:

```text
CKA_hardware_vs_statevector
CKA_statevector_self
CKA_drop_relative_to_statevector
```

The CKA point estimates are:

| Manuscript label | Artifact regime | CKA | CKA loss = `1 - CKA` |
| --- | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 |

The diagonal-sensitivity output is stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` under the `diagonal_robustness` analysis block. When hardware diagonals are forced to one as a sensitivity check only, CKA values are 0.9299004014 (`M0`/`H0`), 0.9335071225 (`M1`/`H1`), and 0.9853398979 (`M2`/`H2`), preserving the ordering `M2 > M1 > M0`. Reported kernels retain the measured diagonal.

A leave-one-window-out jackknife for CKA is stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` under the `leave_one_window_out_jackknife` and `paired_jackknife_contrast` analysis blocks. These CKA rows use `diagonal_policy = measured_diagonal_full_matrix`, because CKA is evaluated on the full centered kernel matrix while retaining the measured hardware diagonal. The `M1 - M0` CKA contrast is unresolved at the frozen-window resampling scale (`z ≈ 0.6`), whereas `M2` is separated from both `M0` and `M1` (`z ≈ 2.8–3.1`). These values are descriptive window-level robustness diagnostics, not inferential significance tests.

CKA is a centered global geometry-survival diagnostic. It is not a classifier-performance metric, does not use labels, and does not support a hardware-superiority or quantum-advantage claim.

## Section 2.10: centered kernel-target alignment

Section 2.10 isolates the centered KTA diagnostic. The frozen binary label column `y_event_onset_next_1h` is ordered by `hardware_row_order` and mapped as `0 -> -1` and `1 -> +1`. The target kernel is `Y = y y^T`. The reported quantity is the centered alignment

```text
<K_c, Y_c>_F / (||K_c||_F ||Y_c||_F), where K_c = H K H and Y_c = H Y H.
```

The uncentered KTA functional is not used. Because the frozen label vector is balanced, `H y = y`; nevertheless the kernel matrix is still double-centered before alignment with the target.

The KTA columns are stored in:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
```

with columns:

```text
KTA_hardware
KTA_statevector
KTA_drop_relative_to_statevector
```

The centered KTA point estimates are:

| Kernel / manuscript label | Artifact regime | Centered KTA | Hardware minus statevector |
| --- | ---: | ---: | ---: |
| Statevector reference | `SV` | 0.1585110924 | 0 |
| `M0` | `H0` | 0.1833084594 | +0.0247973670 |
| `M1` | `H1` | 0.1814633785 | +0.0229522861 |
| `M2` | `H2` | 0.1710248441 | +0.0125137518 |

The hardware-centered KTA values are higher than the statevector-centered KTA. This is interpreted as class-structured kernel distortion on the frozen subset, not as improved classifier performance. `M2` is closest to the statevector KTA among the three executed configurations.

The KTA diagonal-sensitivity output is stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` under `analysis_block = diagonal_robustness` and `metric = kta_centered`. The unit-diagonal sensitivity values are 0.1856507720 (`M0`/`H0`), 0.1839754900 (`M1`/`H1`), and 0.1741450073 (`M2`/`H2`). These sensitivity calculations do not replace the measured-diagonal kernels.

A leave-one-window-out jackknife for centered KTA is stored in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` under `analysis_block = leave_one_window_out_jackknife` and `metric = kta_centered`; paired KTA contrasts are stored under `analysis_block = paired_jackknife_contrast`. The centered-KTA jackknife values are 0.1833084594 ± 0.036223 (`M0`/`H0`), 0.1814633785 ± 0.035045 (`M1`/`H1`), and 0.1710248441 ± 0.035962 (`M2`/`H2`). The paired KTA contrast ratios are unresolved at the window scale: `M1-M0 = -0.001845` (`z = -0.328255`), `M2-M1 = -0.010439` (`z = -0.776936`), and `M2-M0 = -0.012284` (`z = -0.871930`). These are descriptive robustness diagnostics, not inferential significance tests.

KTA is a supervised label-geometry diagnostic. It is not classifier accuracy, not a proof of prediction performance, and not evidence of quantum advantage or hardware classifier superiority.

## Section 2.11: KTA/CKA tension analysis

Section 2.11 combines the CKA and centered-KTA results without introducing new data artifacts. It compares the configuration that best preserves the intended statevector geometry with the configuration that maximizes the absolute centered hardware label alignment.

The derived quantities are:

```text
CKA loss = 1 - CKA_hardware_vs_statevector
Delta_KTA = KTA_hardware - KTA_statevector
```

The Section 2.11 point estimates are:

| Manuscript label | Artifact regime | CKA | CKA loss | Centered hardware KTA | Statevector KTA | Delta_KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.9333906747 | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 |
| `M1` | `H1` | 0.9373725928 | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 |
| `M2` | `H2` | 0.9886681278 | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 |

The point-estimate ranks are in tension: `M2/H2` is best by CKA and has the smallest KTA uplift relative to the statevector, while `M0/H0` has the highest absolute hardware KTA. Thus, maximizing absolute centered hardware KTA alone would select the most distorted configuration by CKA, whereas preserving the intended statevector geometry selects `M2/H2`.

The paired leave-one-window-out robustness rows in `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` support the geometry-preservation conclusion but do not resolve KTA configuration differences. CKA separates `M2` from `M0` and `M1` descriptively (`z ≈ 2.8–3.1`), whereas all centered-KTA paired contrast ratios have `|z| < 1`.

The same qualitative rank reversal is retained under the unit-diagonal sensitivity check: unit-diagonal CKA remains ordered `M2 > M1 > M0`, while unit-diagonal KTA remains ordered `M0 > M1 > M2`. The KTA/CKA tension is therefore not produced by the measured-diagonal convention.

Section 2.11 is a derived synthesis of already included artifacts. No new source-to-reproducibility data copy is required for the section beyond the files already supporting Sections 2.8--2.10.

Relevant artifacts:

```text
scripts/09b_analyze_wave1_distortion_direct.py
scripts/09c_wave1_distortion_uncertainty.py
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

## Included materials

### Dataset and preprocessing

- `config/config.py`
- `preprocessing/data.py`
- `preprocessing/feature_maps.py`
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

### Hardware analysis

- `hardware_analysis/zz4_wave1_distortion_metrics.csv`
- `hardware_analysis/zz4_wave1_distortion_summary.json`
- `hardware_analysis/zz4_wave1_distortion_summary.md`
- `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`
- `hardware_analysis/zz4_wave1_distortion_uncertainty.json`

### Reproduction scripts

- `scripts/00_artifact_lock.py`
- `scripts/01_capture_live_backend_metadata.py`
- `scripts/02_lock_runtime_options.py`
- `scripts/03_optional_backend_compile_confirmation.py`
- `scripts/04_validate_wave1_preflight.py`
- `scripts/05_build_zz4_wave1_circuits.py`
- `scripts/06_submit_wave1_jobs.py`
- `scripts/07_retrieve_wave1_results.py`
- `scripts/08_build_hardware_kernels.py`
- `scripts/08b_audit_kernel_reconstruction.py`
- `scripts/09_analyze_wave1_distortion.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/10_create_wave1_decision_record.py`
- `scripts/common.py`

The script `scripts/06_submit_wave1_jobs.py` is included for traceability only. Reproduction of the reported results should not re-submit IBM Quantum hardware jobs unless explicitly authorized by a new decision record.

## Reproducing the distortion, CKA, KTA, and KTA/CKA tension analysis

From the repository root:

```bash
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
```

The direct analysis reads:

```text
frozen_subset/hardware_subset_event_onset_next_1h.csv
statevector_reference/zz4_K_all_all.npy
hardware_kernels/zz4_H0_kernel.npy
hardware_kernels/zz4_H1_kernel.npy
hardware_kernels/zz4_H2_kernel.npy
```

and writes or updates:

```text
hardware_analysis/zz4_wave1_distortion_metrics.csv
hardware_analysis/zz4_wave1_distortion_summary.json
hardware_analysis/zz4_wave1_distortion_summary.md
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

Section 2.11 does not require a separate persisted tension-analysis script. It is obtained by reading `CKA_hardware_vs_statevector`, `CKA_drop_relative_to_statevector`, `KTA_hardware`, `KTA_statevector`, and `KTA_drop_relative_to_statevector` from `hardware_analysis/zz4_wave1_distortion_metrics.csv` and reversing the sign of `KTA_drop_relative_to_statevector` to report `Delta_KTA = KTA_hardware - KTA_statevector`. The paired CKA/KTA contrast statements come from `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`.

A successful reproduction should report all required regimes `H0`, `H1`, and `H2`, with no failure reasons in `hardware_analysis/zz4_wave1_distortion_summary.json`.

## Integrity verification

Verify the package state with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, environment secrets, `.DS_Store`, local-only transfer scripts, and the checksum file itself.

If repository files are intentionally updated, regenerate the checksum file from the repository root after all edits are complete.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory. The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. CKA and centered KTA are descriptive geometry diagnostics, not classifier-performance metrics. The KTA/CKA tension analysis treats KTA uplift as hardware-induced class-structured distortion, not as prediction-performance improvement.

The leave-one-window-out CKA and centered-KTA jackknife contrasts are descriptive robustness checks on the frozen `N = 24` window scale; they are not formal significance tests.

## License

See `LICENSE`. No license update is required for the Section 2.11 KTA/CKA tension-analysis documentation update.
