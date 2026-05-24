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

The package preserves the non-sensitive artifacts required to support the frozen ZZ4 Wave 1 statevector-to-hardware kernel-survival and hardware-distortion analysis.

The package is derived from the working repository:

```text
rsipakov/QuantumKernel
```

Only non-sensitive files required to support the manuscript claims are included. IBM Quantum tokens, local credentials, IDE state, local virtual environments, and other machine-specific artifacts are not part of this package.

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
- Off-diagonal matrix entries used for distortion metrics: 552 directed off-diagonal entries (`i != j`)
- Hardware backend: `ibm_fez`
- Primitive: Qiskit Runtime `SamplerV2`
- Artifact hardware-regime labels: `H0`, `H1`, `H2`
- Manuscript execution-configuration labels: `M0`, `M1`, `M2`
- Label mapping: `M0` = `H0`, `M1` = `H1`, `M2` = `H2`
- Fidelity circuits: 900 total, i.e. 300 pairs x 3 regimes
- Originally planned shots: 4096 per circuit
- Submitted shots in the reported Wave 1 execution: 1024 per circuit
- Raw retrieved results: 300 PUB results per regime, three regimes
- Reconstructed hardware kernels: three complete `24 x 24` matrices
- Kernel-reconstruction diagonal policy: measured diagonal
- Kernel-reconstruction symmetrization policy: average duplicate entries, then mirror
- PSD policy: diagnostic only; do not hide the uncorrected minimum eigenvalue
- Geometry metrics: Spearman, Pearson, MAE, RMSE, median absolute error, maximum absolute error, off-diagonal variance, effective rank, centered kernel alignment, and centered kernel-target alignment
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

The frozen subset was fixed before IBM hardware execution authorization and is treated as part of the study design, not as an adjustable analysis input.

Within the current Wave 1 / v9 scope, the subset is immutable. No observation window may be added, removed, replaced, reordered, or reweighted after hardware execution authorization. This applies regardless of missingness, intermediate model behavior, hardware results, kernel distortion, diagnostic outcomes, reviewer preference, or downstream performance.

Thresholds used for inclusion, exclusion, hardware feasibility, compile-gate acceptance, subset stability, or pass/fail interpretation are frozen. Post-hoc threshold relaxation is not permitted.

Wave 2 execution is excluded from the current frozen-subset reproduction unless explicitly authorized by a new decision record. Full 300-pair Wave 2 execution is not authorized under the current scope. Any sentinel-only Wave 2 extension must preserve the frozen-subset policy and must not retroactively alter the Wave 1 subset, thresholds, or claims.

## Pair inventory policy

The Wave 1 pair inventory is a deterministic upper-triangular enumeration of the frozen `N = 24` subset. It contains all unordered off-diagonal pairs and all diagonal entries:

```text
276 off-diagonal pairs + 24 diagonal entries = 300 pair entries
```

The pair inventory is not a random sample, not a class-balanced sample, and not an adaptive subset selected after hardware execution. Each row carries a stable `pair_id`, an integer `pair_order`, the kernel coordinates `kernel_i` and `kernel_j`, the corresponding frozen-subset sample identifiers, a diagonal/off-diagonal pair label, an expected-symmetry flag, a Wave 1 full-kernel inclusion flag, and a sentinel-pair flag.

In the frozen Wave 1 inventory, `include_in_wave1_full_kernel` is `true` for all 300 rows and `sentinel_pair` is `false` for all 300 rows. The reserved split- and target-label fields are present in the schema but left unpopulated; pair rows reference samples only by opaque identifiers and carry no split membership or class label. Pair inclusion is therefore label-blind by construction.

The companion circuit inventory crosses the same 300 pair entries with the three pre-authorized Wave 1 regimes, producing 900 planned fidelity-circuit records. The reported budget-safe execution submitted 900 circuits at 1024 shots per circuit.

The configured kernel-reconstruction symmetrization policy is `average_duplicate_entries_then_mirror`. In Wave 1 it reduced to mirror-only, because each unordered pair was measured exactly once and no duplicate entries existed to average; symmetrization therefore amounted to mirroring the measured upper triangle, `K_r(j, i) = K_r(i, j)`.

## IBM Quantum hardware protocol

Wave 1 IBM Quantum execution used the backend `ibm_fez` and Qiskit Runtime `SamplerV2`. A live backend snapshot recorded backend version 2, 156 physical qubits, operational status, and a passed metadata gate with no detected scope drift.

The runtime protocol used three artifact regimes:

- `H0`: unmitigated Sampler baseline; dynamical decoupling disabled; gate and measurement twirling disabled.
- `H1`: dynamical decoupling only; `XX` sequence; `alap` scheduling; middle extra-slack distribution; twirling disabled.
- `H2`: gate/Pauli twirling only; dynamical decoupling disabled; measurement twirling disabled; automatic randomization settings; `active-accum` strategy.

`H1` and `H2` were intentionally separate. Dynamical decoupling and gate twirling were not combined in Wave 1.

Before submission, the 900 circuits were built and validated, then compiled against `ibm_fez`. The compile-confirmation artifact records a successful resource gate, maximum compiled depth 102, maximum two-qubit-gate count 22, and a four-active-qubit resource gate.

The actual reported hardware execution used one IBM Quantum job per regime:

| Artifact regime | Job ID | Submitted shots per circuit | Circuits | Pairs |
| --- | --- | ---: | ---: | ---: |
| `H0` | `d7vf6n3ack5s73bfc0eg` | 1024 | 300 | 300 |
| `H1` | `d7vf8ocinasc738u1bhg` | 1024 | 300 | 300 |
| `H2` | `d7vfbsfmrars73d84u20` | 1024 | 300 | 300 |

The retrieval manifest records all three jobs as `DONE`, with 300 retrieved PUB results per regime. The raw-result artifacts store per-PUB count dictionaries and circuit metadata. The long-form kernel-entry table stores all-zero counts, observed shot counts, and raw finite-shot kernel values. The hardware-kernel manifest records one complete `24 x 24` hardware kernel for each regime, with no missing entries and a measured-diagonal policy.

## Execution configuration label policy

The source artifacts retain the hardware-regime labels H0, H1, and H2. The manuscript uses manuscript-level execution-configuration labels M0, M1, and M2 to avoid confusion between the artifact label H0 and the conventional null-hypothesis symbol H_0. This relabeling is a reporting convention only; it does not define new circuits, new jobs, new kernels, or new analysis outputs.

| Manuscript label | Artifact label | Configuration | Runtime distinction |
| --- | ---: | --- | --- |
| `M0` | `H0` | Sampler baseline | Dynamical decoupling off; gate twirling off; measurement twirling off. |
| `M1` | `H1` | Sampler + dynamical decoupling | Dynamical decoupling on with `XX`, `alap`, middle slack; twirling off. |
| `M2` | `H2` | Sampler + gate/Pauli twirling | Gate twirling on with `active-accum` and automatic randomization; dynamical decoupling and measurement twirling off. |

All artifact filenames, JSON fields, CSV regime columns, raw-result files, kernel matrices, and checksum records remain keyed by `H0`, `H1`, and `H2`. Manuscript tables may report both labels for traceability. For manuscript notation, the label map is

```text
a(M0) = H0
a(M1) = H1
a(M2) = H2
```

and the hardware kernel for manuscript configuration `m` is the artifact kernel `K_{a(m)}`. The complete Wave 1 analysis set is therefore `{M0, M1, M2}` in manuscript notation and `{H0, H1, H2}` in the persisted artifacts. There is no fourth combined dynamical-decoupling-plus-twirling configuration in Wave 1.

## Kernel reconstruction

Kernel reconstruction starts from the retrieved SamplerV2 result payloads and does not re-submit hardware jobs. The reconstruction script maps each PUB order back to the circuit index for the same artifact regime, reads the pair coordinates `(i, j)`, computes the all-zero probability, writes the long-form kernel-entry table, and assembles one hardware kernel matrix per regime.

For each regime `H0`, `H1`, and `H2`, the raw-result JSON file contains 300 PUB entries. Each entry stores `pub_order`, a count dictionary, `shots_observed`, and circuit metadata containing `circuit_inventory_id`, `pair_id`, `pair_inventory_row`, coordinates `i` and `j`, and the regime label. For `H2`, twirling metadata are also preserved where present. The long-form table `hardware_kernels/zz4_wave1_kernel_entries_long.csv` records the derived all-zero count, observed shots, and raw kernel value for every retrieved PUB.

The reconstructed matrices are persisted in both CSV and NumPy formats:

| Artifact regime | Manuscript label | CSV | NumPy |
| --- | --- | --- | --- |
| `H0` | `M0` | `hardware_kernels/zz4_H0_kernel.csv` | `hardware_kernels/zz4_H0_kernel.npy` |
| `H1` | `M1` | `hardware_kernels/zz4_H1_kernel.csv` | `hardware_kernels/zz4_H1_kernel.npy` |
| `H2` | `M2` | `hardware_kernels/zz4_H2_kernel.csv` | `hardware_kernels/zz4_H2_kernel.npy` |

The kernel manifest confirms that all three matrices are present, each has shape `24 x 24`, each has 576 finite entries, and each has zero missing entries. The diagonal is retained as measured rather than overwritten by unity. PSD projection is diagnostic only: the manifest retains the uncorrected minimum eigenvalue and reports the Frobenius norm of the diagnostic eigenvalue-clipping correction.

| Artifact regime | Manuscript label | Minimum eigenvalue before PSD diagnostic | Missing entries | PSD correction Frobenius norm |
| --- | --- | ---: | ---: | ---: |
| `H0` | `M0` | 0.428763111071851 | 0 | 8.583547173776992e-15 |
| `H1` | `M1` | 0.46215593566687874 | 0 | 9.259630923313487e-15 |
| `H2` | `M2` | 0.23216438914772836 | 0 | 1.070945942310601e-14 |

## Geometry and distortion metrics

The Wave 1 distortion analysis compares each reconstructed hardware kernel with the statevector reference kernel on the off-diagonal matrix set `i != j`. For `N = 24`, this gives 552 directed off-diagonal entries. Because the matrices are symmetric, this is the duplicate-weighted representation of the 276 unique unordered off-diagonal pairs; the correlation coefficients and mean loss summaries are descriptive geometry summaries, not independent-sample inferential tests.

The direct reproduction script computes the following metrics:

- Spearman correlation between off-diagonal statevector and hardware entries.
- Pearson correlation between off-diagonal statevector and hardware entries.
- Mean absolute error and root-mean-squared error against the statevector kernel.
- Median absolute error and maximum absolute error against the statevector kernel.
- Hardware and statevector off-diagonal variances and their difference.
- Effective rank of the hardware and statevector kernels.
- Centered kernel alignment between each hardware kernel and the statevector reference.
- Centered kernel-target alignment using the frozen-subset binary labels.
- PSD diagnostics retained from the matrix-valued kernel check.

The persisted Wave 1 distortion metrics are:

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Effective rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741297 | 0.827253 | 0.049036 | 0.087770 | 0.026154 | 0.568666 | 0.933391 | 21.184209 |
| `M1` | `H1` | 0.774951 | 0.842774 | 0.047290 | 0.086428 | 0.026143 | 0.563897 | 0.937373 | 21.217026 |
| `M2` | `H2` | 0.943744 | 0.986203 | 0.025726 | 0.042727 | 0.016161 | 0.263978 | 0.988668 | 19.788170 |

The statevector off-diagonal variance is 0.0186558. Hardware off-diagonal variances are 0.0053865 (`H0`), 0.0052842 (`H1`), and 0.0097585 (`H2`). The statevector effective rank is 17.971892. The statevector kernel-target alignment is 0.158511; hardware KTA values are 0.183308 (`H0`), 0.181463 (`H1`), and 0.171025 (`H2`). These label-alignment values are geometry diagnostics on the frozen subset only and are not classifier-performance claims.

The distortion summary records that all required regimes are reported and that no failure reasons were recorded.

## Included materials

### Dataset and preprocessing

- `config/config.py`  
  Target and feature-set definitions, including `event_onset_next_1h` and `F_quantum_4`.

- `preprocessing/data.py`  
  Dataset loading, valid-label filtering, train-only imputation, train-only scaling to `[0, pi]`, and clipping.

- `preprocessing/feature_maps.py`  
  ZZ feature-map implementation for the `F_quantum_4 / ZZ4` kernel.

- `metadata/qiskit_stage_v5_scaling_report.csv`  
  Split counts and feature-scaling diagnostics for the full event-onset context.

### Frozen subset and pair/circuit inventories

- `frozen_subset/hardware_subset_event_onset_next_1h.csv`  
  Fixed `N = 24` subset of observation windows used for the Wave 1 ZZ4 hardware pilot.

- `metadata/zz_only_pilot_operational_plan.json`  
  Operational plan defining the ZZ-only hardware pilot scope, frozen-subset policy, allowed claims, pair counts, and Wave 2 restrictions.

- `metadata/zz_only_step8_execution_manifest.json`  
  Execution manifest recording the authorized Wave 1 scope, including frozen `N = 24`, `F_quantum_4`, `ZZ4`, pair-count metadata, and pair-inventory checksum.

- `metadata/zz_only_step8_pair_inventory.csv`  
  Deterministic 300-row upper-triangular inventory for the frozen `24 x 24` kernel.

- `metadata/zz_only_step8_circuit_inventory.csv`  
  900-row circuit inventory obtained by crossing the 300 pair entries with regimes `H0`, `H1`, and `H2`.

- `metadata/v9_audit_freeze_manifest.json`  
  Audit/freeze manifest recording the allowed subset, allowed feature set, allowed kernel, threshold policy, and freeze state.

- `metadata/zz4_subset_seed_stability_summary.json`  
  Subset-stability summary confirming that the frozen subset was not changed after hardware results.

### Feature-map and execution-scope configuration

- `config/wave1_scope.json`  
  Wave 1 scope configuration used by the circuit-build and kernel-reconstruction workflows.

- `metadata/zz4_wave1_feature_map_spec.json`  
  Manuscript-support metadata for the ZZ4 feature-map specification.

- `metadata/statevector_reference_metadata.json`  
  Statevector reference metadata for the ZZ4 feature order and the exact squared-fidelity kernel.

- `statevector_reference/zz4_K_all_all.npy`  
  Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset.

### IBM hardware protocol and execution metadata

- `metadata/zz4_wave1_runtime_options.json`  
  Locked Wave 1 runtime options for artifact regimes `H0`, `H1`, and `H2`; these correspond to manuscript execution configurations `M0`, `M1`, and `M2`, respectively.

- `metadata/zz4_wave1_runtime_options_sha256.txt`  
  Checksum for the locked runtime-options artifact.

- `metadata/zz_only_step9_live_backend_metadata.json`  
  Live backend metadata snapshot for `ibm_fez`.

- `metadata/zz4_wave1_circuit_build_manifest.json`  
  Circuit-build manifest confirming 900 built ZZ4 fidelity circuits and all-zero interpretation.

- `metadata/zz4_wave1_preflight_report.json`  
  Preflight report confirming selected backend, allowed scope, expected and observed pair/circuit counts, and secret-scan status.

- `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json`  
  Backend compile-confirmation summary for `ibm_fez`.

- `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv`  
  Per-circuit compile records for the 900 compiled circuits.

- `circuits/zz4_wave1_circuit_index.csv`  
  Circuit-order ledger linking circuit order, regime, pair identifier, pair row, and kernel coordinates.

- `circuits/zz4_wave1_circuits.qpy`  
  QPY archive of the built Wave 1 ZZ4 circuits.

- `job_metadata/zz4_wave1_job_manifest.json`  
  Combined Wave 1 IBM job manifest recording regimes `H0`, `H1`, and `H2`, 1024 submitted shots per circuit, 300 covered pairs per regime, and 900 total submitted circuits.

- `job_metadata/zz4_wave1_job_manifest.csv`  
  CSV representation of the combined Wave 1 job manifest.

- `job_metadata/zz4_wave1_job_manifest_H0_1024.json`  
  JSON job manifest for regime `H0`.

- `job_metadata/zz4_wave1_job_manifest_H0_1024.csv`  
  CSV job manifest for regime `H0`.

- `job_metadata/zz4_wave1_job_manifest_H1_1024.json`  
  JSON job manifest for regime `H1`.

- `job_metadata/zz4_wave1_job_manifest_H1_1024.csv`  
  CSV job manifest for regime `H1`.

- `job_metadata/zz4_wave1_job_manifest_H2_1024.json`  
  JSON job manifest for regime `H2`.

- `job_metadata/zz4_wave1_job_manifest_H2_1024.csv`  
  CSV job manifest for regime `H2`.

- `job_metadata/zz4_wave1_retrieval_manifest.json`  
  Retrieval manifest recording `DONE` status and 300 PUB results per regime.

- `logs/zz4_wave1_submission_log.md`  
  Submission log for Wave 1 IBM hardware jobs.

- `logs/zz4_wave1_retrieval_log.md`  
  Retrieval log for Wave 1 IBM hardware jobs.

### Hardware results and reconstructed kernels

- `hardware_results/zz4_H0_raw_results.json`  
  Raw SamplerV2 count results for regime `H0`.

- `hardware_results/zz4_H1_raw_results.json`  
  Raw SamplerV2 count results for regime `H1`.

- `hardware_results/zz4_H2_raw_results.json`  
  Raw SamplerV2 count results for regime `H2`.

- `metadata/zz4_wave1_kernel_manifest.json`  
  Hardware-kernel manifest confirming `24 x 24` matrices, no missing entries, measured-diagonal policy, and diagnostic PSD metadata.

- `hardware_kernels/zz4_H0_kernel.npy`  
  Wave 1 hardware-derived ZZ4 kernel for regime `H0` / manuscript configuration `M0`.

- `hardware_kernels/zz4_H1_kernel.npy`  
  Wave 1 hardware-derived ZZ4 kernel for regime `H1` / manuscript configuration `M1`.

- `hardware_kernels/zz4_H2_kernel.npy`  
  Wave 1 hardware-derived ZZ4 kernel for regime `H2` / manuscript configuration `M2`.

- `hardware_kernels/zz4_H0_kernel.csv`  
  CSV representation of the `H0` / `M0` hardware-derived kernel.

- `hardware_kernels/zz4_H1_kernel.csv`  
  CSV representation of the `H1` / `M1` hardware-derived kernel.

- `hardware_kernels/zz4_H2_kernel.csv`  
  CSV representation of the `H2` / `M2` hardware-derived kernel.

- `hardware_kernels/zz4_wave1_kernel_entries_long.csv`  
  Long-form Wave 1 kernel-entry table for count-level inspection.

### Hardware analysis

- `hardware_analysis/zz4_wave1_distortion_summary.json`  
  Summary of Wave 1 statevector-to-hardware kernel distortion metrics, reporting all required regimes and no failure reasons.

- `hardware_analysis/zz4_wave1_distortion_metrics.csv`  
  Tabular Wave 1 geometry and distortion metrics.

- `hardware_analysis/zz4_wave1_distortion_summary.md`  
  Human-readable Wave 1 distortion summary.

- `hardware_analysis/zz4_wave1_distortion_uncertainty.csv`  
  Leave-one-window-out jackknife, paired contrast, diagonal-robustness, and directed-vs-unique off-diagonal equivalence diagnostics for the Wave 1 geometry-distortion analysis.

- `hardware_analysis/zz4_wave1_distortion_uncertainty.json`  
  Machine-readable summary of the uncertainty/robustness analysis, including input paths, resampling unit, diagonal-sensitivity policy, and inferential limitation.

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

### Environment, verification, and metadata

- `environment/python_version.txt`
- `environment/pip_freeze.txt`
- `checksums/SHA256SUMS.txt`
- `MANIFEST.md`
- `CITATION.cff`
- `LICENSE`

## Reconstructing the Wave 1 hardware kernels

The curated package includes the raw hardware-result JSON files, the circuit-index ledger, the long-form kernel-entry table, the three reconstructed kernel matrices, and the kernel manifest required to audit the Wave 1 kernel reconstruction without re-submitting IBM Quantum jobs. The source-layout reconstruction script `scripts/08_build_hardware_kernels.py` is included for traceability; use the persisted reconstructed kernels in this curated package unless the path configuration is explicitly adapted to the local repository layout.

## Reproducing the Wave 1 distortion analysis

The curated package is intended to reproduce the reported statevector-to-hardware kernel distortion analysis without re-submitting IBM Quantum jobs.

From the repository root:

```bash
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
```

This script reads:

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


For the Section 2.8 robustness and uncertainty diagnostics, run:

```bash
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
```

This script writes or updates:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
hardware_analysis/zz4_wave1_distortion_uncertainty.json
```

The uncertainty/robustness outputs provide the directed-versus-unique off-diagonal equivalence check, unit-diagonal sensitivity diagnostics, and leave-one-window-out jackknife contrasts. These are descriptive robustness checks on the frozen `N = 24` window scale, not formal significance tests.

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

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory. The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. The centered kernel-target alignment values in the distortion analysis are descriptive geometry diagnostics on the frozen subset and are not classifier-performance claims.

The leave-one-window-out jackknife contrasts are descriptive robustness checks on the frozen `N = 24` window scale; they are not formal significance tests.

## License

See `LICENSE`.
