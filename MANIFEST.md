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
- **2.12. Shot-noise reference-scale decomposition**

## Reproducibility status

This repository is an artifact-level reproducibility package for the frozen Wave 1 ZZ4 hardware analysis. It supports reproduction of the kernel reconstruction audit, geometry-distortion metrics, CKA/KTA diagnostics, jackknife and diagonal-robustness checks, and shot-noise reference-scale decomposition from the persisted frozen artifacts listed below.

It is not a full end-to-end raw-data-to-IBM-execution pipeline. The upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission workflow, and original numbered execution pipeline are retained only as provenance where present.

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

## Supported analysis scripts

- `scripts/08b_audit_kernel_reconstruction.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/09d_shot_noise_reference_scale_decomposition.py`

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
| Geometry/distortion metrics | Spearman, Pearson, MAE, RMSE, MedAE, MaxAE, off-diagonal variance, effective rank, CKA, centered KTA |
| Section 2.9 CKA point estimates | `M0/H0 = 0.9333906747`, `M1/H1 = 0.9373725928`, `M2/H2 = 0.9886681278` |
| Section 2.10 centered KTA point estimates | `SV = 0.1585110924`, `M0/H0 = 0.1833084594`, `M1/H1 = 0.1814633785`, `M2/H2 = 0.1710248441` |
| Section 2.11 CKA/KTA tension quantities | `CKA loss = 1 - CKA`; `Delta_KTA = KTA_hardware - KTA_statevector` |
| Section 2.12 conservative global shot reference | `sigma_shot = 1/sqrt(2*1024) = 0.0220970869121`; conservative upper reference, not an individual-entry sampling SE |
| Section 2.12 matrix-aware shot reference | `sqrt(mean_{Omega} p_ij(1-p_ij)/1024)` using reconstructed off-diagonal hardware probabilities |
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
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Tabular Wave 1 geometry and distortion metrics. Supplies RMSE for Section 2.12 and CKA/KTA/effective-rank diagnostics for Sections 2.8--2.11. |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | Summary of Wave 1 statevector-to-hardware kernel distortion metrics. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable Wave 1 distortion summary. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` | Robustness diagnostics, including diagonal-sensitivity and leave-one-window-out jackknife summaries. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.json` | Machine-readable uncertainty/robustness summary. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv` | Section 2.12 tabular shot-noise reference-scale decomposition, including global and matrix-aware scales, residuals, and shot-share values. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json` | Machine-readable Section 2.12 decomposition with formulas, input paths, output paths, and diagnostic caveat. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md` | Human-readable Section 2.12 decomposition summary. |

### Section 2.8 primary distortion metrics

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Effective rank | Centered KTA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741297 | 0.827253 | 0.049036 | 0.087770 | 0.026154 | 0.568666 | 0.933391 | 21.184209 | 0.183308 |
| `M1` | `H1` | 0.774951 | 0.842774 | 0.047290 | 0.086428 | 0.026143 | 0.563897 | 0.937373 | 21.217026 | 0.181463 |
| `M2` | `H2` | 0.943744 | 0.986203 | 0.025726 | 0.042727 | 0.016161 | 0.263978 | 0.988668 | 19.788170 | 0.171025 |

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

The matrix-aware scale is computed from reconstructed hardware all-zero probabilities on the off-diagonal domain. The decomposition is diagnostic, not a full physical noise-model decomposition.
The global scale is a conservative upper reference that exceeds the maximum per-entry binomial standard error by `sqrt(2)`, not the sampling standard error of an individual kernel entry.

## Supported and archival scripts

| Path | Purpose |
| --- | --- |
| `scripts/08b_audit_kernel_reconstruction.py` | Independent reconstruction audit; verifies coordinate/pair-identifier consistency between retrieved PUBs and the circuit-index ledger. |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Direct reproduction script for distortion metrics. |
| `scripts/09c_wave1_distortion_uncertainty.py` | Computes robustness diagnostics, including diagonal sensitivity and leave-one-window-out jackknife rows. |
| `scripts/09d_shot_noise_reference_scale_decomposition.py` | Computes Section 2.12 global and matrix-aware shot-noise reference-scale decomposition. |
| `scripts/common.py` | Legacy shared utility module retained for archival/source-context provenance; the supported direct reproduction scripts `08b`, `09b`, `09c`, and `09d` are self-contained and do not require the legacy path/runtime configuration files. |
| `scripts/archive_original_execution_pipeline/` | Archived original execution pipeline retained for provenance only; not part of the supported flat-package reproduction path. |
| `archive_legacy_preprocessing/` | Archived legacy preprocessing code retained for source-context provenance only. |

The `offdiag_spearman_pvalue` and `offdiag_pearson_pvalue` columns in `hardware_analysis/zz4_wave1_distortion_metrics.csv` are retained for schema compatibility and intentionally left blank/NaN in the supported minimal workflow. They are not used for any manuscript claim because kernel entries are dependent observations.

## Environment and verification artifacts

| Path | Purpose |
| --- | --- |
| `environment/python_version.txt` | Python version recorded at package creation time. |
| `environment/pip_freeze.txt` | Package-freeze record documenting the Python environment. |
| `requirements.txt` | Minimal dependency declaration for the supported artifact-level reproduction scripts. |
| `checksums/SHA256SUMS.txt` | SHA-256 checksum manifest for verifying the reproduction package state. |

## Repository metadata

| Path | Purpose |
| --- | --- |
| `README.md` | Main reproduction-package description, updated to include Section 2.12 and the shot-noise reference-scale decomposition diagnostics. |
| `MANIFEST.md` | This artifact manifest, updated to include Section 2.12 and the shot-noise reference-scale decomposition diagnostics. |
| `CITATION.cff` | Citation metadata for the reproduction package. |
| `LICENSE` | License file. No update is required for the addition of Section 2.12 documentation. |
| `.gitignore` | Local and sensitive-file exclusion rules. |

## Decision-record artifacts

| Path | Purpose |
| --- | --- |
| `decision_records/zz4_wave1_decision_record.json` | Final Wave 1 decision record with `decision = STOP_AFTER_WAVE1_REPORT_RESULTS`; records frozen `N = 24`, blocked subset change, blocked threshold relaxation, and no Wave 2 without a new decision record. |

## Numerical Reproduction Verification

Run the supported direct workflow from the repository root:

```bash
python scripts/08b_audit_kernel_reconstruction.py --project-root .
python scripts/09b_analyze_wave1_distortion_direct.py --project-root .
python scripts/09c_wave1_distortion_uncertainty.py --project-root .
python scripts/09d_shot_noise_reference_scale_decomposition.py --project-root . --check
```

The expected result is successful execution and preservation of the reported scientific values within numerical tolerance. SHA-256 hashes verify the static curated package state, not byte-for-byte identity of regenerated timestamped/numerical outputs.

## Integrity Verification

Before regenerating outputs, verify the curated package state with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

This checksum manifest verifies the static curated repository state. It is not a byte-for-byte reproduction oracle for regenerated analysis outputs. Several supported scripts write `created_utc` timestamps and floating-point eigensolver diagnostics that may differ at roundoff scale across machines.

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, environment secrets, `.DS_Store`, local-only transfer scripts, and the checksum file itself.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory. The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope.

CKA, centered KTA, leave-one-window-out jackknife contrasts, and shot-noise reference-scale decomposition are descriptive diagnostics. Section 2.12 is not a physical noise-model decomposition and does not assign a mechanistic hardware-noise channel.
