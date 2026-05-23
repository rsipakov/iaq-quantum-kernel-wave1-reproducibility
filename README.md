# IAQ Quantum Kernel Wave 1 Reproducibility Package

This repository is a curated reproducibility package for the manuscript Materials and Methods section, including:

- **2.1. Dataset and prediction context**
- **2.2. Frozen subset**
- **2.3. ZZ4 quantum feature map**
- **2.4. Pair inventory**

The package preserves the non-sensitive artifacts required to support the frozen ZZ4 Wave 1 statevector-to-hardware kernel-survival and hardware-distortion analysis.

The package is derived from the private working repository:

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
- Unique off-diagonal pairs: 276
- Diagonal entries: 24
- Hardware regimes: `H0`, `H1`, `H2`
- Fidelity circuits: 900 total, i.e. 300 pairs × 3 regimes
- Submitted shots: 1024 per circuit for `H0`, `H1`, and `H2`
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis
- Claim scope: no quantum-advantage claim and no hardware classifier-superiority claim

The originally planned Wave 1 scope recorded 4096 shots per circuit, but the reported artifacts in this curated package correspond to the budget-safe execution using 1024 submitted shots per circuit. This affects sampling precision, not the definition of the ZZ4 feature map, the statevector reference kernel, or the 300-row pair inventory.

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

The current Wave 1 decision-record mechanism does not authorize subset modification. Any future subset modification would require a separate scope-unlock procedure outside the current Wave 1 reproduction scope.

Thresholds used for inclusion, exclusion, hardware feasibility, compile-gate acceptance, subset stability, or pass/fail interpretation are also frozen. Post-hoc threshold relaxation is not permitted.

Wave 2 execution is excluded from the current frozen-subset reproduction unless explicitly authorized by a new decision record. Full 300-pair Wave 2 execution is not authorized under the current scope. Any sentinel-only Wave 2 extension must preserve the frozen-subset policy and must not retroactively alter the Wave 1 subset, thresholds, or claims.

## Pair inventory policy

The Wave 1 pair inventory is a deterministic upper-triangular enumeration of the frozen `N = 24` subset. It contains all unordered off-diagonal pairs and all diagonal entries:

```text
276 off-diagonal pairs + 24 diagonal entries = 300 pair entries
```

The pair inventory is not a random sample, not a class-balanced sample, and not an adaptive subset selected after hardware execution. Each row carries a stable `pair_id`, an integer `pair_order` (`0`–`299`), the enumeration mode `pair_mode` (`upper_triangle_including_diagonal`), the kernel coordinates `kernel_i` and `kernel_j` (with `kernel_i <= kernel_j`), the frozen-subset sample identifiers `sample_i_id` and `sample_j_id`, a `pair_type` label (`diagonal` or `off_diagonal`), the reserved fields `sample_i_split`, `sample_j_split`, `sample_i_target`, `sample_j_target`, `split_pair`, and `target_pair`, an `expected_symmetry_mirror` flag, an `include_in_wave1_full_kernel` flag, a `sentinel_pair` flag, and a free-text `notes` field. The full column schema is documented in `MANIFEST.md`.

In the frozen Wave 1 inventory, `include_in_wave1_full_kernel` is `true` for all 300 rows, and `sentinel_pair` is `false` for all 300 rows: no sentinel pairs are designated in Wave 1, consistent with the Wave 2 / sentinel restrictions above. `expected_symmetry_mirror` is `true` for the 276 off-diagonal rows and `false` for the 24 diagonal rows. The reserved split- and target-label fields are present in the schema but left unpopulated; pair rows reference samples only by their opaque `sample_*_id` identifiers, so no split membership or class label is attached to any pair. Pair inclusion is therefore label-blind by construction.

The companion circuit inventory crosses the same 300 pair entries with the three pre-authorized Wave 1 regimes, producing 900 planned fidelity-circuit records. The reported budget-safe execution submitted 900 circuits at 1024 shots per circuit.

## Included materials

- `config/config.py`  
  Target and feature-set definitions, including `event_onset_next_1h` and `F_quantum_4`.

- `preprocessing/data.py`  
  Dataset loading, valid-label filtering, train-only imputation, train-only scaling to `[0, pi]`, and clipping.

- `preprocessing/feature_maps.py`  
  ZZ feature-map implementation for the `F_quantum_4 / ZZ4` kernel.

- `metadata/qiskit_stage_v5_scaling_report.csv`  
  Split counts and feature-scaling diagnostics for the full event-onset context.

- `frozen_subset/hardware_subset_event_onset_next_1h.csv`  
  Fixed `N = 24` subset of observation windows used for the Wave 1 ZZ4 hardware pilot.

- `metadata/zz_only_pilot_operational_plan.json`  
  Operational plan defining the ZZ-only hardware pilot scope, frozen-subset policy, allowed claims, pair counts, and Wave 2 restrictions.

- `metadata/zz_only_step8_execution_manifest.json`  
  Execution manifest recording the authorized Wave 1 scope, including the frozen `N = 24` subset, ZZ4 kernel configuration, pair-count metadata, and pair-inventory checksum.

- `metadata/zz_only_step8_pair_inventory.csv`  
  Deterministic 300-row upper-triangular inventory for the frozen `24 x 24` kernel, including all 276 off-diagonal pairs and all 24 diagonal entries. Full column schema documented in `MANIFEST.md`.

- `metadata/zz_only_step8_circuit_inventory.csv`  
  900-row circuit inventory obtained by crossing the 300 pair entries with regimes `H0`, `H1`, and `H2`.

- `metadata/zz4_wave1_circuit_build_manifest.json`  
  Circuit-build manifest confirming the expected 300 pairs and 900 Wave 1 fidelity circuits.

- `metadata/zz4_wave1_preflight_report.json`  
  Preflight report confirming expected and observed pair/circuit counts and recording the pair-inventory checksum.

- `metadata/zz4_wave1_kernel_manifest.json`  
  Kernel-build manifest confirming `24 x 24` hardware-kernel shapes, no missing entries, measured-diagonal policy, and diagnostic PSD policy.

- `metadata/v9_audit_freeze_manifest.json`  
  Audit/freeze manifest recording the allowed subset, allowed feature set, allowed kernel, threshold policy, and freeze state.

- `metadata/zz4_subset_seed_stability_summary.json`  
  Subset-stability summary confirming that the frozen subset was not changed after hardware results.

- `metadata/statevector_reference_metadata.json`  
  Statevector reference metadata for the ZZ4 feature order and the exact squared-fidelity kernel.

- `statevector_reference/zz4_K_all_all.npy`  
  Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset.

- `hardware_kernels/`  
  IBM hardware-derived ZZ4 kernels for Wave 1 regimes `H0`, `H1`, and `H2`, stored in both `.npy` and `.csv` form.

- `job_metadata/zz4_wave1_job_manifest.json`  
  Combined Wave 1 IBM job manifest recording regimes `H0`, `H1`, and `H2`, 1024 submitted shots per circuit, 300 covered pairs per regime, and 900 total submitted circuits.

- `job_metadata/`  
  IBM job manifests and retrieval records for the Wave 1 hardware execution.

- `hardware_analysis/`  
  Wave 1 distortion and kernel-comparison analysis outputs.

- `scripts/`  
  Scripts used to lock, validate, retrieve, build, and analyze the Wave 1 hardware kernel artifacts.

- `environment/`  
  Python version and package-freeze information used to document the reproduction environment.

- `decision_records/zz4_wave1_decision_record.json`  
  Final Wave 1 decision record documenting `STOP_AFTER_WAVE1_REPORT_RESULTS`, frozen `N = 24` subset scope, blocked subset change, blocked threshold relaxation, and no Wave 2 execution without a new decision record.

- `scripts/09b_analyze_wave1_distortion_direct.py`  
  Direct Wave 1 distortion-analysis script adapted for the curated reproduction layout. It reads labels from `frozen_subset/hardware_subset_event_onset_next_1h.csv`, loads the statevector reference from `statevector_reference/`, loads hardware kernels from `hardware_kernels/`, and writes outputs to `hardware_analysis/`.

- `checksums/SHA256SUMS.txt`  
  SHA-256 checksums for verifying the reproduction package state.

- `MANIFEST.md`  
  Human-readable artifact manifest for the curated reproduction package.

- `CITATION.cff`  
  Citation metadata for the reproduction package.

- `manuscript/section_2_4_pair_inventory.md`  
  Manuscript-ready text for Section 2.4, Pair inventory.

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

The script `scripts/06_submit_wave1_jobs.py` is included for traceability only. Reproduction of the reported results should not re-submit IBM Quantum hardware jobs unless explicitly authorized by a new decision record.

## Integrity verification

The package state can be verified with:

```bash
shasum -a 256 -c checksums/SHA256SUMS.txt
```

The checksum file should exclude `.git/`, IDE state such as `.idea/`, local virtual environments, environment secrets, `.DS_Store`, local-only transfer scripts, and the checksum file itself.

If repository files are intentionally updated, regenerate the checksum file from the repository root after all edits are complete.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N = 24` subset or the fixed 300-row pair inventory.

## License

See `LICENSE`.
