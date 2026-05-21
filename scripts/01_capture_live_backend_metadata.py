#!/usr/bin/env python3
"""
Step 9.2: capture live backend/runtime metadata.

This script contacts IBM Quantum, captures backend/runtime metadata immediately
before submission, and writes no token values. It also includes the exact runtime
option hashes; if the runtime options artifact is absent, it creates it from the
package template to avoid an incomplete metadata lock.

Required environment:
- Either a saved QiskitRuntimeService account, or IBM_QUANTUM_TOKEN in the shell.
- Optional IBM_QUANTUM_INSTANCE to avoid account ambiguity.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from common import (
    backend_metadata_snapshot,
    default_runtime_options,
    ensure_output_dirs,
    get_backend,
    get_runtime_options_hashes,
    load_paths,
    load_scope,
    load_service,
    package_versions,
    parser_with_project,
    read_json,
    resolve_project_path,
    sha256_file,
    utc_now,
    validate_runtime_options_structure,
    write_safe_json,
    write_text,
)


def _load_or_create_runtime_options(project_root: Path, paths: Dict[str, Any], scope: Dict[str, Any], operator: str) -> Dict[str, Any]:
    out_path = resolve_project_path(project_root, paths["outputs"]["runtime_options"])
    if out_path.exists():
        return read_json(out_path)

    runtime_options = default_runtime_options()
    runtime_options["created_utc"] = utc_now()
    runtime_options["operator_identifier"] = operator
    runtime_options["selected_backend"] = scope["selected_backend"]
    runtime_options["pair_count_expected"] = scope["pair_count_expected"]
    runtime_options["circuit_count_expected"] = scope["circuit_count_expected"]
    runtime_options.update(get_runtime_options_hashes(runtime_options))
    runtime_options["options_explicit_and_hashed"] = True
    runtime_options["failure_reasons"] = []
    runtime_options["token_value_absent_from_artifact"] = True
    write_safe_json(out_path, runtime_options)
    write_text(resolve_project_path(project_root, paths["outputs"]["runtime_options_sha256"]), runtime_options["runtime_options_all_sha256"] + "\n")
    return runtime_options


def main() -> int:
    parser = parser_with_project("Step 9.2 capture live backend/runtime metadata.")
    parser.add_argument("--backend", default=None, help="Override backend name. Must still be in allowed_backends.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)

    selected_backend = args.backend or scope["selected_backend"]
    failure_reasons: List[str] = []
    if selected_backend not in scope["allowed_backends"]:
        failure_reasons.append(f"selected backend is not allowed by v9 scope: {selected_backend}")

    runtime_options = _load_or_create_runtime_options(project_root, paths, scope, args.operator)
    failure_reasons.extend(validate_runtime_options_structure(runtime_options, scope))
    option_hashes = get_runtime_options_hashes(runtime_options)

    backend_snapshot: Dict[str, Any] = {}
    primitive_name = runtime_options.get("primitive_name", "SamplerV2")
    primitive_version_or_class = None

    if not failure_reasons:
        try:
            service = load_service()
            backend = get_backend(service, selected_backend)
            backend_snapshot = backend_metadata_snapshot(backend)
            try:
                from qiskit_ibm_runtime import SamplerV2
                primitive_version_or_class = f"{SamplerV2.__module__}.{SamplerV2.__name__}"
            except Exception as exc:
                primitive_version_or_class = f"SamplerV2 import failed: {exc}"
        except Exception as exc:
            failure_reasons.append(f"backend metadata capture failed: {type(exc).__name__}: {exc}")

    backend_name = backend_snapshot.get("backend_name")
    if backend_name and backend_name != selected_backend:
        failure_reasons.append(f"backend name mismatch: selected={selected_backend}, live={backend_name}")

    backend_num_qubits = backend_snapshot.get("backend_num_qubits")
    if backend_num_qubits is not None and int(backend_num_qubits) < int(scope["feature_dimension"]):
        failure_reasons.append(f"backend has too few qubits: {backend_num_qubits}")

    token_value_absent = True
    metadata_gate_pass = not failure_reasons
    artifact = {
        "artifact_type": "zz_only_step9_live_backend_metadata",
        "schema_version": "v9.0.live_backend_metadata.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "selected_backend": selected_backend,
        **backend_snapshot,
        "queue_or_selection_rationale": "v9 package selected backend retained unless live metadata gate fails.",
        **package_versions(),
        "primitive_name": primitive_name,
        "primitive_version_or_class": primitive_version_or_class,
        "runtime_options_H0": runtime_options["regimes"].get("H0", {}).get("sampler_options"),
        "runtime_options_H1": runtime_options["regimes"].get("H1", {}).get("sampler_options"),
        "runtime_options_H2": runtime_options["regimes"].get("H2", {}).get("sampler_options"),
        "runtime_options_sha256_H0": option_hashes.get("runtime_options_sha256_H0"),
        "runtime_options_sha256_H1": option_hashes.get("runtime_options_sha256_H1"),
        "runtime_options_sha256_H2": option_hashes.get("runtime_options_sha256_H2"),
        "runtime_options_all_sha256": option_hashes.get("runtime_options_all_sha256"),
        "shots_planned_per_circuit": scope["shots_planned_per_circuit"],
        "pair_count_expected": scope["pair_count_expected"],
        "circuit_count_expected": scope["circuit_count_expected"],
        "execution_manifest_path": paths["input_artifacts"]["execution_manifest"],
        "execution_manifest_sha256": sha256_file(resolve_project_path(project_root, paths["input_artifacts"]["execution_manifest"])),
        "backend_selection_path": paths["input_artifacts"]["backend_selection"],
        "backend_selection_sha256": sha256_file(resolve_project_path(project_root, paths["input_artifacts"]["backend_selection"])),
        "token_value_absent_from_artifact": token_value_absent,
        "scope_drift_detected": bool(failure_reasons),
        "metadata_capture_status": "passed" if metadata_gate_pass else "failed",
        "metadata_gate_pass": metadata_gate_pass,
        "failure_reasons": failure_reasons,
    }

    out_path = resolve_project_path(project_root, paths["outputs"]["live_backend_metadata"])
    write_safe_json(out_path, artifact)

    # The v9 plan names zz_only_step8_live_backend_metadata.json. Keep a compatibility alias.
    alias_path = resolve_project_path(project_root, paths["outputs"]["legacy_live_backend_metadata_alias"])
    write_safe_json(alias_path, artifact)

    print(f"[step9.2] metadata_gate_pass={metadata_gate_pass} -> {out_path}")
    if not metadata_gate_pass:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
