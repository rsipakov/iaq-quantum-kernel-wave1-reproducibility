# IAQ Quantum Kernel Wave 1 Reproducibility Package

This repository is a curated reproducibility package for the manuscript subsection
"Dataset and prediction context" and related Wave 1 quantum-kernel artifacts.

The package is derived from the private working repository:

`rsipakov/QuantumKernel`

Only non-sensitive files required to support the manuscript claims are included.

## Scope

- Domain: real indoor air-quality duplicate-sensor monitoring data
- Prediction target: `event_onset_next_1h` / `y_event_onset_next_1h`
- Feature set: `F_quantum_4`
- Frozen subset: `N=24` fixed observation windows
- Kernel: `ZZ4`
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis

## Frozen subset policy

This reproduction package uses a fixed `N=24` subset of observation windows from the duplicate-sensor indoor air-quality monitoring dataset.

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

## Included materials

- `config/config.py`  
  Target and feature-set definitions, including `F_quantum_4`.

- `preprocessing/data.py`  
  Dataset loading, valid-label filtering, train-only imputation, train-only scaling to `[0, pi]`, and clipping.

- `preprocessing/feature_maps.py`  
  ZZ feature-map implementation for the `F_quantum_4 / ZZ4` kernel.

- `metadata/qiskit_stage_v5_scaling_report.csv`  
  Split counts and scaling diagnostics.

- `frozen_subset/hardware_subset_event_onset_next_1h.csv`  
  Fixed `N=24` subset of observation windows used for the Wave 1 ZZ4 hardware pilot.

- `metadata/zz_only_pilot_operational_plan.json`  
  Operational plan defining the ZZ-only hardware pilot scope, frozen-subset policy, allowed claims, and Wave 2 restrictions.

- `metadata/zz_only_step8_execution_manifest.json`  
  Execution manifest recording the authorized Wave 1 scope, including the frozen `N=24` subset and ZZ4 kernel configuration.

- `metadata/v9_audit_freeze_manifest.json`  
  Audit/freeze manifest recording the allowed subset, allowed feature set, allowed kernel, threshold policy, and freeze state.

- `metadata/zz4_subset_seed_stability_summary.json`  
  Subset-stability summary confirming that the frozen subset was not changed after hardware results.

- `metadata/statevector_reference_metadata.json`  
  Statevector kernel definition and ZZ4 feature order.

- `statevector_reference/zz4_K_all_all.npy`  
  Full `24 x 24` ZZ4 statevector reference kernel for the frozen subset.

- `hardware_kernels/`  
  IBM hardware-derived ZZ4 kernels for the Wave 1 regimes.

- `job_metadata/`  
  IBM job manifests and retrieval records for the Wave 1 hardware execution.

- `hardware_analysis/`  
  Wave 1 distortion and kernel-comparison analysis outputs.

- `scripts/`  
  Scripts used to lock, validate, retrieve, build, and analyze the Wave 1 hardware kernel artifacts.

- `environment/`  
  Python version and package-freeze information used to document the reproduction environment.

- `decision_records/zz4_wave1_decision_record.json`  
  Final Wave 1 decision record documenting `STOP_AFTER_WAVE1_REPORT_RESULTS`, frozen `N=24` subset scope, blocked subset change, blocked threshold relaxation, and no Wave 2 execution without a new decision record.

- `checksums/`  
  SHA-256 checksums for verifying the reproduction package state.

- `MANIFEST.md`  
  Human-readable artifact manifest for the curated reproduction package.

- `CITATION.cff`  
  Citation metadata for the reproduction package.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.

It does not support claims of quantum advantage, hardware classifier superiority, post hoc subset optimization, post hoc threshold relaxation, uncontrolled Wave 2 expansion, or any conclusion that depends on replacing or modifying the frozen `N=24` subset.

## License

See `LICENSE`.