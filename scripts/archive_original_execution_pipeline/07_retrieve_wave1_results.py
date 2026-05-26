#!/usr/bin/env python3
"""
Step 9.7: retrieve Wave 1 hardware results.

This script reads zz4_wave1_job_manifest.json, retrieves each real job, extracts
SamplerV2 counts per PUB/circuit, and writes regime-specific raw result JSON
artifacts. It can either poll until final states (--wait) or record current
statuses without blocking.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from common import (
    ensure_output_dirs,
    load_paths,
    load_scope,
    load_service,
    parser_with_project,
    read_json,
    resolve_project_path,
    to_jsonable,
    utc_now,
    write_safe_json,
    write_text,
)


def _extract_counts_from_pub(pub_result: Any) -> Dict[str, int]:
    data = getattr(pub_result, "data", None)
    if data is None:
        return {}
    # Preferred default register name for SamplerV2 examples.
    for reg_name in ("meas", "c", "clbits"):
        reg = getattr(data, reg_name, None)
        if reg is not None:
            get_counts = getattr(reg, "get_counts", None)
            if callable(get_counts):
                try:
                    return {str(k): int(v) for k, v in get_counts().items()}
                except Exception:
                    pass
    # Generic fallback: inspect attributes and pick first BitArray-like object.
    for name in dir(data):
        if name.startswith("_"):
            continue
        reg = getattr(data, name, None)
        get_counts = getattr(reg, "get_counts", None)
        if callable(get_counts):
            try:
                return {str(k): int(v) for k, v in get_counts().items()}
            except Exception:
                continue
    return {}


def _result_payload(result: Any, regime: str, job_id: str, circuit_count_hint: int) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    try:
        result_list = list(result)
    except Exception:
        result_list = []

    for idx, pub in enumerate(result_list):
        counts = _extract_counts_from_pub(pub)
        entries.append({
            "pub_order": idx,
            "counts": counts,
            "shots_observed": int(sum(counts.values())) if counts else None,
            "metadata": to_jsonable(getattr(pub, "metadata", None)),
        })

    return {
        "artifact_type": "zz4_wave1_raw_results",
        "schema_version": "v9.0.raw_results.1",
        "created_utc": utc_now(),
        "regime_id": regime,
        "job_id": job_id,
        "circuit_count_hint": circuit_count_hint,
        "pub_result_count": len(entries),
        "entries": entries,
        "raw_result_summary": to_jsonable(result, max_str_len=5000),
        "token_value_absent_from_artifact": True,
    }


def main() -> int:
    parser = parser_with_project("Step 9.7 retrieve Wave 1 hardware results.")
    parser.add_argument("--wait", action="store_true", help="Poll until jobs reach final states or timeout.")
    parser.add_argument("--poll-seconds", type=int, default=60, help="Polling interval when --wait is used.")
    parser.add_argument("--timeout-seconds", type=int, default=21600, help="Max wait time. Default: 6 hours.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)
    outputs = paths["outputs"]

    manifest_path = resolve_project_path(project_root, outputs["job_manifest_json"])
    job_manifest = read_json(manifest_path)

    service = None
    real_jobs = [r for r in job_manifest.get("rows", []) if r.get("job_id") and r.get("job_id") != "DRY_RUN_NOT_SUBMITTED"]
    if real_jobs:
        service = load_service()

    retrieval_rows: List[Dict[str, Any]] = []
    log_lines = [
        "# ZZ4 Wave 1 retrieval log\n\n",
        f"- created_utc: {utc_now()}\n",
        f"- operator_identifier: {args.operator}\n",
        f"- real_job_count: {len(real_jobs)}\n\n",
    ]
    failure_reasons: List[str] = []

    for row in job_manifest.get("rows", []):
        regime = row.get("regime_id")
        job_id = row.get("job_id")
        raw_rel = f"step6b_hardware_subset_package/outputs/hardware_results/zz4_{regime}_raw_results.json"
        raw_path = resolve_project_path(project_root, raw_rel)

        if not job_id or job_id == "DRY_RUN_NOT_SUBMITTED":
            reason = "job was not submitted"
            failure_reasons.append(f"{regime}: {reason}")
            payload = {
                "artifact_type": "zz4_wave1_raw_results",
                "schema_version": "v9.0.raw_results.1",
                "created_utc": utc_now(),
                "regime_id": regime,
                "job_id": job_id,
                "retrieval_status": "not_retrieved",
                "failure_reason": reason,
                "entries": [],
                "token_value_absent_from_artifact": True,
            }
            write_safe_json(raw_path, payload)
            retrieval_rows.append({
                "regime_id": regime,
                "job_id": job_id,
                "retrieved_status": "not_retrieved",
                "raw_result_path": raw_rel,
                "pub_result_count": 0,
                "failure_or_exception_if_any": reason,
            })
            continue

        try:
            job = service.job(job_id)
            start = time.time()
            while args.wait and not job.in_final_state():
                if time.time() - start > args.timeout_seconds:
                    break
                log_lines.append(f"- {utc_now()} {regime} {job_id} status={job.status()}\n")
                time.sleep(args.poll_seconds)

            status = str(job.status())
            final = bool(job.in_final_state())
            errored = bool(job.errored()) if hasattr(job, "errored") else False
            error_msg = job.error_message() if errored and hasattr(job, "error_message") else None

            if final and not errored and status not in ("CANCELLED", "ERROR"):
                result = job.result()
                payload = _result_payload(result, regime, job_id, int(row.get("circuit_count_submitted") or scope["pair_count_expected"]))
                payload["retrieval_status"] = "retrieved"
                payload["job_status_at_retrieval"] = status
                try:
                    payload["job_metrics"] = to_jsonable(job.metrics())
                except Exception:
                    payload["job_metrics"] = None
                try:
                    payload["job_logs"] = to_jsonable(job.logs(), max_str_len=5000)
                except Exception:
                    payload["job_logs"] = None
                write_safe_json(raw_path, payload)
                retrieval_rows.append({
                    "regime_id": regime,
                    "job_id": job_id,
                    "retrieved_status": "retrieved",
                    "job_status": status,
                    "raw_result_path": raw_rel,
                    "pub_result_count": payload["pub_result_count"],
                    "failure_or_exception_if_any": "",
                })
            else:
                reason = f"job not retrieved: status={status}, final={final}, error={error_msg}"
                failure_reasons.append(f"{regime}: {reason}")
                payload = {
                    "artifact_type": "zz4_wave1_raw_results",
                    "schema_version": "v9.0.raw_results.1",
                    "created_utc": utc_now(),
                    "regime_id": regime,
                    "job_id": job_id,
                    "retrieval_status": "not_retrieved",
                    "job_status_at_retrieval": status,
                    "failure_reason": reason,
                    "entries": [],
                    "token_value_absent_from_artifact": True,
                }
                write_safe_json(raw_path, payload)
                retrieval_rows.append({
                    "regime_id": regime,
                    "job_id": job_id,
                    "retrieved_status": "not_retrieved",
                    "job_status": status,
                    "raw_result_path": raw_rel,
                    "pub_result_count": 0,
                    "failure_or_exception_if_any": reason,
                })
        except Exception as exc:
            reason = f"retrieval failed: {type(exc).__name__}: {exc}"
            failure_reasons.append(f"{regime}: {reason}")
            payload = {
                "artifact_type": "zz4_wave1_raw_results",
                "schema_version": "v9.0.raw_results.1",
                "created_utc": utc_now(),
                "regime_id": regime,
                "job_id": job_id,
                "retrieval_status": "failed",
                "failure_reason": reason,
                "entries": [],
                "token_value_absent_from_artifact": True,
            }
            write_safe_json(raw_path, payload)
            retrieval_rows.append({
                "regime_id": regime,
                "job_id": job_id,
                "retrieved_status": "failed",
                "raw_result_path": raw_rel,
                "pub_result_count": 0,
                "failure_or_exception_if_any": reason,
            })

    retrieved_or_failures_recorded = len(retrieval_rows) == len(job_manifest.get("rows", []))
    manifest = {
        "artifact_type": "zz4_wave1_retrieval_manifest",
        "schema_version": "v9.0.retrieval.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "retrieved_or_failures_recorded": retrieved_or_failures_recorded,
        "rows": retrieval_rows,
        "failure_reasons": failure_reasons,
        "rma_excluded": True,
        "wave2_excluded": True,
        "token_value_absent_from_artifact": True,
    }

    out_path = resolve_project_path(project_root, outputs["retrieval_manifest"])
    log_path = resolve_project_path(project_root, outputs["retrieval_log"])
    write_safe_json(out_path, manifest)
    write_text(log_path, "".join(log_lines))

    print(f"[retrieve] retrieved_or_failures_recorded={retrieved_or_failures_recorded} -> {out_path}")
    # Return success if failures are recorded; downstream kernel build will decide usability.
    return 0 if retrieved_or_failures_recorded else 2


if __name__ == "__main__":
    raise SystemExit(main())
