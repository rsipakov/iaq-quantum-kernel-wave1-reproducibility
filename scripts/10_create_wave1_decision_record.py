#!/usr/bin/env python3
"""
Step 9.10: create Wave 1 decision record.

Allowed decisions:
- STOP_AFTER_WAVE1_REPORT_RESULTS
- PROCEED_TO_WAVE2_SENTINEL_ONLY
- RETRY_WAVE1_WITH_DOCUMENTED_REASON
- NO_GO_HARDWARE_RESULTS_UNUSABLE

Wave 2 is not automatic. RMA remains deferred regardless of favorable ZZ4
hardware-survival metrics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from common import (
    ALLOWED_DECISIONS,
    ensure_output_dirs,
    load_paths,
    load_scope,
    parser_with_project,
    read_json,
    resolve_project_path,
    sha256_file,
    utc_now,
    write_safe_json,
)


def _auto_decision(summary: Dict[str, Any], kernel_manifest: Dict[str, Any], retrieval_manifest: Dict[str, Any]) -> str:
    if not retrieval_manifest.get("retrieved_or_failures_recorded"):
        return "RETRY_WAVE1_WITH_DOCUMENTED_REASON"
    if not kernel_manifest.get("kernel_matrices_shape_24x24"):
        return "NO_GO_HARDWARE_RESULTS_UNUSABLE"
    if not summary.get("all_required_regimes_reported"):
        return "NO_GO_HARDWARE_RESULTS_UNUSABLE"
    # Conservative default: report Wave 1 results, do not automatically proceed.
    return "STOP_AFTER_WAVE1_REPORT_RESULTS"


def main() -> int:
    parser = parser_with_project("Step 9.10 create Wave 1 decision record.")
    parser.add_argument("--decision", default="AUTO", choices=["AUTO"] + sorted(ALLOWED_DECISIONS), help="Decision to record. AUTO defaults conservatively.")
    parser.add_argument("--rationale", default="", help="Human rationale for the decision.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)
    outputs = paths["outputs"]

    failure_reasons: List[str] = []
    try:
        summary = read_json(resolve_project_path(project_root, outputs["distortion_summary_json"]))
    except Exception as exc:
        summary = {}
        failure_reasons.append(f"cannot read distortion summary: {type(exc).__name__}: {exc}")
    try:
        kernel_manifest = read_json(resolve_project_path(project_root, outputs["kernel_manifest"]))
    except Exception as exc:
        kernel_manifest = {}
        failure_reasons.append(f"cannot read kernel manifest: {type(exc).__name__}: {exc}")
    try:
        retrieval_manifest = read_json(resolve_project_path(project_root, outputs["retrieval_manifest"]))
    except Exception as exc:
        retrieval_manifest = {}
        failure_reasons.append(f"cannot read retrieval manifest: {type(exc).__name__}: {exc}")

    decision = _auto_decision(summary, kernel_manifest, retrieval_manifest) if args.decision == "AUTO" else args.decision
    if decision not in ALLOWED_DECISIONS:
        failure_reasons.append(f"invalid decision: {decision}")

    if decision == "PROCEED_TO_WAVE2_SENTINEL_ONLY" and not args.rationale.strip():
        failure_reasons.append("PROCEED_TO_WAVE2_SENTINEL_ONLY requires an explicit rationale")
    if decision == "PROCEED_TO_WAVE2_SENTINEL_ONLY":
        wave2_status = "sentinel_only_planning_allowed_after_this_record"
    else:
        wave2_status = "not_allowed_without_new_decision_record"

    record = {
        "artifact_type": "zz4_wave1_decision_record",
        "schema_version": "v9.0.decision_record.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "decision": decision,
        "decision_record_created": not failure_reasons,
        "rationale": args.rationale.strip() or "AUTO conservative default: report Wave 1 results; do not proceed automatically.",
        "allowed_decisions": sorted(ALLOWED_DECISIONS),
        "wave2_status": wave2_status,
        "wave2_allowed_regimes_if_proceed": ["H3", "H4", "H5"] if decision == "PROCEED_TO_WAVE2_SENTINEL_ONLY" else [],
        "wave2_full_300_pair_execution_allowed": False,
        "rma_hardware_status": "DEFER",
        "rma_excluded": True,
        "scope_restrictions": {
            "allowed_kernel": scope["allowed_kernel"],
            "allowed_feature_set": scope["allowed_feature_set"],
            "allowed_subset": scope["allowed_subset"],
            "allowed_wave1_regimes": scope["allowed_wave1_regimes"],
            "blocked_indefinitely_in_v9": scope["blocked_indefinitely_in_v9"],
        },
        "claims_policy": scope["claims_policy"],
        "retrieval_manifest_sha256": sha256_file(resolve_project_path(project_root, outputs["retrieval_manifest"])),
        "kernel_manifest_sha256": sha256_file(resolve_project_path(project_root, outputs["kernel_manifest"])),
        "distortion_summary_sha256": sha256_file(resolve_project_path(project_root, outputs["distortion_summary_json"])),
        "failure_reasons": failure_reasons,
        "token_value_absent_from_artifact": True,
    }

    out_path = resolve_project_path(project_root, outputs["decision_record"])
    write_safe_json(out_path, record)

    print(f"[decision] decision_record_created={not failure_reasons} decision={decision} -> {out_path}")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
