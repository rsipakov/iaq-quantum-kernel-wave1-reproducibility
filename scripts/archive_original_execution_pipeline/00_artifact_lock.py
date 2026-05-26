#!/usr/bin/env python3
"""
Step 9.1: artifact lock and final pre-submit review.

This script freezes the hash state of the Step 8 / v8b artifacts that the v9
Wave 1 submission depends on. It does not contact IBM Quantum and does not need
an IBM token.

Hard-stop logic:
- authorization must be GO when the file is present;
- pair/circuit inventory row counts must match 300/900;
- generated output tree must not contain token-like values;
- scope restrictions are repeated in the artifact so later scripts can compare.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from common import (
    count_csv_rows,
    ensure_output_dirs,
    file_record,
    load_paths,
    load_scope,
    parser_with_project,
    read_json,
    resolve_project_path,
    scan_tree_for_secret_values,
    utc_now,
    write_safe_json,
)


def main() -> int:
    parser = parser_with_project("Step 9.1 artifact lock and final pre-submit review.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)

    input_artifacts = paths["input_artifacts"]
    records: Dict[str, Dict[str, Any]] = {name: file_record(project_root, rel) for name, rel in input_artifacts.items()}

    failure_reasons: List[str] = []

    # Authorization file: required by v9. It should contain decision=GO.
    auth_rel = input_artifacts["v8b_authorization"]
    auth_path = resolve_project_path(project_root, auth_rel)
    auth_decision = None
    if not auth_path.exists():
        failure_reasons.append(f"missing v8b authorization artifact: {auth_rel}")
    else:
        try:
            auth = read_json(auth_path)
            auth_decision = auth.get("decision") or auth.get("authorization_decision")
            if auth_decision != "GO":
                failure_reasons.append(f"v8b authorization decision is not GO: {auth_decision}")
        except Exception as exc:
            failure_reasons.append(f"cannot parse v8b authorization artifact: {exc}")

    # Inventory counts: these are the core v9 scope lock.
    pair_rel = input_artifacts["pair_inventory"]
    circuit_rel = input_artifacts["circuit_inventory"]
    pair_rows = count_csv_rows(resolve_project_path(project_root, pair_rel))
    circuit_rows = count_csv_rows(resolve_project_path(project_root, circuit_rel))
    if pair_rows != scope["pair_count_expected"]:
        failure_reasons.append(f"pair inventory row count mismatch: expected {scope['pair_count_expected']}, got {pair_rows}")
    if circuit_rows != scope["circuit_count_expected"]:
        failure_reasons.append(f"circuit inventory row count mismatch: expected {scope['circuit_count_expected']}, got {circuit_rows}")

    # Secret scan over the output folder only. The package never scans arbitrary user home directories.
    outputs_root = resolve_project_path(project_root, "step6b_hardware_subset_package/outputs")
    secret_findings = scan_tree_for_secret_values(outputs_root)
    if secret_findings:
        failure_reasons.append("secret-like token values detected in generated output tree")

    scope_lock_pass = not failure_reasons
    artifact = {
        "artifact_type": "zz_only_step9_artifact_lock",
        "schema_version": "v9.0.artifact_lock.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "project_root": str(project_root),
        "scope_lock_pass": scope_lock_pass,
        "failure_reasons": failure_reasons,
        "v8b_authorization_decision": auth_decision,
        "selected_backend": scope["selected_backend"],
        "allowed_backends": scope["allowed_backends"],
        "allowed_kernel": scope["allowed_kernel"],
        "allowed_feature_set": scope["allowed_feature_set"],
        "allowed_subset": scope["allowed_subset"],
        "allowed_wave1_regimes": scope["allowed_wave1_regimes"],
        "rma_excluded": True,
        "wave2_excluded": True,
        "threshold_relaxation_excluded": True,
        "pair_count_expected": scope["pair_count_expected"],
        "pair_count_observed": pair_rows,
        "circuit_count_expected": scope["circuit_count_expected"],
        "circuit_count_observed": circuit_rows,
        "input_artifact_records": records,
        "token_value_absent_from_artifact": True,
        "local_secret_scan": {
            "scan_root": str(outputs_root),
            "status": "passed" if not secret_findings else "failed",
            "finding_count": sum(len(v) for v in secret_findings.values()),
            "findings": secret_findings,
        },
    }

    out_rel = paths["outputs"]["artifact_lock"]
    out_path = resolve_project_path(project_root, out_rel)
    write_safe_json(out_path, artifact)

    # v9 plan also recommends an audit freeze manifest. Keep it as an alias/superset.
    audit_rel = paths["outputs"]["audit_freeze_manifest"]
    audit_path = resolve_project_path(project_root, audit_rel)
    audit = dict(artifact)
    audit["artifact_type"] = "v9_audit_freeze_manifest"
    write_safe_json(audit_path, audit)

    print(f"[step9.1] scope_lock_pass={scope_lock_pass} -> {out_path}")
    if not scope_lock_pass:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
