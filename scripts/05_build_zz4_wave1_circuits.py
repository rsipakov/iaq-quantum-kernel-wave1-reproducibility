#!/usr/bin/env python3
"""
Step 9.2/9.5 support: build or validate ZZ4 Wave 1 fidelity circuits.

Inputs:
- frozen N=24 feature CSV;
- frozen pair inventory CSV with 300 rows;
- frozen circuit inventory CSV with 900 H0/H1/H2 rows.

Output:
- QPY file with one circuit per circuit-inventory row;
- circuit index CSV preserving pair/regime/circuit IDs;
- circuit build manifest.

The circuit is U_ZZ(x_i) followed by U_ZZ(x_j)^† with terminal all-qubit
measurement. The all-zero probability is later interpreted as the hardware
kernel entry for pair (i,j).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from common import (
    count_csv_rows,
    ensure_output_dirs,
    infer_column,
    load_paths,
    load_scope,
    pair_indices_from_inventory_rows,
    parser_with_project,
    read_csv_rows,
    resolve_project_path,
    utc_now,
    write_csv_rows,
    write_safe_json,
)


def _load_features(features_path: Path, feature_columns: Sequence[str]) -> "Any":
    import pandas as pd

    df = pd.read_csv(features_path)
    if not all(c in df.columns for c in feature_columns):
        # Fallback: use first four numeric columns if configured names do not match.
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if len(numeric_cols) < len(feature_columns):
            raise ValueError(
                f"Feature columns {feature_columns} not found and fewer than {len(feature_columns)} numeric columns exist. "
                f"Available columns={list(df.columns)}"
            )
        feature_columns = numeric_cols[: len(feature_columns)]
    return df, list(feature_columns)


def _build_zz_fidelity_circuit(x_i: Sequence[float], x_j: Sequence[float], feature_dim: int, reps: int, entanglement: str, name: str):
    from qiskit import QuantumCircuit

    try:
        from qiskit.circuit.library import ZZFeatureMap
        fm = ZZFeatureMap(feature_dimension=feature_dim, reps=reps, entanglement=entanglement)
    except Exception:
        # Conservative fallback: implements a simple ZZ-style feature map without relying on
        # a possibly renamed library class. This should only be used if Qiskit changes imports.
        from qiskit.circuit import ParameterVector
        import itertools
        x = ParameterVector("x", feature_dim)
        fm = QuantumCircuit(feature_dim, name="fallback_ZZFeatureMap")
        for _ in range(reps):
            for q in range(feature_dim):
                fm.h(q)
                fm.rz(x[q], q)
            pairs = [(q, q + 1) for q in range(feature_dim - 1)] if entanglement == "linear" else list(itertools.combinations(range(feature_dim), 2))
            for a, b in pairs:
                fm.cx(a, b)
                fm.rz((3.141592653589793 - x[a]) * (3.141592653589793 - x[b]), b)
                fm.cx(a, b)

    params = list(fm.parameters)
    left = fm.assign_parameters({p: float(v) for p, v in zip(params, x_i)}, inplace=False)
    right = fm.assign_parameters({p: float(v) for p, v in zip(params, x_j)}, inplace=False)

    qc = QuantumCircuit(feature_dim, name=name)
    qc.compose(left, inplace=True)
    qc.compose(right.inverse(), inplace=True)
    qc.measure_all()
    return qc


def _infer_circuit_columns(rows: List[Dict[str, str]], paths: Dict[str, Any]) -> Tuple[str, str, str]:
    candidates = paths.get("circuit_inventory_column_candidates", {})
    cols = rows[0].keys()
    circuit_id_col = infer_column(cols, candidates.get("circuit_id", []), "circuit id")
    pair_id_col = infer_column(cols, candidates.get("pair_id", []), "circuit pair id")
    regime_col = infer_column(cols, candidates.get("regime", []), "circuit regime")
    return circuit_id_col, pair_id_col, regime_col


def main() -> int:
    parser = parser_with_project("Build/validate ZZ4 Wave 1 circuits.")
    parser.add_argument("--features-csv", default=None, help="Override frozen subset feature CSV path.")
    parser.add_argument("--pair-inventory-csv", default=None, help="Override pair inventory CSV path.")
    parser.add_argument("--circuit-inventory-csv", default=None, help="Override circuit inventory CSV path.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)

    features_path = resolve_project_path(project_root, args.features_csv or paths["input_artifacts"]["frozen_subset_features"])
    pair_path = resolve_project_path(project_root, args.pair_inventory_csv or paths["input_artifacts"]["pair_inventory"])
    circuit_inventory_path = resolve_project_path(project_root, args.circuit_inventory_csv or paths["input_artifacts"]["circuit_inventory"])

    failure_reasons: List[str] = []
    circuit_index_rows: List[Dict[str, Any]] = []

    try:
        features_df, feature_columns = _load_features(features_path, paths["feature_columns"])
    except Exception as exc:
        feature_columns = paths["feature_columns"]
        features_df = None
        failure_reasons.append(f"cannot load frozen subset features: {type(exc).__name__}: {exc}")

    pair_rows = []
    circuit_rows = []
    try:
        pair_rows = read_csv_rows(pair_path)
        if len(pair_rows) != scope["pair_count_expected"]:
            failure_reasons.append(f"pair inventory row count mismatch: expected {scope['pair_count_expected']}, got {len(pair_rows)}")
    except Exception as exc:
        failure_reasons.append(f"cannot load pair inventory: {type(exc).__name__}: {exc}")

    try:
        circuit_rows = read_csv_rows(circuit_inventory_path)
        if len(circuit_rows) != scope["circuit_count_expected"]:
            failure_reasons.append(f"circuit inventory row count mismatch: expected {scope['circuit_count_expected']}, got {len(circuit_rows)}")
    except Exception as exc:
        failure_reasons.append(f"cannot load circuit inventory: {type(exc).__name__}: {exc}")

    if features_df is not None and len(features_df) != scope["frozen_subset_n"]:
        failure_reasons.append(f"frozen subset size mismatch: expected {scope['frozen_subset_n']}, got {len(features_df)}")

    if failure_reasons:
        manifest = {
            "artifact_type": "zz4_wave1_circuit_build_manifest",
            "schema_version": "v9.0.circuit_build.1",
            "created_utc": utc_now(),
            "operator_identifier": args.operator,
            "circuit_build_pass": False,
            "failure_reasons": failure_reasons,
            "token_value_absent_from_artifact": True,
        }
        out_path = resolve_project_path(project_root, paths["outputs"]["circuit_build_manifest"])
        write_safe_json(out_path, manifest)
        print(f"[build] circuit_build_pass=False -> {out_path}")
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2

    try:
        i_col, j_col, pair_id_col = pair_indices_from_inventory_rows(pair_rows, paths)
        circuit_id_col, circuit_pair_id_col, regime_col = _infer_circuit_columns(circuit_rows, paths)
    except Exception as exc:
        failure_reasons.append(f"cannot infer inventory columns: {type(exc).__name__}: {exc}")

    if not failure_reasons:
        pair_lookup: Dict[str, Dict[str, Any]] = {}
        from common import parse_intish
        for idx, row in enumerate(pair_rows):
            pair_id = str(row[pair_id_col]) if pair_id_col else str(idx)
            pair_lookup[pair_id] = {
                "pair_id": pair_id,
                "pair_inventory_row": idx,
                "i": parse_intish(row[i_col]),
                "j": parse_intish(row[j_col]),
            }

        regimes_observed = sorted(set(str(r[regime_col]) for r in circuit_rows))
        if regimes_observed != sorted(scope["allowed_wave1_regimes"]):
            failure_reasons.append(f"circuit inventory regimes mismatch: expected {sorted(scope['allowed_wave1_regimes'])}, got {regimes_observed}")

    circuits = []
    if not failure_reasons:
        import qiskit.qpy as qpy

        fmap = scope["feature_map"]
        for row_idx, row in enumerate(circuit_rows):
            circuit_id = str(row[circuit_id_col])
            pair_id = str(row[circuit_pair_id_col])
            regime = str(row[regime_col])
            pair = pair_lookup.get(pair_id)
            if pair is None:
                failure_reasons.append(f"circuit row {row_idx} references missing pair_id={pair_id}")
                continue
            i = pair["i"]
            j = pair["j"]
            if i < 0 or j < 0 or i >= len(features_df) or j >= len(features_df):
                failure_reasons.append(f"pair_id={pair_id} has out-of-range indices i={i}, j={j}")
                continue
            x_i = [float(features_df.iloc[i][c]) for c in feature_columns]
            x_j = [float(features_df.iloc[j][c]) for c in feature_columns]
            name = f"zz4_{regime}_pair_{pair_id}_circuit_{circuit_id}"[:100]
            qc = _build_zz_fidelity_circuit(
                x_i=x_i,
                x_j=x_j,
                feature_dim=int(fmap["feature_dimension"]),
                reps=int(fmap["reps"]),
                entanglement=str(fmap["entanglement"]),
                name=name,
            )
            qc.metadata = {
                "circuit_inventory_id": circuit_id,
                "pair_id": pair_id,
                "pair_inventory_row": pair["pair_inventory_row"],
                "i": i,
                "j": j,
                "regime": regime,
                "feature_columns": feature_columns,
                "fidelity_circuit_policy": fmap["fidelity_circuit"],
            }
            circuits.append(qc)
            circuit_index_rows.append({
                "circuit_order": len(circuits) - 1,
                "circuit_inventory_id": circuit_id,
                "pair_id": pair_id,
                "pair_inventory_row": pair["pair_inventory_row"],
                "i": i,
                "j": j,
                "regime": regime,
                "num_qubits": qc.num_qubits,
                "num_clbits": qc.num_clbits,
                "depth_logical": qc.depth(),
                "name": qc.name,
            })

        if len(circuits) != scope["circuit_count_expected"]:
            failure_reasons.append(f"built circuit count mismatch: expected {scope['circuit_count_expected']}, got {len(circuits)}")

    if not failure_reasons:
        qpy_path = resolve_project_path(project_root, paths["outputs"]["circuit_qpy"])
        qpy_path.parent.mkdir(parents=True, exist_ok=True)
        import qiskit.qpy as qpy
        with qpy_path.open("wb") as f:
            qpy.dump(circuits, f)

        index_path = resolve_project_path(project_root, paths["outputs"]["circuit_index"])
        write_csv_rows(index_path, circuit_index_rows)

    manifest = {
        "artifact_type": "zz4_wave1_circuit_build_manifest",
        "schema_version": "v9.0.circuit_build.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "circuit_build_pass": not failure_reasons,
        "failure_reasons": failure_reasons,
        "feature_source_path": str(features_path),
        "feature_columns": feature_columns,
        "pair_inventory_path": str(pair_path),
        "circuit_inventory_path": str(circuit_inventory_path),
        "qpy_output_path": paths["outputs"]["circuit_qpy"],
        "circuit_index_path": paths["outputs"]["circuit_index"],
        "built_circuit_count": len(circuit_index_rows),
        "pair_count_expected": scope["pair_count_expected"],
        "circuit_count_expected": scope["circuit_count_expected"],
        "regimes": scope["allowed_wave1_regimes"],
        "rma_excluded": True,
        "wave2_excluded": True,
        "all_zero_measurement_interpretation": scope["feature_map"]["all_zero_bitstring_policy"],
        "token_value_absent_from_artifact": True,
    }
    out_path = resolve_project_path(project_root, paths["outputs"]["circuit_build_manifest"])
    write_safe_json(out_path, manifest)

    print(f"[build] circuit_build_pass={not failure_reasons} -> {out_path}")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
