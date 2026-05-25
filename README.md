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
- Statevector reference: exact ZZ4 squared-fidelity kernel
- Pair inventory: 300 unordered upper-triangular pairs including diagonal entries
- Unique unordered off-diagonal pairs: 276
- Diagonal entries: 24
- Off-diagonal matrix entries used for entrywise distortion metrics: 552 directed entries with `i != j`
- Full-matrix entries used for CKA: complete `24 x 24` centered matrices, including the measured hardware diagonal
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
- Section 2.9 robustness: CKA diagonal-sensitivity diagnostics and leave-one-window-out CKA jackknife diagnostics
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis
- Claim scope: no quantum-advantage claim and no hardware classifier-superiority claim

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, the frozen subset, the pair inventory, the reconstruction rules, or the distortion-metric definitions.

## Frozen subset policy

This reproduction package uses a fixed `N = 24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset.

```text
N = 24
No post-hoc subset replacement
No threshold relaxation
No Wave 2 execution without a new decision record
```

The frozen subset was fixed before IBM hardware execution authorization and is treated as part of the study design, not as an adjustable analysis input. Within the current Wave 1 / v9 scope, no observation window may be added, removed, replaced, reordered, or reweighted after hardware execution authorization. Wave 2 execution is excluded from the current reproduction unless explicitly authorized by a new decision record.

## Execution configuration label policy

The source artifacts retain the hardware-regime labels `H0`, `H1`, and `H2`. The manuscript uses manuscript-level labels `M0`, `M1`, and `M2` to avoid confusion between the artifact label `H0` and the conventional null-hypothesis notation $H_0$.

| Manuscript label | Artifact label | Configuration | Runtime distinction |
| --- | ---: | --- | --- |
| `M0` | `H0` | Sampler baseline | Dynamical decoupling off; gate twirling off; measurement twirling off. |
| `M1` | `H1` | Sampler + dynamical decoupling | Dynamical decoupling on with `XX`, `alap`, middle slack; twirling off. |
| `M2` | `H2` | Sampler + gate/Pauli twirling | Gate twirling on with `active-accum` and automatic randomization; dynamical decoupling and measurement twirling off. |

This relabeling is a reporting convention only. It does not create new circuits, jobs, kernels, or analysis outputs. All persisted artifacts remain keyed by `H0`, `H1`, and `H2`.

## Kernel reconstruction

Kernel reconstruction starts from the retrieved SamplerV2 result payloads and does not re-submit hardware jobs. The reconstruction workflow maps each PUB order back to the circuit-index ledger, reads the pair coordinates, computes the all-zero probability, writes the long-form kernel-entry table, and assembles one hardware kernel matrix per regime.

The reconstructed matrices are persisted in both CSV and NumPy formats:

| Artifact regime | Manuscript label | CSV | NumPy |
| --- | --- | --- | --- |
| `H0` | `M0` | `hardware_kernels/zz4_H0_kernel.csv` | `hardware_kernels/zz4_H0_kernel.npy` |
| `H1` | `M1` | `hardware_kernels/zz4_H1_kernel.csv` | `hardware_kernels/zz4_H1_kernel.npy` |
| `H2` | `M2` | `hardware_kernels/zz4_H2_kernel.csv` | `hardware_kernels/zz4_H2_kernel.npy` |

The kernel manifest confirms that all three matrices are present, each has shape `24 x 24`, each has 576 finite entries, and each has zero missing entries. The diagonal is retained as measured rather than overwritten by unity. PSD projection is diagnostic only.

## Geometry and distortion metrics

The Wave 1 distortion analysis compares each reconstructed hardware kernel with the statevector reference kernel. Entrywise agreement and error summaries are evaluated on the off-diagonal set `i != j`, giving 552 directed off-diagonal entries for `N = 24`. Matrix-level diagnostics, including centered kernel alignment (CKA), effective rank, and centered kernel-target alignment, are evaluated on the complete symmetric `24 x 24` matrices and therefore include the measured hardware diagonal.

The direct reproduction script computes Spearman, Pearson, MAE, RMSE, median absolute error, maximum absolute error, hardware and statevector off-diagonal variances, effective rank, CKA, centered KTA, and PSD diagnostics.

The persisted Wave 1 distortion metrics are:

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Effective rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741297 | 0.827253 | 0.049036 | 0.087770 | 0.026154 | 0.568666 | 0.933391 | 21.184209 |
| `M1` | `H1` | 0.774951 | 0.842774 | 0.047290 | 0.086428 | 0.026143 | 0.563897 | 0.937373 | 21.217026 |
| `M2` | `H2` | 0.943744 | 0.986203 | 0.025726 | 0.042727 | 0.016161 | 0.263978 | 0.988668 | 19.788170 |

The statevector off-diagonal variance is 0.0186558. Hardware off-diagonal variances are 0.0053865 (`H0`), 0.0052842 (`H1`), and 0.0097585 (`H2`). The statevector effective rank is 17.971892. The statevector centered kernel-target alignment is 0.158511; hardware centered KTA values are 0.183308 (`H0`), 0.181463 (`H1`), and 0.171025 (`H2`). These label-alignment values are geometry diagnostics on the frozen subset only and are not classifier-performance claims.

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

The diagonal-sensitivity output is stored in:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
```

under the `diagonal_robustness` analysis block. When hardware diagonals are forced to one as a sensitivity check only, CKA values are 0.9299004014 (`M0`/`H0`), 0.9335071225 (`M1`/`H1`), and 0.9853398979 (`M2`/`H2`), preserving the ordering `M2 > M1 > M0`. Reported kernels retain the measured diagonal.

A leave-one-window-out jackknife for CKA is stored in:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
```

under the `leave_one_window_out_jackknife` and `paired_jackknife_contrast` analysis blocks. These CKA rows use `diagonal_policy = measured_diagonal_full_matrix`, because CKA is evaluated on the full centered kernel matrix while retaining the measured hardware diagonal. The `M1 - M0` CKA contrast is unresolved at the frozen-window resampling scale (`z ≈ 0.6`), whereas `M2` is separated from both `M0` and `M1` (`z ≈ 2.8–3.1`). These values are descriptive window-level robustness diagnostics, not inferential significance tests.

CKA is a centered global geometry-survival diagnostic. It is not a classifier-performance metric, does not use labels, and does not support a hardware-superiority or quantum-advantage claim.

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
- `hardware_kernels/zz4_H0_kernel.npy`
- `hardware_kernels/zz4_H1_kernel.npy`
- `hardware_kernels/zz4_H2_kernel.npy`
- `hardware_kernels/zz4_H0_kernel.csv`
- `hardware_kernels/zz4_H1_kernel.csv`
- `hardware_kernels/zz4_H2_kernel.csv`
- `hardware_kernels/zz4_wave1_kernel_entries_long.csv`

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
- `scripts/09_analyze_wave1_distortion.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/10_create_wave1_decision_record.py`
- `scripts/common.py`

The script `scripts/06_submit_wave1_jobs.py` is included for traceability only. Reproduction of the reported results should not re-submit IBM Quantum hardware jobs unless explicitly authorized by a new decision record.

## Reproducing the distortion and CKA analysis

From the repository root:

```bash
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
```

This reads:

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
```

For robustness diagnostics, including the Section 2.9 diagonal-sensitivity check and leave-one-window-out CKA jackknife, run:

```bash
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
```

This writes or updates:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

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

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory. The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. CKA and centered kernel-target alignment are descriptive geometry diagnostics on the frozen subset and are not classifier-performance claims.

The leave-one-window-out jackknife contrasts are descriptive robustness checks on the frozen `N = 24` window scale; they are not formal significance tests.

## License

See `LICENSE`. No license update is required for the Section 2.9 CKA documentation update.
