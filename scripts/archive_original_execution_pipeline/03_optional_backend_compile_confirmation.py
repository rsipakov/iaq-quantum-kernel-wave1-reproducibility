#!/usr/bin/env python3
"""
Step 9.4: optional backend-specific compile confirmation.

This script transpiles the built QPY circuits against the live backend and checks
the v9 resource gate. It is optional but recommended before submission because
the Step 8.1 package did not yet archive live backend-specific metadata.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from common import (
    ensure_output_dirs,
    get_backend,
    load_paths,
    load_scope,
    load_service,
    parser_with_project,
    read_csv_rows,
    resolve_project_path,
    utc_now,
    write_csv_rows,
    write_safe_json,
)


def main() -> int:
    parser = parser_with_project("Optional backend-specific compile confirmation.")
    parser.add_argument("--backend", default=None, help="Override backend name. Must be allowed by scope.")
    parser.add_argument("--sample-limit", type=int, default=0, help="Transpile only first N circuits for a fast smoke test. 0 = all circuits.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)
    selected_backend = args.backend or scope["selected_backend"]

    failure_reasons: List[str] = []
    if selected_backend not in scope["allowed_backends"]:
        failure_reasons.append(f"backend not allowed by scope: {selected_backend}")

    qpy_path = resolve_project_path(project_root, paths["outputs"]["circuit_qpy"])
    index_path = resolve_project_path(project_root, paths["outputs"]["circuit_index"])

    rows: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}

    if not failure_reasons:
        try:
            import qiskit.qpy as qpy
            from qiskit.transpiler import generate_preset_pass_manager

            with qpy_path.open("rb") as f:
                circuits = list(qpy.load(f))
            index_rows = read_csv_rows(index_path)
            if args.sample_limit and args.sample_limit > 0:
                circuits = circuits[: args.sample_limit]
                index_rows = index_rows[: args.sample_limit]

            service = load_service()
            backend = get_backend(service, selected_backend)
            pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
            isa_circuits = pm.run(circuits)

            twoq_names = set(scope["resource_gate"]["two_qubit_gate_names"])
            max_depth = 0
            max_twoq = 0
            max_qubits = 0
            for idx, circ in enumerate(isa_circuits):
                ops = dict(circ.count_ops())
                twoq_count = sum(int(v) for k, v in ops.items() if k in twoq_names)
                depth = int(circ.depth() or 0)
                active_qubits = int(circ.num_qubits)
                max_depth = max(max_depth, depth)
                max_twoq = max(max_twoq, twoq_count)
                max_qubits = max(max_qubits, active_qubits)
                meta = getattr(circ, "metadata", None) or {}
                inv = index_rows[idx] if idx < len(index_rows) else {}
                rows.append({
                    "compile_order": idx,
                    "circuit_inventory_id": meta.get("circuit_inventory_id", inv.get("circuit_inventory_id", "")),
                    "pair_id": meta.get("pair_id", inv.get("pair_id", "")),
                    "regime": meta.get("regime", inv.get("regime", "")),
                    "depth": depth,
                    "two_qubit_count": twoq_count,
                    "num_qubits": active_qubits,
                    "ops": str(ops),
                })

            resource_gate_pass = (
                max_depth <= int(scope["resource_gate"]["max_depth"])
                and max_twoq <= int(scope["resource_gate"]["max_two_qubit_count"])
                and max_qubits >= int(scope["feature_dimension"])
            )
            if not resource_gate_pass:
                failure_reasons.append(
                    f"resource gate failed: max_depth={max_depth}, max_two_qubit_count={max_twoq}, max_qubits={max_qubits}"
                )
            summary = {
                "compiled_circuit_count": len(rows),
                "sample_limit": args.sample_limit,
                "max_depth": max_depth,
                "max_two_qubit_count": max_twoq,
                "max_num_qubits_in_compiled_circuit": max_qubits,
                "resource_gate_pass": resource_gate_pass,
            }
        except Exception as exc:
            failure_reasons.append(f"compile confirmation failed: {type(exc).__name__}: {exc}")

    csv_path = resolve_project_path(project_root, paths["outputs"]["backend_compile_csv"])
    if rows:
        write_csv_rows(csv_path, rows)

    artifact = {
        "artifact_type": "zz4_step9_backend_compile_confirmation",
        "schema_version": "v9.0.backend_compile.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "selected_backend": selected_backend,
        **summary,
        "resource_gate": scope["resource_gate"],
        "failure_reasons": failure_reasons,
        "rma_excluded": True,
        "wave2_excluded": True,
        "token_value_absent_from_artifact": True,
    }
    json_path = resolve_project_path(project_root, paths["outputs"]["backend_compile_json"])
    write_safe_json(json_path, artifact)

    print(f"[compile] resource_gate_pass={artifact.get('resource_gate_pass', False)} -> {json_path}")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
