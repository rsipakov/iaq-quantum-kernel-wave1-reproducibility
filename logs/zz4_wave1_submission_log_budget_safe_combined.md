# ZZ4 Wave 1 budget-safe combined submission log

This derived human-readable log was reconstructed from `job_metadata/zz4_wave1_job_manifest_budget_safe_combined.json`.

The original submission script wrote the human-readable submission log to a single fixed path. Because Wave 1 was submitted in budget-safe partial runs, the final H2 partial submission overwrote the earlier H0/H1 human-readable submission log. The complete H0-H2 submission provenance is preserved in the combined machine-readable manifest.

- artifact_type: zz4_wave1_job_manifest_budget_safe_combined
- selected_regimes: H0, H1, H2
- shots_submitted_per_circuit: [1024]
- job_ids_recorded_for_H0_H1_H2: True
- budget_safe_partial_submission: True
- total_circuits_submitted: 900

## H0

- created_utc: 2026-05-09T08:42:05Z
- selected_backend: ibm_fez
- backend_version: 2
- regime_label: Sampler unmitigated baseline
- circuits: 300
- shots_submitted: 1024
- job_id: d7vf6n3ack5s73bfc0eg
- status_at_submission: QUEUED
- runtime_options_sha256: c962a9bc5dcbbf3b24b6e0d0416fd0411dee5291889ea7dc9bd54cb14ee134af
- scope_lock_confirmed: True
- rma_excluded: True
- wave2_excluded: True

## H1

- created_utc: 2026-05-09T08:46:26Z
- selected_backend: ibm_fez
- backend_version: 2
- regime_label: Sampler + dynamical decoupling only
- circuits: 300
- shots_submitted: 1024
- job_id: d7vf8ocinasc738u1bhg
- status_at_submission: QUEUED
- runtime_options_sha256: f3db14fe06202c2a9385947a052d52904e6594668dc407ac5fdd6ae4d0032ebd
- scope_lock_confirmed: True
- rma_excluded: True
- wave2_excluded: True

## H2

- created_utc: 2026-05-09T08:53:05Z
- selected_backend: ibm_fez
- backend_version: 2
- regime_label: Sampler + Pauli/gate twirling only
- circuits: 300
- shots_submitted: 1024
- job_id: d7vfbsfmrars73d84u20
- status_at_submission: QUEUED
- runtime_options_sha256: 74bf3e5285a619ead97b0fc252eb5228263dab169863a74f795f3b3bf97e37e7
- scope_lock_confirmed: True
- rma_excluded: True
- wave2_excluded: True

