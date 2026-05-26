#!/usr/bin/env python3
"""
Step 9.8b: independent reconstruction audit for the Wave 1 ZZ4 hardware kernels.

This auditor does NOT re-submit jobs and does NOT alter any reconstruction
output. It verifies, against the curated reproducibility package, that the
positional PUB-to-coordinate mapping used by 08_build_hardware_kernels.py is
consistent with the coordinate identifiers redundantly preserved inside each
raw SamplerV2 result entry, and it records reconstruction quality-control
summaries (measured-diagonal statistics and a spectral reference value).

Outputs:
- hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv   (per-PUB rows)
- metadata/zz4_wave1_kernel_reconstruction_audit.json          (summary)
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REGIMES = ["H0", "H1", "H2"]
MANUSCRIPT_LABEL = {"H0": "M0", "H1": "M1", "H2": "M2"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(root: Path) -> int:
    circuit_index = list(csv.DictReader(open(root / "circuits/zz4_wave1_circuit_index.csv")))
    statevector = np.load(root / "statevector_reference/zz4_K_all_all.npy")
    sv_min_eig = float(np.linalg.eigvalsh(0.5 * (statevector + statevector.T)).min())

    audit_rows = []
    summary_regimes = []

    for regime in REGIMES:
        raw = json.load(open(root / f"hardware_results/zz4_{regime}_raw_results.json"))
        entries = raw["entries"]
        regime_index = [r for r in circuit_index if r["regime"] == regime]

        coord_matches = 0
        pair_matches = 0
        randomization_counts = set()
        for q, entry in enumerate(entries):
            idx_row = regime_index[q]
            md = entry["metadata"]
            cm = md["circuit_metadata"]
            ci_i, ci_j = int(idx_row["i"]), int(idx_row["j"])
            ci_pair = idx_row["pair_id"]
            md_i, md_j = int(cm["i"]), int(cm["j"])
            md_pair = cm["pair_id"]
            coord_ok = (ci_i == md_i) and (ci_j == md_j)
            pair_ok = ci_pair == md_pair
            coord_matches += int(coord_ok)
            pair_matches += int(pair_ok)
            # Realized twirling-randomization count, when recorded by the primitive.
            for source in (md, cm):
                for key in ("num_randomizations", "randomizations_realized",
                            "realized_randomizations", "randomizations"):
                    if key in source and source[key] is not None:
                        randomization_counts.add(int(source[key]))
            audit_rows.append({
                "regime_id": regime,
                "pub_order": q,
                "circuit_index_i": ci_i,
                "raw_metadata_i": md_i,
                "circuit_index_j": ci_j,
                "raw_metadata_j": md_j,
                "circuit_index_pair_id": ci_pair,
                "raw_metadata_pair_id": md_pair,
                "match": bool(coord_ok and pair_ok),
            })

        K = np.load(root / f"hardware_kernels/zz4_{regime}_kernel.npy")
        diag = np.diag(K)
        hw_min_eig = float(np.linalg.eigvalsh(0.5 * (K + K.T)).min())

        summary_regimes.append({
            "regime_id": regime,
            "manuscript_label": MANUSCRIPT_LABEL[regime],
            "n_pubs": len(entries),
            "coordinate_matches": coord_matches,
            "pair_id_matches": pair_matches,
            "all_consistent": bool(coord_matches == len(entries) == pair_matches),
            "measured_diagonal_mean": round(float(diag.mean()), 6),
            "measured_diagonal_min": round(float(diag.min()), 6),
            "measured_diagonal_max": round(float(diag.max()), 6),
            "hardware_min_eigenvalue": hw_min_eig,
            "num_randomizations_unique": sorted(randomization_counts),
        })

    all_consistent = all(r["all_consistent"] for r in summary_regimes)

    csv_path = root / "hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(audit_rows[0].keys()))
        writer.writeheader()
        writer.writerows(audit_rows)

    summary = {
        "artifact_type": "zz4_wave1_kernel_reconstruction_audit",
        "schema_version": "v9.0.kernel_reconstruction_audit.2",
        "created_utc": utc_now(),
        "purpose": "Independent verification of the positional PUB-to-coordinate mapping and reconstruction QC summaries; no kernel value is modified.",
        "coordinate_mapping_consistent": all_consistent,
        "total_configurations_checked": len(audit_rows),
        "per_pub_audit_csv": "hardware_kernels/zz4_wave1_kernel_reconstruction_audit.csv",
        "spectral_reference": {
            "statevector_min_eigenvalue": sv_min_eig,
            "note": "Comparative spectral interpretation is reported with the hardware-distortion results, not here.",
        },
        "regimes": summary_regimes,
    }
    json_path = root / "metadata/zz4_wave1_kernel_reconstruction_audit.json"
    json_path.write_text(json.dumps(summary, indent=2))

    print(f"[audit] coordinate_mapping_consistent={all_consistent} "
          f"checked={len(audit_rows)} -> {json_path.name}, {csv_path.name}")
    return 0 if all_consistent else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Audit Wave 1 ZZ4 kernel reconstruction from persisted artifacts."
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Reproducibility repository root. Defaults to this script's repository root.",
    )
    cli_args = parser.parse_args()
    root = Path(cli_args.project_root).resolve() if cli_args.project_root else Path(__file__).resolve().parents[1]
    raise SystemExit(main(root))
