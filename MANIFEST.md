# Manifest

## Dataset and prediction context source files

| Path | Purpose |
|---|---|
| `config/config.py` | Defines allowed targets and compact feature sets, including `F_quantum_4`. |
| `preprocessing/data.py` | Implements train-only preprocessing, scaling to `[0, pi]`, valid-label filtering, and clipping. |
| `preprocessing/feature_maps.py` | Implements the ZZ feature-map builder used for `ZZ4`. |
| `metadata/qiskit_stage_v5_scaling_report.csv` | Reports split counts and scaling diagnostics for `event_onset_next_1h`. |
| `frozen_subset/hardware_subset_event_onset_next_1h.csv` | Frozen `N=24` subset used for hardware-kernel evaluation. |
| `metadata/zz_only_pilot_operational_plan.json` | Defines ZZ-only hardware-pilot scope and allowed claims. |
| `metadata/statevector_reference_metadata.json` | Defines statevector kernel and ZZ4 feature order. |
| `metadata/zz_only_step8_execution_manifest.json` | Records authorized hardware execution scope. |
| `metadata/v9_audit_freeze_manifest.json` | Records audit/freeze state and immutable scope constraints. |
| `metadata/zz4_subset_seed_stability_summary.json` | Records subset-stability caveat and frozen-subset status. |
| `statevector_reference/zz4_K_all_all.npy` | Full `24 x 24` ZZ4 statevector reference kernel. |
