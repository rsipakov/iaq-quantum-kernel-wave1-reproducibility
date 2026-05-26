#!/usr/bin/env python3
"""
Step 9.6: submit H0/H1/H2 Wave 1 IBM hardware jobs.

Safety:
- The script refuses to submit unless preflight_pass=true.
- It refuses to submit unless --confirm-submit YES is supplied.
- It does not print or persist IBM token values.
- By default, it uses job mode (SamplerV2(mode=backend)), not session mode.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from common import (
    ensure_output_dirs,
    get_backend,
    get_runtime_options_hashes,
    load_paths,
    load_scope,
    load_service,
    package_versions,
    parser_with_project,
    read_csv_rows,
    read_json,
    resolve_project_path,
    sha256_file,
    utc_now,
    write_csv_rows,
    write_safe_json,
    write_text,
)


def _apply_options(sampler: Any, options: Dict[str, Any]) -> None:
    """Use the SamplerOptions.update API when available; fall back to attribute update."""
    try:
        sampler.options.update(**options)
        return
    except Exception:
        pass
    for key, value in options.items():
        try:
            setattr(sampler.options, key, value)
        except Exception:
            pass


def main() -> int:
    parser = parser_with_project("Step 9.6 submit H0/H1/H2 Wave 1 IBM hardware jobs.")
    parser.add_argument("--confirm-submit", default="NO", help="Must be exactly YES to submit real hardware jobs.")
    parser.add_argument("--dry-run", action="store_true", help="Write a dry-run manifest without submitting jobs.")
    parser.add_argument("--backend", default=None, help="Override backend name. Must still pass preflight scope.")
    parser.add_argument(
        "--regimes",
        default="H0,H1,H2",
        help="Comma-separated regimes to submit, e.g. H0 or H0,H1. Must be subset of H0,H1,H2.",
    )
    parser.add_argument(
        "--shots-override",
        type=int,
        default=None,
        help="Optional shots override for budget-safe pilot, e.g. 1024.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)
    outputs = paths["outputs"]
    inputs = paths["input_artifacts"]

    failure_reasons: List[str] = []
    preflight_path = resolve_project_path(project_root, outputs["preflight_report"])
    if not preflight_path.exists():
        failure_reasons.append("preflight report missing; run 04_validate_wave1_preflight.py first")
        preflight = {}
    else:
        preflight = read_json(preflight_path)
        if preflight.get("preflight_pass") is not True:
            failure_reasons.append("preflight_pass is not true")

    runtime_options = read_json(resolve_project_path(project_root, outputs["runtime_options"]))
    live_metadata = read_json(resolve_project_path(project_root, outputs["live_backend_metadata"]))

    selected_backend = args.backend or live_metadata.get("selected_backend") or scope["selected_backend"]
    if selected_backend not in scope["allowed_backends"]:
        failure_reasons.append(f"backend not allowed by scope: {selected_backend}")

    selected_regimes = [r.strip() for r in str(args.regimes).split(",") if r.strip()]
    allowed_regimes = list(scope["allowed_wave1_regimes"])
    invalid_regimes = [r for r in selected_regimes if r not in allowed_regimes]
    if not selected_regimes:
        failure_reasons.append("no regimes selected")
    if invalid_regimes:
        failure_reasons.append(f"selected regimes not allowed by scope: {invalid_regimes}; allowed={allowed_regimes}")

    selected_shots = int(args.shots_override or scope["shots_planned_per_circuit"])
    if selected_shots <= 0:
        failure_reasons.append(f"shots must be positive, got {selected_shots}")
    if selected_shots > int(scope["shots_planned_per_circuit"]):
        failure_reasons.append(
            f"shots override {selected_shots} exceeds planned shots {scope['shots_planned_per_circuit']}"
        )

    real_submit = args.confirm_submit == "YES" and not args.dry_run
    if not real_submit:
        failure_reasons_for_manifest = list(failure_reasons)
        if args.confirm_submit != "YES":
            failure_reasons_for_manifest.append("real submission not confirmed; run with --confirm-submit YES to submit")
        if args.dry_run:
            failure_reasons_for_manifest.append("dry-run requested")
    else:
        failure_reasons_for_manifest = list(failure_reasons)

    manifest_rows: List[Dict[str, Any]] = []
    submission_log_lines = [
        f"# ZZ4 Wave 1 submission log\n\n",
        f"- created_utc: {utc_now()}\n",
        f"- operator_identifier: {args.operator}\n",
        f"- selected_backend: {selected_backend}\n",
        f"- real_submit: {real_submit}\n",
        f"- scope: ZZ4 / F_quantum_4 / frozen N=24 / H0-H2 only\n",
        f"- selected_regimes: {selected_regimes}\n",
        f"- shots_submitted_per_circuit: {selected_shots}\n\n",
    ]

    if failure_reasons:
        real_submit = False

    if real_submit:
        try:
            import qiskit.qpy as qpy
            from qiskit.transpiler import generate_preset_pass_manager
            from qiskit_ibm_runtime import SamplerV2 as Sampler

            service = load_service()
            backend = get_backend(service, selected_backend)
            pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

            with resolve_project_path(project_root, outputs["circuit_qpy"]).open("rb") as f:
                circuits = list(qpy.load(f))
            circuit_index = read_csv_rows(resolve_project_path(project_root, outputs["circuit_index"]))

            for regime in selected_regimes:
                regime_indices = [idx for idx, row in enumerate(circuit_index) if row.get("regime") == regime]
                regime_circuits = [circuits[idx] for idx in regime_indices]
                if len(regime_circuits) != scope["pair_count_expected"]:
                    raise RuntimeError(f"{regime}: expected {scope['pair_count_expected']} circuits, got {len(regime_circuits)}")

                submission_log_lines.append(f"## {regime}\n\n")
                submission_log_lines.append(f"- circuits: {len(regime_circuits)}\n")
                isa_circuits = pm.run(regime_circuits)
                sampler = Sampler(mode=backend)
                opts = runtime_options["regimes"][regime]["sampler_options"]
                _apply_options(sampler, opts)

                # SamplerV2 accepts circuit PUBs. Keep one PUB per circuit so retrieval order maps
                # directly to circuit_index rows for this regime.
                pubs = [(circ,) for circ in isa_circuits]
                job = sampler.run(pubs, shots=int(selected_shots))
                job_id = job.job_id()
                status = str(job.status())
                opt_hash = get_runtime_options_hashes(runtime_options).get(f"runtime_options_sha256_{regime}")

                manifest_rows.append({
                    "artifact_type": "zz4_wave1_job_manifest_row",
                    "created_utc": utc_now(),
                    "operator_identifier": args.operator,
                    "selected_backend": selected_backend,
                    "backend_version": live_metadata.get("backend_version"),
                    "session_id_if_used": None,
                    "regime_id": regime,
                    "regime_label": runtime_options["regimes"][regime].get("regime_label"),
                    "job_id": job_id,
                    "job_status_at_submission": status,
                    "primitive_name": runtime_options.get("primitive_name", "SamplerV2"),
                    "runtime_options_sha256": opt_hash,
                    "shots_submitted": selected_shots,
                    "circuit_count_submitted": len(regime_circuits),
                    "pair_count_covered": scope["pair_count_expected"],
                    "execution_manifest_sha256": sha256_file(resolve_project_path(project_root, inputs["execution_manifest"])),
                    "circuit_inventory_sha256": sha256_file(resolve_project_path(project_root, inputs["circuit_inventory"])),
                    "pair_inventory_sha256": sha256_file(resolve_project_path(project_root, inputs["pair_inventory"])),
                    "live_backend_metadata_sha256": sha256_file(resolve_project_path(project_root, outputs["live_backend_metadata"])),
                    "scope_lock_confirmed": True,
                    "rma_excluded": True,
                    "wave2_excluded": True,
                    "failure_or_exception_if_any": "",
                })
                submission_log_lines.append(f"- job_id: {job_id}\n")
                submission_log_lines.append(f"- status_at_submission: {status}\n\n")
        except Exception as exc:
            failure_reasons_for_manifest.append(f"submission failed: {type(exc).__name__}: {exc}")
            submission_log_lines.append(f"\nSubmission failed: {type(exc).__name__}: {exc}\n")
    else:
        # Dry-run manifest rows keep the intended scope visible without creating IBM jobs.
        for regime in selected_regimes:
            manifest_rows.append({
                "artifact_type": "zz4_wave1_job_manifest_row",
                "created_utc": utc_now(),
                "operator_identifier": args.operator,
                "selected_backend": selected_backend,
                "backend_version": live_metadata.get("backend_version"),
                "session_id_if_used": None,
                "regime_id": regime,
                "regime_label": runtime_options["regimes"][regime].get("regime_label"),
                "job_id": "DRY_RUN_NOT_SUBMITTED",
                "job_status_at_submission": "NOT_SUBMITTED",
                "primitive_name": runtime_options.get("primitive_name", "SamplerV2"),
                "runtime_options_sha256": get_runtime_options_hashes(runtime_options).get(f"runtime_options_sha256_{regime}"),
                "shots_submitted": selected_shots,
                "circuit_count_submitted": scope["pair_count_expected"],
                "pair_count_covered": scope["pair_count_expected"],
                "execution_manifest_sha256": sha256_file(resolve_project_path(project_root, inputs["execution_manifest"])),
                "circuit_inventory_sha256": sha256_file(resolve_project_path(project_root, inputs["circuit_inventory"])),
                "pair_inventory_sha256": sha256_file(resolve_project_path(project_root, inputs["pair_inventory"])),
                "live_backend_metadata_sha256": sha256_file(resolve_project_path(project_root, outputs["live_backend_metadata"])),
                "scope_lock_confirmed": preflight.get("preflight_pass") is True,
                "rma_excluded": True,
                "wave2_excluded": True,
                "failure_or_exception_if_any": "; ".join(failure_reasons_for_manifest),
            })

    submitted_job_ids = [r["job_id"] for r in manifest_rows if r["job_id"] and r["job_id"] != "DRY_RUN_NOT_SUBMITTED"]
    job_ids_recorded_for_selected_regimes = (
        len(submitted_job_ids) == len(selected_regimes)
        and all(r["job_id"] != "DRY_RUN_NOT_SUBMITTED" for r in manifest_rows)
        and not any(r.get("failure_or_exception_if_any") for r in manifest_rows)
    )

    # Full v9 terminal condition remains true only if all H0/H1/H2 were submitted.
    job_ids_recorded_for_H0_H1_H2 = (
        set(selected_regimes) == set(scope["allowed_wave1_regimes"])
        and job_ids_recorded_for_selected_regimes
    )

    manifest = {
        "artifact_type": "zz4_wave1_job_manifest",
        "schema_version": "v9.0.job_manifest.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "selected_backend": selected_backend,
        "backend_version": live_metadata.get("backend_version"),
        "job_ids_recorded_for_H0_H1_H2": job_ids_recorded_for_H0_H1_H2,
        "job_ids_recorded_for_selected_regimes": job_ids_recorded_for_selected_regimes,
        "selected_regimes": selected_regimes,
        "shots_submitted_per_circuit": selected_shots,
        "budget_safe_partial_submission": set(selected_regimes) != set(scope["allowed_wave1_regimes"]) or selected_shots != int(scope["shots_planned_per_circuit"]),
        "real_submit": real_submit,
        "confirm_submit_value": "YES" if args.confirm_submit == "YES" else "not_yes",
        "rows": manifest_rows,
        "failure_reasons": failure_reasons_for_manifest,
        "scope_lock_confirmed": preflight.get("preflight_pass") is True,
        "rma_excluded": True,
        "wave2_excluded": True,
        "token_value_absent_from_artifact": True,
        **package_versions(),
    }

    json_path = resolve_project_path(project_root, outputs["job_manifest_json"])
    csv_path = resolve_project_path(project_root, outputs["job_manifest_csv"])
    log_path = resolve_project_path(project_root, outputs["submission_log"])
    write_safe_json(json_path, manifest)
    write_csv_rows(csv_path, manifest_rows)
    write_text(log_path, "".join(submission_log_lines))

    print(f"[submit] job_ids_recorded_for_selected_regimes={job_ids_recorded_for_selected_regimes} -> {json_path}")
    print(f"[submit] job_ids_recorded_for_H0_H1_H2={job_ids_recorded_for_H0_H1_H2}")
    print(f"[submit] selected_regimes={selected_regimes}; shots={selected_shots}")

    if args.dry_run:
        print("  - dry-run completed successfully; no IBM jobs were submitted")
        return 0

    if not job_ids_recorded_for_selected_regimes:
        for reason in failure_reasons_for_manifest:
            print(f"  - {reason}")
        return 2

    if not job_ids_recorded_for_H0_H1_H2:
        print("  - budget-safe partial submission completed; full H0/H1/H2 terminal condition is not yet met")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
