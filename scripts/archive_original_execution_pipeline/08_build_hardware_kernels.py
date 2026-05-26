#!/usr/bin/env python3
"""
Step 9.8: build H0/H1/H2 hardware kernel matrices.

For each retrieved SamplerV2 PUB result:
- map result order back to circuit_index rows for the same regime;
- compute P(00..0) from counts;
- assign it to K[i,j];
- symmetrize by averaging duplicate/directed entries, then mirror;
- keep diagonal as measured by default;
- compute PSD diagnostics, but do not hide uncorrected kernels.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from common import (
    all_zero_key,
    ensure_output_dirs,
    load_paths,
    load_scope,
    nearest_psd_by_eigenclip,
    parser_with_project,
    probability_of_all_zero,
    read_csv_rows,
    read_json,
    resolve_project_path,
    utc_now,
    write_csv_rows,
    write_matrix_csv,
    write_safe_json,
)


def main() -> int:
    parser = parser_with_project("Step 9.8 build hardware kernel matrices.")
    parser.add_argument("--force-diagonal-one", action="store_true", help="Override measured diagonal with 1.0. Default is measured diagonal.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)
    outputs = paths["outputs"]

    import numpy as np

    circuit_index = read_csv_rows(resolve_project_path(project_root, outputs["circuit_index"]))
    n = int(scope["frozen_subset_n"])
    num_qubits = int(scope["feature_dimension"])
    all_entries: List[Dict[str, Any]] = []
    kernel_manifest_rows: List[Dict[str, Any]] = []
    failure_reasons: List[str] = []

    for regime in scope["allowed_wave1_regimes"]:
        regime_index = [row for row in circuit_index if row.get("regime") == regime]
        raw_path = resolve_project_path(project_root, f"step6b_hardware_subset_package/outputs/hardware_results/zz4_{regime}_raw_results.json")
        if not raw_path.exists():
            failure_reasons.append(f"{regime}: raw result file missing")
            continue

        raw = read_json(raw_path)
        entries = raw.get("entries", [])
        K_values: Dict[Tuple[int, int], List[float]] = {}
        entry_rows: List[Dict[str, Any]] = []

        if raw.get("retrieval_status") != "retrieved":
            failure_reasons.append(f"{regime}: raw result not retrieved: {raw.get('failure_reason')}")
        if len(entries) != len(regime_index):
            failure_reasons.append(f"{regime}: result count {len(entries)} does not match circuit index count {len(regime_index)}")

        for pub_order, result_entry in enumerate(entries):
            if pub_order >= len(regime_index):
                break
            idx_row = regime_index[pub_order]
            try:
                i = int(idx_row["i"])
                j = int(idx_row["j"])
            except Exception as exc:
                failure_reasons.append(f"{regime}: invalid i/j at pub_order={pub_order}: {exc}")
                continue
            counts = result_entry.get("counts", {}) or {}
            prob0, count0, shots_observed, key_used = probability_of_all_zero(
                counts, num_qubits=num_qubits, shots_hint=int(scope["shots_planned_per_circuit"])
            )
            K_values.setdefault((i, j), []).append(prob0)
            entry = {
                "regime_id": regime,
                "pub_order": pub_order,
                "circuit_inventory_id": idx_row.get("circuit_inventory_id"),
                "pair_id": idx_row.get("pair_id"),
                "i": i,
                "j": j,
                "all_zero_key": key_used,
                "all_zero_count": count0,
                "shots_observed": shots_observed,
                "kernel_value_raw": prob0,
            }
            entry_rows.append(entry)
            all_entries.append(entry)

        K = np.full((n, n), np.nan, dtype=float)
        for (i, j), vals in K_values.items():
            vals_clean = [v for v in vals if np.isfinite(v)]
            if vals_clean:
                value = float(np.mean(vals_clean))
                K[i, j] = value

        # Symmetrize: for each unordered pair, average observed K[i,j] and K[j,i] if both exist.
        for i in range(n):
            for j in range(i, n):
                vals = []
                if np.isfinite(K[i, j]):
                    vals.append(K[i, j])
                if i != j and np.isfinite(K[j, i]):
                    vals.append(K[j, i])
                if vals:
                    value = float(np.mean(vals))
                    K[i, j] = value
                    K[j, i] = value

        if args.force_diagonal_one:
            np.fill_diagonal(K, 1.0)
            diagonal_policy = "forced_one"
        else:
            diagonal_policy = scope["kernel_reconstruction"]["diagonal_policy"]

        missing_count = int(np.isnan(K).sum())
        finite_count = int(np.isfinite(K).sum())

        K_for_psd = np.nan_to_num(K, nan=0.0)
        psd, psd_diag = nearest_psd_by_eigenclip(K_for_psd)

        csv_path = resolve_project_path(project_root, f"step6b_hardware_subset_package/outputs/hardware_kernels/zz4_{regime}_kernel.csv")
        npy_path = resolve_project_path(project_root, f"step6b_hardware_subset_package/outputs/hardware_kernels/zz4_{regime}_kernel.npy")
        write_matrix_csv(csv_path, K)
        npy_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(npy_path, K)

        kernel_manifest_rows.append({
            "regime_id": regime,
            "kernel_csv": str(csv_path.relative_to(project_root)) if csv_path.is_relative_to(project_root) else str(csv_path),
            "kernel_npy": str(npy_path.relative_to(project_root)) if npy_path.is_relative_to(project_root) else str(npy_path),
            "shape_rows": n,
            "shape_cols": n,
            "finite_entry_count": finite_count,
            "missing_entry_count": missing_count,
            "diagonal_policy": diagonal_policy,
            "symmetrization_policy": scope["kernel_reconstruction"]["symmetrization_policy"],
            **psd_diag,
        })

    entries_path = resolve_project_path(project_root, outputs["kernel_entries_long"])
    if all_entries:
        write_csv_rows(entries_path, all_entries)

    all_three_kernels_present = len(kernel_manifest_rows) == len(scope["allowed_wave1_regimes"])
    matrices_shape_24x24 = all(r.get("shape_rows") == n and r.get("shape_cols") == n for r in kernel_manifest_rows)
    no_missing_entries = all(r.get("missing_entry_count") == 0 for r in kernel_manifest_rows)
    kernel_matrices_shape_24x24 = all_three_kernels_present and matrices_shape_24x24

    manifest = {
        "artifact_type": "zz4_wave1_kernel_manifest",
        "schema_version": "v9.0.kernel_manifest.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "kernel_matrices_shape_24x24": kernel_matrices_shape_24x24,
        "all_three_kernels_present": all_three_kernels_present,
        "no_missing_entries": no_missing_entries,
        "failure_reasons": failure_reasons,
        "rows": kernel_manifest_rows,
        "kernel_entries_long_path": outputs["kernel_entries_long"],
        "diagonal_policy": "forced_one" if args.force_diagonal_one else scope["kernel_reconstruction"]["diagonal_policy"],
        "psd_policy": scope["kernel_reconstruction"]["psd_policy"],
        "rma_excluded": True,
        "wave2_excluded": True,
        "token_value_absent_from_artifact": True,
    }

    out_path = resolve_project_path(project_root, outputs["kernel_manifest"])
    write_safe_json(out_path, manifest)

    print(f"[kernels] kernel_matrices_shape_24x24={kernel_matrices_shape_24x24} -> {out_path}")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"  - {reason}")
    # Missing/unretrieved results are allowed to be documented; analysis may fail later.
    return 0 if kernel_matrices_shape_24x24 else 2


if __name__ == "__main__":
    raise SystemExit(main())
