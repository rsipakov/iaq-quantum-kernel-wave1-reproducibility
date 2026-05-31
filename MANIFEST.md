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
- **3.3. Statistical confidence and label-alignment diagnostics**

## Reproducibility status

This repository is an artifact-level reproducibility package for the frozen Wave 1 ZZ4 hardware analysis. It supports reproduction of the kernel reconstruction audit, geometry-distortion metrics, CKA/KTA diagnostics, jackknife and diagonal-robustness checks, shot-noise reference-scale decomposition, statevector label-permutation reference, Section 2.13 statistical-analysis policy, Section 3.1 hardware-execution summary, Section 3.2 main distortion metrics, and Section 3.3 statistical-confidence and label-alignment diagnostics from the persisted frozen artifacts listed below.

It is not a full end-to-end raw-data-to-IBM-execution pipeline. The upstream IAQ dataset construction, full preprocessing/feature-engineering workflow, IBM Quantum job submission workflow, and original numbered execution pipeline are retained only as provenance where present.

The manuscript files `NewSection_3.1.md`, `NewSection_3.2.md`, and `NewSection_3.3.md` are not artifacts to copy into this repository. They are manuscript draft files supplied outside the reproducibility package.

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

## Static Section 2.13 / Section 3.3 support artifact

- `hardware_analysis/qiskit_kta_cka_permutation_tests.csv`

This file is copied from the source artifact `step6_v6_consolidation/outputs/tables/qiskit_kta_cka_permutation_tests.csv` when available. It is a static label-permutation reference table for statevector kernels. Section 2.13 and Section 3.3 use only the ZZ4 statevector rows; the table also contains RMA6 rows retained for source-level traceability.

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

| Manuscript label | Artifact regime | Spearman | Pearson | MAE | RMSE | MedAE | MaxAE | CKA | Centered KTA hw | Eff. rank hw | min eig | PSD rel. Fro. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.741 | 0.827 | 0.0490 | 0.0878 | 0.0262 | 0.569 | 0.933 | 0.183 | 21.18 | 0.429 | `<2e-15` |
| `M1` | `H1` | 0.775 | 0.843 | 0.0473 | 0.0864 | 0.0261 | 0.564 | 0.937 | 0.181 | 21.22 | 0.462 | `<2e-15` |
| `M2` | `H2` | 0.944 | 0.986 | 0.0257 | 0.0427 | 0.0162 | 0.264 | 0.989 | 0.171 | 19.79 | 0.232 | `<2e-15` |

The verification script `scripts/verify_section3_2_support_files.sh` enforces the following Section 3.2 invariants:

- exactly three metric rows are present, one each for `H0`, `H1`, and `H2`;
- `n = 24` and `shots_submitted_per_circuit = 1024` for every row;
- correlation-test p-value columns remain blank/NaN in the supported minimal workflow;
- `H2` has the highest Spearman, Pearson, and CKA point estimates;
- `H2` has the lowest MAE, RMSE, MedAE, and MaxAE point estimates;
- among the three regimes, `H2` is closest to the statevector effective rank;
- all uncorrected hardware matrices have strictly positive minimum eigenvalues;
- PSD grounding is based on `min_eigenvalue_before_psd`, not on `psd_correction_frobenius_relative`;
- PSD relative Frobenius corrections remain below `5e-15`;
- the paired leave-one-window-out jackknife resolves `H2` from `H0` and `H1` for Spearman, MAE, and CKA, while the `H1-H0` contrast is unresolved;
- all hardware centered-KTA values exceed the statevector KTA, and `H2` has the smallest uplift;
- `H0` and `H1` retain less than 30% of the statevector off-diagonal variance, while `H2` retains approximately 52%.

The historical source metric table in `rsipakov/QuantumKernel` contains conventional Spearman/Pearson p-value columns and slightly different roundoff-scale PSD Frobenius diagnostics. The public reproducibility package uses the direct workflow instead: p-values are blank/NaN because kernel entries are dependent, and PSD correction values are interpreted only at order-of-magnitude precision.

## Section 3.3 statistical-confidence and label-alignment grounding

Section 3.3 uses the supported uncertainty table:

```text
hardware_analysis/zz4_wave1_distortion_uncertainty.csv
```

The point estimates and leave-one-window-out jackknife standard errors used in the pre-submission statistical table are:

| Metric | Domain | `M0/H0` | `M1/H1` | `M2/H2` |
| --- | --- | ---: | ---: | ---: |
| Spearman | off-diagonal | 0.741297 ± 0.051669 | 0.774951 ± 0.045891 | 0.943744 ± 0.012376 |
| Pearson | off-diagonal | 0.827253 ± 0.085944 | 0.842774 ± 0.062777 | 0.986203 ± 0.004460 |
| MAE | off-diagonal | 0.049036 ± 0.007897 | 0.047290 ± 0.008294 | 0.025726 ± 0.003549 |
| RMSE | off-diagonal | 0.087770 | 0.086428 | 0.042727 |
| CKA | full matrix | 0.933391 ± 0.021873 | 0.937373 ± 0.019001 | 0.988668 ± 0.002567 |
| Centered KTA | full matrix | 0.183308 ± 0.036223 | 0.181463 ± 0.035045 | 0.171025 ± 0.035962 |

RMSE is point-estimate only; no leave-one-window jackknife row or paired contrast is persisted for RMSE.

The paired jackknife contrasts used in Section 3.3 are:

| Metric | Contrast | Delta | SE_delta | z_desc |
| --- | --- | ---: | ---: | ---: |
| Spearman | `M2-M0` | +0.202447 | 0.049890 | +4.057866 |
| Spearman | `M2-M1` | +0.168793 | 0.042800 | +3.943710 |
| Pearson | `M2-M0` | +0.158950 | 0.082937 | +1.916517 |
| Pearson | `M2-M1` | +0.143429 | 0.059757 | +2.400205 |
| MAE | `M2-M0` | -0.023310 | 0.004720 | -4.938800 |
| MAE | `M2-M1` | -0.021564 | 0.005012 | -4.302463 |
| CKA | `M2-M0` | +0.055277 | 0.019543 | +2.828536 |
| CKA | `M2-M1` | +0.051296 | 0.016621 | +3.086171 |
| Centered KTA | `M2-M0` | -0.012284 | 0.014088 | -0.871930 |
| Centered KTA | `M2-M1` | -0.010439 | 0.013436 | -0.776936 |

These contrasts are descriptive robustness diagnostics, not formal tests. No adjusted hardware-contrast p-values are generated or reported.

### Section 3.3 statevector permutation reference

The fixed-seed in-package reference is:

```text
hardware_analysis/zz4_wave1_label_permutation_reference.csv
hardware_analysis/zz4_wave1_label_permutation_reference.json
```

The reference uses `n_perm = 5000`, `seed = 0`, and the frozen balanced label vector (`positive = 12`, `negative = 12`). It records:

| Kernel | Source metric label | Alignment convention | Observed | Null mean | Null SD | Null q95 | Null q99 | p_upper_tail | p_two_sided_centered | p_two_sided_2min | n_perm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | centered label alignment | 0.1585110924 | 0.1709786387 | 0.0355291291 | 0.2353874561 | 0.2681052758 | 0.5988 | 0.7294 | 0.8024 | 5000 |
| `zz4` | `KTA` | uncentered label alignment | 0.1329093895 | 0.1433632571 | 0.0297906903 | 0.1973691723 | 0.2248026179 | 0.5988 | 0.7294 | 0.8024 | 5000 |

In manuscript notation, the source metric label `CKA` denotes the centered label-alignment row, equivalent to `KTA_c(K_SV, y) = CKA(K_SV, yy^T)`. The source metric label `KTA` denotes the companion uncentered alignment row and is retained for provenance only. It is a statevector random-label reference, not a hardware-regime permutation test.

The static source-derived ZZ4 rows retained for provenance are:

| Kernel | Metric row | Observed | Null mean | Null SD | Null q95 | Null q99 | p_perm upper-tail (source field: `p_perm_two_sided`) | n_perm |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `zz4` | `CKA` | 0.1585110924 | 0.1709625562 | 0.0352334692 | 0.2346692114 | 0.2688889140 | 0.5946810638 | 5000 |
| `zz4` | `KTA` | 0.1329093895 | 0.1433497722 | 0.0295427835 | 0.1967669338 | 0.2254596879 | 0.5946810638 | 5000 |

The persisted source field `p_perm_two_sided` records an upper-tail exceedance probability $P(T_{\text{null}} \ge T_{\text{obs}})$, retained under its original name for provenance. The observed alignment lies below the permutation-null mean, so the conclusion, no alignment beyond a random-label reference, holds under both one- and two-sided conventions.

### Section 3.3 CKA/KTA tension

The Section 3.3 CKA/KTA tension values are:

| Manuscript label | Artifact regime | CKA loss | Hardware KTA_c | Statevector KTA_c | Delta_KTA | Unit-diagonal KTA sensitivity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.0666093253 | 0.1833084594 | 0.1585110924 | +0.0247973670 | +0.0023423126 |
| `M1` | `H1` | 0.0626274072 | 0.1814633785 | 0.1585110924 | +0.0229522861 | +0.0025121116 |
| `M2` | `H2` | 0.0113318722 | 0.1710248441 | 0.1585110924 | +0.0125137518 | +0.0031201632 |

`M2/H2` has the smallest CKA loss and smallest KTA uplift. `M0/H0` has the largest absolute hardware centered KTA but the largest CKA loss. This pattern is interpreted as non-affine, label-correlated hardware distortion, not as classifier-performance improvement.

The verification script `scripts/verify_section3_3_support_files.sh` enforces the following Section 3.3 invariants:

- required support files and scripts are present;
- `NewSection_3.3.md` is not present in the repository root;
- metric rows are present for `H0`, `H1`, and `H2`, with `n = 24` and 1024 submitted shots;
- correlation-test p-value columns remain blank/NaN;
- hardware KTA uplift is positive for all regimes and smallest for `H2`;
- `H2` has the smallest CKA loss;
- `H0` has the largest absolute hardware centered KTA;
- jackknife SEs and paired contrasts match the persisted uncertainty table;
- RMSE has no persisted jackknife or paired contrast;
- unit-diagonal KTA sensitivity is small and does not change the ordering;
- the fixed-seed label-permutation reference matches the reported values;
- the static source-derived permutation table is retained as provenance and has non-significant ZZ4 flags.

## Shot-noise reference-scale summary

The shot-noise reference-scale decomposition uses:

```text
hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv
```

| Manuscript label | Artifact regime | RMSE | sigma_ref_global | residual_global | ShotShare_global | sigma_shot_matrix | residual_matrix | ShotShare_matrix |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% | 0.008266 | 0.087380 | 0.89% |
| `M1` | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% | 0.008243 | 0.086034 | 0.91% |
| `M2` | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% | 0.008528 | 0.041868 | 3.98% |

The matrix-aware scale is computed from reconstructed hardware all-zero probabilities on the off-diagonal domain. The decomposition is diagnostic, not a full physical noise-model decomposition. The global scale is a conservative upper reference that exceeds the maximum per-entry binomial standard error by `sqrt(2)`, not the sampling standard error of an individual kernel entry.

## Section 2.13 statistical analysis summary

| Item | Status |
| --- | --- |
| Statistical unit | Frozen observation window |
| Pair-entry bootstrap CI | Not reported; no 10,000-replicate hardware-bootstrap CI artifact is present, and kernel entries are dependent observations |
| Jackknife | Leave-one-window-out jackknife for Spearman, Pearson, MAE, CKA, and centered KTA |
| Paired contrasts | `M1-M0`, `M2-M1`, `M2-M0`; descriptive `z = delta / SE_delta`, not formal tests |
| Point-estimate-only metrics | RMSE, MedAE, MaxAE, off-diagonal variance, and effective rank are reported as point estimates; no window-level jackknife is persisted for any of them |
| Correlation p-values | Blank/NaN and not used |
| Hardware label permutation | Not persisted or claimed |
| Statevector label permutation | Static source-derived ZZ4 reference and fixed-seed in-package reference, each with `n_perm = 5000` |
| Multiple-comparison correction | Not applied because no formal hardware-contrast p-values are generated |

## Supported and archival scripts

| Path | Purpose |
| --- | --- |
| `scripts/08b_audit_kernel_reconstruction.py` | Audits coordinate and pair-identifier consistency between raw retrieved PUB metadata and the circuit-index ledger. |
| `scripts/09b_analyze_wave1_distortion_direct.py` | Regenerates the direct distortion metrics from persisted kernels and statevector reference. |
| `scripts/09c_wave1_distortion_uncertainty.py` | Regenerates leave-one-window-out jackknife, paired descriptive contrasts, diagonal-sensitivity checks, and directed-versus-unique equivalence checks. |
| `scripts/09d_shot_noise_reference_scale_decomposition.py` | Regenerates Section 2.12 finite-shot reference-scale decomposition; supports `--check`. |
| `scripts/09e_label_permutation_reference.py` | Regenerates and checks the Section 2.13 / Section 3.3 statevector label-permutation reference. |
| `scripts/common.py` | Legacy shared utility module retained for archival/source-context provenance; not required by the supported direct reproduction scripts. |
| `scripts/copy_section3_1_support_files.sh` | Idempotently copies the Section 3.1 support artifacts from the upstream source tree into the flat reproducibility layout if files are absent or changed. |
| `scripts/verify_section3_1_support_files.sh` | Verifies job manifests, retrieval manifest, raw-result counts, shot counts, `H2` randomization metadata, billed quantum seconds, and long-form kernel-entry counts needed by Section 3.1. |
| `scripts/publish_section3_1_updates.sh` | Runs Section 3.1 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_1_copy_verify_publish.sh` | Runs Section 3.1 copy, verify, and publish in sequence. |
| `scripts/copy_section3_2_support_files.sh` | Idempotently copies Section 3.2 support inputs from the upstream source tree if files are absent or changed; curated in-package analysis scripts are retained locally. |
| `scripts/verify_section3_2_support_files.sh` | Verifies the Section 3.2 metric table, point-estimate ordering, PSD roundoff-scale diagnostics, KTA-uplift interpretation boundary, and off-diagonal variance-retention pattern. |
| `scripts/publish_section3_2_updates.sh` | Runs Section 3.2 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_2_copy_verify_publish.sh` | Runs Section 3.2 copy, direct metric regeneration, verify, and publish in sequence. |
| `scripts/copy_section3_3_support_files.sh` | Idempotently copies Section 3.3 support inputs and the static permutation provenance table if files are absent or changed. |
| `scripts/verify_section3_3_support_files.sh` | Verifies Section 3.3 jackknife table values, paired descriptive contrasts, RMSE point-estimate-only status, KTA/CKA tension, diagonal sensitivity, and label-permutation reference. |
| `scripts/publish_section3_3_updates.sh` | Runs Section 3.3 verification, regenerates `checksums/SHA256SUMS.txt`, and stages/commits/pushes repository updates. |
| `scripts/run_section3_3_copy_verify_publish.sh` | Runs Section 3.3 copy, direct metric regeneration, label-permutation regeneration/check, verify, and publish in sequence. |
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

The manuscript execution-configuration labels `M0`, `M1`, and `M2` are aliases for the persisted artifact labels `H0`, `H1`, and `H2`; they do not expand the experimental scope. CKA, centered KTA, leave-one-window-out jackknife contrasts, statevector label-permutation diagnostics, shot-noise reference-scale decomposition, Section 3.1 hardware-execution accounting, Section 3.2 main distortion metrics, and Section 3.3 statistical-confidence diagnostics are descriptive diagnostics, not classifier-performance metrics.

For Section 3.1, the billed quantum seconds are repository-grounded: the values 80, 80, and 84 quantum seconds (total 244) are read from `job_metrics.usage.quantum_seconds` in the raw-result payloads, with the agreeing sub-fields `usage.seconds` and `bss.seconds`, and are verified by `scripts/verify_section3_1_support_files.sh`. They are reported as a resource-usage accounting only and carry no kernel-survival, classifier-performance, or quantum-advantage meaning.

For Section 3.2, `M2/H2` is reported only as the best observed point-estimate kernel-survival configuration among the three executed Wave 1 jobs. The package does not support wording that `M2/H2 significantly outperformed` the other configurations unless a separate inferential analysis is specified and reported.

For Section 3.3, the supported confidence table reports jackknife standard errors and descriptive paired contrast ratios only. It does not report 95% confidence intervals, adjusted hardware-contrast p-values, or hardware-regime permutation p-values. The statevector label-permutation reference does not support ZZ4 label alignment beyond random labels on the frozen subset, and hardware centered-KTA inflation is interpreted as distortion rather than supervised improvement.
