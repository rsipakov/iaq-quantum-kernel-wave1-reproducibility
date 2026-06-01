# Manifest

This manifest lists the curated, non-sensitive artifacts included in the IAQ Quantum Kernel Wave 1 reproducibility package. It is cumulative through manuscript **Materials and methods** sections 2.1--2.13 and **Results** sections 3.1--3.6.

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
- **3.5. Dimensionless finite-shot scale separation of the off-diagonal RMSE**
- **3.6. Optional projection: 4096-shot rerun**

## Reproducibility status

This repository is an artifact-level reproducibility package for the frozen Wave 1 ZZ4 hardware analysis. It supports reproduction of the kernel reconstruction audit, geometry-distortion metrics, CKA/KTA diagnostics, jackknife and diagonal-robustness checks, shot-noise reference-scale decomposition, statevector label-permutation reference, Section 2.13 statistical-analysis policy, Section 3.1 hardware-execution summary, Section 3.2 main distortion metrics, Section 3.3 statistical support and label-alignment diagnostics, Section 3.4 KTA/CKA-tension synthesis, Section 3.5 dimensionless shot-noise scale-separation diagnostics, and Section 3.6 optional 4096-shot finite-shot projection.

It is not a full end-to-end raw-data-to-IBM-execution pipeline. The upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission workflow, and original numbered execution pipeline are retained only as provenance where present. Section 3.6 is not a hardware rerun; it is a deterministic finite-shot reference projection.

The manuscript files `NewSection_3.1.md`, `NewSection_3.2.md`, `NewSection_3.3.md`, `NewSection_3.4.md`, `NewSection_3.4_Revised*.md`, `NewSection_3.4_*Instructions.md`, `NewSection_3.5.md`, `NewSection_3.5_*.md`, `NewSection_3.6.md`, and `NewSection_3.6_*.md` are not artifacts to copy into this repository. They are manuscript draft files supplied outside the reproducibility package.

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
- `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv`
- `config/wave1_scope.json`
- `metadata/zz4_wave1_runtime_options.json`
- `metadata/zz_only_step8_execution_manifest.json`
- `job_metadata/zz4_wave1_job_manifest.json`

## Supported analysis scripts

- `scripts/08b_audit_kernel_reconstruction.py`
- `scripts/09b_analyze_wave1_distortion_direct.py`
- `scripts/09c_wave1_distortion_uncertainty.py`
- `scripts/09d_shot_noise_reference_scale_decomposition.py`
- `scripts/09e_label_permutation_reference.py`
- `scripts/09j_optional_4096_shot_projection.py`

## Results-section support scripts

These shell scripts verify Results-section support state. They do not submit IBM Quantum jobs and do not alter the frozen scientific scope.

- `scripts/verify_privacy_cleanup.sh`
- `scripts/verify_section3_1_support_files.sh`
- `scripts/verify_section3_2_support_files.sh`
- `scripts/verify_section3_3_support_files.sh`
- `scripts/verify_section3_4_support_files.sh`
- `scripts/verify_section3_5_support_files.sh`
- `scripts/verify_section3_6_support_files.sh`

Local update helper scripts supplied for the Section 3.6 update:

- `scripts/copy_section3_6_support_files.sh`
- `scripts/publish_section3_6_updates.sh`
- `scripts/run_section3_6_copy_verify_publish.sh`

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
- `hardware_analysis/zz4_wave1_4096_shot_projection.csv`
- `hardware_analysis/zz4_wave1_4096_shot_projection.json`
- `hardware_analysis/zz4_wave1_4096_shot_projection.md`

## Static Section 2.13 / Section 3.3 / Section 3.4 support artifact

- `hardware_analysis/qiskit_kta_cka_permutation_tests.csv`

This file is copied from the source artifact `step6_v6_consolidation/outputs/tables/qiskit_kta_cka_permutation_tests.csv` when available. It is a static label-permutation reference table for statevector kernels. Sections 2.13, 3.3, and 3.4 use only the ZZ4 statevector rows; the table also contains RMA6 rows retained for source-level traceability.

The historical table is a static source-derived reference: it is not produced by any script in this package and no permutation seed is preserved. The regenerable in-package reference is `hardware_analysis/zz4_wave1_label_permutation_reference.csv`, produced by `scripts/09e_label_permutation_reference.py` with a fixed reference seed and multi-seed sensitivity. Its persisted CSV/JSON outputs are byte-stable; local write-time provenance is emitted only to the ignored sidecar `hardware_analysis/zz4_wave1_label_permutation_reference_provenance.json`. Its `--check` mode validates the static copy without rewriting the persisted CSV/JSON artifacts.

## Section 3.6 projection artifact

- `hardware_analysis/zz4_wave1_4096_shot_projection.csv`
- `hardware_analysis/zz4_wave1_4096_shot_projection.json`
- `hardware_analysis/zz4_wave1_4096_shot_projection.md`

These files are generated by `scripts/09j_optional_4096_shot_projection.py`. The projection rescales only finite-shot reference terms from the executed 1024-shot Wave 1 analysis to the originally planned 4096-shot budget. It keeps the realized off-diagonal RMSE fixed, does not alter hardware kernels, does not simulate a hardware rerun, and does not project CKA, centered KTA, classifier performance, or quantum advantage.

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
| Section 3.6 projected shots | 4096 per circuit, reference-scale projection only |
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
| Section 3.5 global scale ratios | `RMSE/sigma_ref_global`: `H0=3.9720`, `H1=3.9113`, `H2=1.9336` |
| Section 3.5 matrix-aware scale ratios | `RMSE/sigma_shot_matrix`: `H0=10.6188`, `H1=10.4846`, `H2=5.0101` |
| Section 3.5 quadrature residual fractions (global reference) | `H0=93.66%`, `H1=93.46%`, `H2=73.25%` |
| Section 3.5 quadrature residual fractions (matrix-aware reference) | `H0=99.11%`, `H1=99.09%`, `H2=96.02%` |
| Section 3.6 projected global shot reference | `sigma_ref_global(4096)=1/sqrt(8192)=0.0110485434560` |
| Section 3.6 projected global shot shares | `H0=1.58%`, `H1=1.63%`, `H2=6.69%` |
| Section 3.6 projected matrix-aware shot scales | `H0=0.0041328`, `H1=0.0041216`, `H2=0.0042641` |
| Section 3.6 projected matrix-aware shot shares | `H0=0.22%`, `H1=0.23%`, `H2=1.00%` |
| Section 3.6 projected matrix-aware residual fractions | `H0=99.78%`, `H1=99.77%`, `H2=99.00%` |
| Section 3.6 projected matrix-aware RMSE ratios | `H0=21.24`, `H1=20.97`, `H2=10.02` |
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
| `config/wave1_scope.json` | Wave 1 scope configuration consumed by circuit-build and kernel-reconstruction workflows; records planned 4096 shots per circuit. |
| `metadata/zz4_wave1_feature_map_spec.json` | Manuscript-support feature-map specification for ZZ4. |

## Execution configuration label policy

| Manuscript label | Artifact label | Configuration | Runtime distinction |
| --- | ---: | --- | --- |
| `M0` | `H0` | Sampler baseline | Dynamical decoupling off; gate twirling off; measurement twirling off. |
| `M1` | `H1` | Sampler + dynamical decoupling | Dynamical decoupling on with `XX`, `alap`, middle slack; twirling off. |
| `M2` | `H2` | Sampler + gate/Pauli twirling | Gate twirling on; measurement twirling off; `active-accum`; dynamical decoupling off. |

The manuscript labels are aliases only. Persisted files remain keyed by `H0`, `H1`, and `H2`.

## Runtime, submission, and retrieval artifacts

| Path | Purpose |
| --- | --- |
| `metadata/zz4_wave1_runtime_options.json` | Records per-regime SamplerV2 runtime options and planned `default_shots = 4096` before budget-safe override. |
| `metadata/zz4_wave1_runtime_options_sha256.txt` | SHA-256 lock for runtime-option records. |
| `metadata/zz_only_step9_live_backend_metadata.json` | Live backend metadata snapshot for `ibm_fez`. |
| `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json` | Compile confirmation for `ibm_fez`. |
| `hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv` | Tabular compile confirmation. |
| `job_metadata/zz4_wave1_job_manifest.json` | Budget-safe combined manifest recording `shots_submitted_per_circuit = [1024]`, 900 submitted circuits, and one job row for each regime. |
| `job_metadata/zz4_wave1_job_manifest.csv` | Tabular combined job manifest. |
| `job_metadata/zz4_wave1_job_manifest_H0_1024.json` | Per-regime H0 job manifest. |
| `job_metadata/zz4_wave1_job_manifest_H1_1024.json` | Per-regime H1 job manifest. |
| `job_metadata/zz4_wave1_job_manifest_H2_1024.json` | Per-regime H2 job manifest. |
| `job_metadata/zz4_wave1_retrieval_manifest.json` | Retrieval manifest recording `DONE` status and 300 retrieved PUB results per regime. |
| `hardware_results/zz4_H0_raw_results.json` | Raw H0 hardware result payload. |
| `hardware_results/zz4_H1_raw_results.json` | Raw H1 hardware result payload. |
| `hardware_results/zz4_H2_raw_results.json` | Raw H2 hardware result payload, including realized twirling metadata. |
| `logs/zz4_wave1_submission_log_budget_safe_combined.md` | Submission provenance log for the budget-safe combined run. |
| `logs/zz4_wave1_retrieval_log.md` | Retrieval provenance log. |

## Kernel reconstruction artifacts

| Path | Purpose |
| --- | --- |
| `scripts/08b_audit_kernel_reconstruction.py` | Audits reconstruction row order, coordinates, pair identifiers, finite entries, and diagonal policy. |
| `metadata/zz4_wave1_kernel_manifest.json` | Manifest for reconstructed kernels, diagonal policy, symmetrization policy, and PSD diagnostics. |
| `metadata/zz4_wave1_kernel_reconstruction_audit.json` | JSON reconstruction audit. |
| `hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv` | CSV reconstruction audit. |
| `hardware_kernels/zz4_wave1_kernel_entries_long.csv` | Long-form bridge from raw counts to kernel entries: one row per retrieved circuit--regime configuration. |
| `hardware_kernels/zz4_H0_kernel.csv` | Reconstructed H0 kernel matrix. |
| `hardware_kernels/zz4_H1_kernel.csv` | Reconstructed H1 kernel matrix. |
| `hardware_kernels/zz4_H2_kernel.csv` | Reconstructed H2 kernel matrix. |
| `hardware_kernels/zz4_H0_kernel.npy` | Reconstructed H0 kernel matrix, NumPy format. |
| `hardware_kernels/zz4_H1_kernel.npy` | Reconstructed H1 kernel matrix, NumPy format. |
| `hardware_kernels/zz4_H2_kernel.npy` | Reconstructed H2 kernel matrix, NumPy format. |

## Distortion and uncertainty analysis artifacts

| Path | Purpose |
| --- | --- |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Computes the direct statevector-to-hardware distortion metrics. |
| `scripts/09c_wave1_distortion_uncertainty.py` | Computes diagonal-robustness checks, leave-one-window-out jackknife standard errors, and paired descriptive contrasts. |
| `hardware_analysis/zz4_wave1_distortion_metrics.csv` | Primary point-estimate distortion metrics. |
| `hardware_analysis/zz4_wave1_distortion_summary.json` | JSON distortion summary. |
| `hardware_analysis/zz4_wave1_distortion_summary.md` | Human-readable distortion summary. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.csv` | Jackknife, paired contrast, diagonal-sensitivity, and directed-versus-unique checks. |
| `hardware_analysis/zz4_wave1_distortion_uncertainty.json` | JSON companion for uncertainty diagnostics. |

## Shot-noise reference-scale artifacts

| Path | Purpose |
| --- | --- |
| `scripts/09d_shot_noise_reference_scale_decomposition.py` | Computes and checks the 1024-shot finite-shot reference-scale decomposition. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv` | Primary 1024-shot decomposition used in Sections 3.4 and 3.5. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.json` | JSON companion for the decomposition. |
| `hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.md` | Human-readable decomposition summary. |
| `scripts/verify_section3_5_support_files.sh` | Verifies Section 3.5 dimensionless scale-separation values and decomposition invariants. |

## Optional 4096-shot projection artifacts

| Path | Purpose |
| --- | --- |
| `scripts/09j_optional_4096_shot_projection.py` | Rescales the finite-shot reference terms from 1024 to 4096 shots under a fixed-RMSE projection policy. |
| `hardware_analysis/zz4_wave1_4096_shot_projection.csv` | Primary Section 3.6 projection table. |
| `hardware_analysis/zz4_wave1_4096_shot_projection.json` | JSON projection artifact with formulas, input list, and caveat. |
| `hardware_analysis/zz4_wave1_4096_shot_projection.md` | Human-readable projection summary. |
| `scripts/verify_section3_6_support_files.sh` | Verifies Section 3.6 support files, projection values, planned/executed shot-count distinction, and claim-boundary caveats. |
| `scripts/copy_section3_6_support_files.sh` | Local helper to copy or skip existing dependencies, install Section 3.6 files, and generate projection outputs. |
| `scripts/publish_section3_6_updates.sh` | Local helper to verify, update checksums, and print or run git publication commands. |
| `scripts/run_section3_6_copy_verify_publish.sh` | Local wrapper that runs copy, verify, and publish helpers. |

## Label-permutation artifacts

| Path | Purpose |
| --- | --- |
| `scripts/09e_label_permutation_reference.py` | Regenerates and checks the fixed-seed statevector label-permutation reference. |
| `hardware_analysis/zz4_wave1_label_permutation_reference.csv` | Regenerable in-package statevector label-permutation reference. |
| `hardware_analysis/zz4_wave1_label_permutation_reference.json` | JSON companion, including multi-seed sensitivity summary. |
| `hardware_analysis/qiskit_kta_cka_permutation_tests.csv` | Static source-derived statevector permutation table retained for provenance. |

## Verification commands

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
```

## Copy/update command sequence for Section 3.6

The local source repository is expected at:

```bash
SOURCE="/Users/rostyslavsipakov/Documents/GitHub/QuantumKernel/duplicate-sensor-monitoring/notebooks"
```

The dedicated reproducibility repository is expected at:

```bash
REPRO="/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility"
```

Run from the unpacked Section 3.6 update bundle:

```bash
bash scripts/run_section3_6_copy_verify_publish.sh "$SOURCE" "$REPRO" "$(pwd)"
```

The copy helper skips existing dependency artifacts in the reproducibility repository and copies them from `SOURCE` only if missing. It installs the new Section 3.6 projection script and documentation, generates `hardware_analysis/zz4_wave1_4096_shot_projection.{csv,json,md}`, and runs the Section 3.6 verifier.

## Checksums

The checksum file is:

```text
checksums/SHA256SUMS.txt
```

Regenerate from the repository root after intentional updates:

```bash
mkdir -p checksums
find . -type f \
  -not -path './.git/*' \
  -not -path './checksums/SHA256SUMS.txt' \
  -print | LC_ALL=C sort | xargs shasum -a 256 > checksums/SHA256SUMS.txt
```

On Linux, `sha256sum` may be used instead of `shasum -a 256`.

## Claim boundary

The package supports kernel-geometry survival and hardware-distortion analysis only. It does not support claims of quantum advantage, hardware classifier superiority, IAQ forecasting performance, post hoc subset optimization, post hoc threshold relaxation, or uncontrolled Wave 2 expansion.

Section 3.6 is a finite-shot reference-scale projection under a fixed-RMSE assumption. It is not a realized 4096-shot IBM Quantum rerun, not a physical hardware-noise model, not a classifier result, and not evidence that a future 4096-shot execution would preserve the same kernels or the same RMSE values.
