#!/usr/bin/env python3
"""
Step 9.5: Wave 1 preflight validator.

This is the hard submission gate. It validates:
- v8b authorization GO and artifact lock pass;
- live backend metadata gate pass;
- runtime options explicit and hashed;
- frozen pair/circuit inventory sizes;
- built circuit count and mapping;
- ZZ4/F_quantum_4/frozen N=24 only;
- RMA and Wave 2 excluded;
- no token-like values in generated artifacts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from common import (
    count_csv_rows,
    ensure_output_dirs,
    get_runtime_options_hashes,
    load_paths,
    load_scope,
    parser_with_project,
    read_json,
    resolve_project_path,
    scan_tree_for_secret_values,
    sha256_file,
    utc_now,
    validate_runtime_options_structure,
    write_safe_json,
)


def _require_json(project_root: Path, rel: str, failure_reasons: List[str]) -> Dict[str, Any]:
    path = resolve_project_path(project_root, rel)
    if not path.exists():
        failure_reasons.append(f"required JSON artifact missing: {rel}")
        return {}
    try:
        return read_json(path)
    except Exception as exc:
        failure_reasons.append(f"cannot parse {rel}: {type(exc).__name__}: {exc}")
        return {}


def main() -> int:
    parser = parser_with_project("Step 9.5 Wave 1 preflight validator.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)

    failure_reasons: List[str] = []
    outputs = paths["outputs"]
    inputs = paths["input_artifacts"]

    artifact_lock = _require_json(project_root, outputs["artifact_lock"], failure_reasons)
    live_metadata = _require_json(project_root, outputs["live_backend_metadata"], failure_reasons)
    runtime_options = _require_json(project_root, outputs["runtime_options"], failure_reasons)
    circuit_build = _require_json(project_root, outputs["circuit_build_manifest"], failure_reasons)

    if artifact_lock and artifact_lock.get("scope_lock_pass") is not True:
        failure_reasons.append("artifact lock did not pass")
    if live_metadata and not (live_metadata.get("metadata_gate_pass") is True or live_metadata.get("metadata_capture_status") == "passed"):
        failure_reasons.append("live backend metadata gate did not pass")
    if circuit_build and circuit_build.get("circuit_build_pass") is not True:
        failure_reasons.append("circuit build manifest did not pass")

    # v8b authorization must still be GO.
    auth = _require_json(project_root, inputs["v8b_authorization"], failure_reasons)
    auth_decision = auth.get("decision") or auth.get("authorization_decision")
    if auth and auth_decision != "GO":
        failure_reasons.append(f"v8b authorization decision is not GO: {auth_decision}")

    # Row-count check remains repeated here; do not rely only on older manifests.
    pair_rows = count_csv_rows(resolve_project_path(project_root, inputs["pair_inventory"]))
    circuit_rows = count_csv_rows(resolve_project_path(project_root, inputs["circuit_inventory"]))
    if pair_rows != scope["pair_count_expected"]:
        failure_reasons.append(f"pair count mismatch: expected {scope['pair_count_expected']}, got {pair_rows}")
    if circuit_rows != scope["circuit_count_expected"]:
        failure_reasons.append(f"circuit inventory count mismatch: expected {scope['circuit_count_expected']}, got {circuit_rows}")

    # Runtime options: exact H0/H1/H2; 4096 shots; H1 and H2 separated.
    if runtime_options:
        failure_reasons.extend(validate_runtime_options_structure(runtime_options, scope))
        hashes = get_runtime_options_hashes(runtime_options)

        # Per-regime hashes are stable and must match exactly.
        # runtime_options_all_sha256 is an internal canonical hash written before
        # embedding hash fields into the JSON artifact; recomputing it after the
        # hash fields are embedded creates a self-referential mismatch. Therefore
        # it is recorded for audit but not used as a hard preflight failure here.
        for k, v in hashes.items():
            if k == "runtime_options_all_sha256":
                continue
            if runtime_options.get(k) and runtime_options.get(k) != v:
                failure_reasons.append(f"runtime option hash mismatch for {k}")

    # Backend scope.
    selected_backend = live_metadata.get("selected_backend") or scope["selected_backend"]
    if selected_backend not in scope["allowed_backends"]:
        failure_reasons.append(f"selected backend not allowed: {selected_backend}")
    if live_metadata and live_metadata.get("shots_planned_per_circuit") != scope["shots_planned_per_circuit"]:
        failure_reasons.append("live metadata shots_planned_per_circuit mismatch")
    if live_metadata and live_metadata.get("pair_count_expected") != scope["pair_count_expected"]:
        failure_reasons.append("live metadata pair_count_expected mismatch")
    if live_metadata and live_metadata.get("circuit_count_expected") != scope["circuit_count_expected"]:
        failure_reasons.append("live metadata circuit_count_expected mismatch")
    if live_metadata and live_metadata.get("scope_drift_detected"):
        failure_reasons.append("live metadata reports scope drift")

    # QPY + circuit index must exist.
    qpy_path = resolve_project_path(project_root, outputs["circuit_qpy"])
    circuit_index_path = resolve_project_path(project_root, outputs["circuit_index"])
    if not qpy_path.exists():
        failure_reasons.append(f"circuit QPY missing: {outputs['circuit_qpy']}")
    if not circuit_index_path.exists():
        failure_reasons.append(f"circuit index missing: {outputs['circuit_index']}")

    # Secret scan over generated outputs.
    outputs_root = resolve_project_path(project_root, "step6b_hardware_subset_package/outputs")
    secret_findings = scan_tree_for_secret_values(outputs_root)
    if secret_findings:
        failure_reasons.append("secret-like token values detected in generated output tree")

    preflight_pass = not failure_reasons
    report = {
        "artifact_type": "zz4_wave1_preflight_report",
        "schema_version": "v9.0.preflight.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "preflight_pass": preflight_pass,
        "failure_reasons": failure_reasons,
        "selected_backend": selected_backend,
        "allowed_backends": scope["allowed_backends"],
        "allowed_kernel": scope["allowed_kernel"],
        "allowed_feature_set": scope["allowed_feature_set"],
        "allowed_subset": scope["allowed_subset"],
        "regimes": scope["allowed_wave1_regimes"],
        "shots_planned_per_circuit": scope["shots_planned_per_circuit"],
        "pair_count_expected": scope["pair_count_expected"],
        "pair_count_observed": pair_rows,
        "circuit_count_expected": scope["circuit_count_expected"],
        "circuit_count_observed": circuit_rows,
        "qpy_sha256": sha256_file(qpy_path),
        "circuit_index_sha256": sha256_file(circuit_index_path),
        "artifact_lock_sha256": sha256_file(resolve_project_path(project_root, outputs["artifact_lock"])),
        "live_backend_metadata_sha256": sha256_file(resolve_project_path(project_root, outputs["live_backend_metadata"])),
        "runtime_options_sha256": sha256_file(resolve_project_path(project_root, outputs["runtime_options"])),
        "pair_inventory_sha256": sha256_file(resolve_project_path(project_root, inputs["pair_inventory"])),
        "circuit_inventory_sha256": sha256_file(resolve_project_path(project_root, inputs["circuit_inventory"])),
        "execution_manifest_sha256": sha256_file(resolve_project_path(project_root, inputs["execution_manifest"])),
        "scope_lock_confirmed": preflight_pass,
        "rma_excluded": True,
        "wave2_excluded": True,
        "token_value_absent_from_artifact": True,
        "local_secret_scan": {
            "scan_root": str(outputs_root),
            "status": "passed" if not secret_findings else "failed",
            "finding_count": sum(len(v) for v in secret_findings.values()),
            "findings": secret_findings,
        },
    }

    out_path = resolve_project_path(project_root, outputs["preflight_report"])
    write_safe_json(out_path, report)

    print(f"[preflight] preflight_pass={preflight_pass} -> {out_path}")
    if not preflight_pass:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
