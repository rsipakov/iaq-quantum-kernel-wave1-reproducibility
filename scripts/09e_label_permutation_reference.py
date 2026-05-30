#!/usr/bin/env python3
"""
09e_label_permutation_reference.py

Regenerable statevector ZZ4 label-permutation reference for Section 2.13.

Motivation
----------
The Wave 1 package historically carried a *static* source-derived table,
``hardware_analysis/qiskit_kta_cka_permutation_tests.csv``, copied from the
upstream non-public repository. That table persists a field named
``p_perm_two_sided``, but the stored value is numerically an *upper-tail*
exceedance probability ``P(T_null >= T_obs)``, not a symmetric two-sided
p-value, and no generating script or RNG seed was preserved. This script makes
the reference reproducible in-package: it recomputes the observed alignments
exactly, regenerates the permutation null with a *fixed* seed, and reports the
upper-tail probability alongside two explicit symmetric two-sided conventions,
plus a multi-seed Monte-Carlo sensitivity summary.

It does not modify the frozen subset, the labels, the kernels, the execution
configurations, or any claim boundary. It is a post-reconstruction diagnostic
reference only and is not a hardware-configuration selection test.

Outputs
-------
hardware_analysis/zz4_wave1_label_permutation_reference.csv
hardware_analysis/zz4_wave1_label_permutation_reference.json
hardware_analysis/zz4_wave1_label_permutation_reference_provenance.json

Usage
-----
python scripts/09e_label_permutation_reference.py --project-root .
python scripts/09e_label_permutation_reference.py --project-root . --check

The default invocation writes byte-stable CSV/JSON reference artifacts and a
local provenance JSON with the write timestamp. The ``--check`` invocation
builds the reference in memory and validates the static source copy without
rewriting persisted artifacts.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# Reference seed for the primary, manuscript-cited permutation null.
PRIMARY_SEED = 0
# Seeds used for the Monte-Carlo sensitivity envelope (inclusive of PRIMARY_SEED).
SENSITIVITY_SEEDS = list(range(16))
N_PERM = 5000
# The historical static upper-tail values fall inside the regenerated multi-seed
# envelope, so the check does not need extra tolerance beyond the envelope.
CHECK_ENVELOPE_SLACK = 0.0

ALIGNMENT_CONVENTIONS = {
    "CKA": "centered_label_alignment",
    "KTA": "uncentered_label_alignment",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def center_kernel(K: np.ndarray) -> np.ndarray:
    n = K.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    return H @ K @ H


def cka(K: np.ndarray, K_ref: np.ndarray) -> float:
    A = center_kernel(K)
    B = center_kernel(K_ref)
    denom = np.linalg.norm(A, "fro") * np.linalg.norm(B, "fro")
    return float(np.sum(A * B) / denom) if denom > 0 else float("nan")


def centered_alignment(K: np.ndarray, y_signed: np.ndarray) -> float:
    """Centered (Cortes-type) alignment KTA_c(K, y) = CKA(K, yy^T)."""
    Y = np.outer(y_signed, y_signed)
    return cka(K, Y)


def uncentered_alignment(K: np.ndarray, y_signed: np.ndarray) -> float:
    Y = np.outer(y_signed, y_signed)
    denom = np.linalg.norm(K, "fro") * np.linalg.norm(Y, "fro")
    return float(np.sum(K * Y) / denom) if denom > 0 else float("nan")


def permutation_null(K: np.ndarray, y_signed: np.ndarray, alignment_fn, seed: int, n_perm: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = len(y_signed)
    out = np.empty(n_perm, dtype=float)
    for b in range(n_perm):
        out[b] = alignment_fn(K, y_signed[rng.permutation(n)])
    return out


def upper_tail_p(null: np.ndarray, obs: float) -> float:
    """One-sided upper-tail exceedance probability P(T_null >= T_obs)."""
    return float(np.mean(null >= obs))


def upper_tail_p_addone(null: np.ndarray, obs: float) -> float:
    """Add-one (Davison-Hinkley) upper-tail p, guaranteeing p > 0."""
    b = len(null)
    return float((np.sum(null >= obs) + 1) / (b + 1))


def two_sided_centered_p(null: np.ndarray, obs: float) -> float:
    """Symmetric two-sided p by absolute deviation from the null mean."""
    m = float(np.mean(null))
    return float(np.mean(np.abs(null - m) >= abs(obs - m)))


def two_sided_2min_p(null: np.ndarray, obs: float) -> float:
    """Symmetric two-sided p as 2 * min(lower tail, upper tail), capped at 1."""
    lower = float(np.mean(null <= obs))
    upper = float(np.mean(null >= obs))
    return float(min(1.0, 2.0 * min(lower, upper)))


def summarize_null(null: np.ndarray, obs: float) -> dict:
    return {
        "observed": float(obs),
        "null_mean": float(np.mean(null)),
        "null_std": float(np.std(null, ddof=0)),
        "null_q95": float(np.percentile(null, 95)),
        "null_q99": float(np.percentile(null, 99)),
        "p_upper_tail": upper_tail_p(null, obs),
        "p_upper_tail_addone": upper_tail_p_addone(null, obs),
        "p_two_sided_centered": two_sided_centered_p(null, obs),
        "p_two_sided_2min": two_sided_2min_p(null, obs),
    }


def load_inputs(root: Path):
    K_sv = np.load(root / "statevector_reference/zz4_K_all_all.npy")
    labels = pd.read_csv(root / "frozen_subset/hardware_subset_event_onset_next_1h.csv")
    if "hardware_row_order" in labels.columns:
        labels = labels.sort_values("hardware_row_order").reset_index(drop=True)
    if "y_event_onset_next_1h" not in labels.columns:
        raise ValueError("Missing required label column: y_event_onset_next_1h")
    y = labels["y_event_onset_next_1h"].to_numpy(dtype=int)
    y_signed = np.where(y > 0, 1.0, -1.0)
    if K_sv.shape != (24, 24) or len(y_signed) != 24:
        raise SystemExit(f"Unexpected shape/label length: K_sv={K_sv.shape}, len(y)={len(y_signed)}")
    return K_sv, y_signed


def build_reference(root: Path) -> dict:
    K_sv, y_signed = load_inputs(root)
    n_pos = int((y_signed > 0).sum())
    n_neg = int((y_signed < 0).sum())

    metrics = {
        "CKA": centered_alignment,   # centered label alignment KTA_c(K_SV, y) = CKA(K_SV, yy^T)
        "KTA": uncentered_alignment,  # uncentered classical alignment
    }

    primary_rows = []
    sensitivity = {m: {"p_upper_tail": [], "p_two_sided_centered": []} for m in metrics}

    for metric_name, fn in metrics.items():
        obs = fn(K_sv, y_signed)
        # Primary, manuscript-cited null at the reference seed.
        null_primary = permutation_null(K_sv, y_signed, fn, PRIMARY_SEED, N_PERM)
        summary = summarize_null(null_primary, obs)
        summary.update({"kernel_name": "zz4", "metric": metric_name,
                        "alignment_convention": ALIGNMENT_CONVENTIONS[metric_name],
                        "n_rows": 24, "n_perm": N_PERM, "seed": PRIMARY_SEED})
        primary_rows.append(summary)

        # Multi-seed sensitivity envelope.
        for s in SENSITIVITY_SEEDS:
            null_s = permutation_null(K_sv, y_signed, fn, s, N_PERM)
            sensitivity[metric_name]["p_upper_tail"].append(upper_tail_p(null_s, obs))
            sensitivity[metric_name]["p_two_sided_centered"].append(two_sided_centered_p(null_s, obs))

    sens_summary = {}
    for m in metrics:
        for key in ("p_upper_tail", "p_two_sided_centered"):
            arr = np.asarray(sensitivity[m][key], dtype=float)
            sens_summary[f"{m}_{key}_mean"] = float(arr.mean())
            sens_summary[f"{m}_{key}_std"] = float(arr.std(ddof=0))
            sens_summary[f"{m}_{key}_min"] = float(arr.min())
            sens_summary[f"{m}_{key}_max"] = float(arr.max())

    return {
        "artifact_type": "zz4_wave1_label_permutation_reference",
        "description": (
            "Regenerable statevector ZZ4 label-permutation reference. The persisted "
            "source field p_perm_two_sided is an upper-tail exceedance probability; "
            "this artifact reports the upper-tail probability together with explicit "
            "symmetric two-sided conventions and a multi-seed sensitivity envelope."
        ),
        "inputs": {
            "statevector_kernel": "statevector_reference/zz4_K_all_all.npy",
            "labels": "frozen_subset/hardware_subset_event_onset_next_1h.csv",
        },
        "label_balance": {"positive": n_pos, "negative": n_neg},
        "primary_seed": PRIMARY_SEED,
        "sensitivity_seeds": SENSITIVITY_SEEDS,
        "n_perm": N_PERM,
        "primary_rows": primary_rows,
        "sensitivity_summary": sens_summary,
        "convention_note": (
            "p_upper_tail = P(T_null >= T_obs). p_two_sided_centered = "
            "P(|T_null - mean| >= |T_obs - mean|). p_two_sided_2min = "
            "2*min(lower, upper) capped at 1. The static source field "
            "p_perm_two_sided corresponds numerically to p_upper_tail. The "
            "source metric label CKA denotes the centered label-alignment row, "
            "equivalent to manuscript KTA_c(K_SV, y); the source metric label "
            "KTA denotes the companion uncentered alignment row retained for "
            "provenance."
        ),
        "inferential_policy": (
            "Statevector random-label reference only; not a hardware-configuration "
            "selection test and not a classifier-performance claim."
        ),
    }


def write_outputs(root: Path, ref: dict) -> tuple[Path, Path, Path]:
    out_dir = root / "hardware_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "zz4_wave1_label_permutation_reference.csv"
    json_path = out_dir / "zz4_wave1_label_permutation_reference.json"
    provenance_path = out_dir / "zz4_wave1_label_permutation_reference_provenance.json"

    df = pd.DataFrame(ref["primary_rows"])
    cols = ["kernel_name", "metric", "alignment_convention",
            "seed", "n_perm", "n_rows", "observed",
            "null_mean", "null_std", "null_q95", "null_q99",
            "p_upper_tail", "p_upper_tail_addone",
            "p_two_sided_centered", "p_two_sided_2min"]
    df = df[cols]
    df.to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(ref, indent=2) + "\n")
    provenance = {
        "artifact_type": "zz4_wave1_label_permutation_reference_provenance",
        "created_utc": utc_now(),
        "reference_csv": str(csv_path.relative_to(root)),
        "reference_json": str(json_path.relative_to(root)),
        "note": (
            "Local write-time provenance for the regenerable label-permutation "
            "reference. This file is intentionally excluded from the checksum "
            "manifest so the main CSV/JSON artifacts remain byte-stable across "
            "plain regeneration runs."
        ),
    }
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    return csv_path, json_path, provenance_path


def run_check(root: Path, ref: dict) -> int:
    static_path = root / "hardware_analysis/qiskit_kta_cka_permutation_tests.csv"
    if not static_path.exists():
        print(f"[09e][check] static reference not found: {static_path}")
        return 1
    static = pd.read_csv(static_path)
    ok = True

    for metric_name in ("CKA", "KTA"):
        static_row = static[(static["kernel_name"] == "zz4") & (static["metric"] == metric_name)].iloc[0]
        regen_row = next(r for r in ref["primary_rows"] if r["metric"] == metric_name)

        obs_ok = abs(regen_row["observed"] - float(static_row["observed"])) < 1e-9
        lo = ref["sensitivity_summary"][f"{metric_name}_p_upper_tail_min"] - CHECK_ENVELOPE_SLACK
        hi = ref["sensitivity_summary"][f"{metric_name}_p_upper_tail_max"] + CHECK_ENVELOPE_SLACK
        static_p = float(static_row["p_perm_two_sided"])
        p_in_envelope = lo <= static_p <= hi
        ok = ok and obs_ok and p_in_envelope

        print(f"[09e][check] {metric_name} observed alignment: "
              f"regen={regen_row['observed']:.10f} static={float(static_row['observed']):.10f} "
              f"match={obs_ok}")
        print(f"[09e][check] {metric_name} static p_perm_two_sided={static_p:.10f} "
              f"interpreted as upper-tail; multi-seed envelope=[{lo:.4f}, {hi:.4f}] "
              f"-> in_envelope={p_in_envelope}")

    print(f"[09e][check] regenerated symmetric two-sided (centered, primary seed): "
          f"{next(r['p_two_sided_centered'] for r in ref['primary_rows'] if r['metric'] == 'CKA'):.4f}")

    return 0 if ok else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--check", action="store_true",
                        help="Compare regenerated reference against the static source-derived copy.")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    ref = build_reference(root)
    if args.check:
        return run_check(root, ref)

    csv_path, json_path, provenance_path = write_outputs(root, ref)
    print(f"[09e] wrote {csv_path}")
    print(f"[09e] wrote {json_path}")
    print(f"[09e] wrote {provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
