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
- Frozen hardware subset: `N=24`
- Kernel: `ZZ4`
- Purpose: statevector-to-hardware kernel-geometry survival/distortion analysis

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
  Frozen `N=24` subset used for the hardware pilot.

- `metadata/statevector_reference_metadata.json`  
  Statevector kernel definition and ZZ4 feature order.

- `statevector_reference/zz4_K_all_all.npy`  
  Full `24 x 24` ZZ4 statevector reference kernel.

## Claim limitation

This package supports kernel-geometry survival and distortion analysis only.
It does not support claims of quantum advantage, hardware classifier superiority,
or post hoc subset optimization.

## License

See `LICENSE`.
