#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr


REGIMES = ["H0", "H1", "H2"]
ALIAS = {"H0": "M0", "H1": "M1", "H2": "M2"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def offdiag_values(K: np.ndarray) -> np.ndarray:
    mask = ~np.eye(K.shape[0], dtype=bool)
    return K[mask]


def unique_offdiag_values(K: np.ndarray) -> np.ndarray:
    idx = np.triu_indices(K.shape[0], k=1)
    return K[idx]


def center_kernel(K: np.ndarray) -> np.ndarray:
    n = K.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    return H @ K @ H


def cka(K: np.ndarray, K_ref: np.ndarray) -> float:
    A = center_kernel(K)
    B = center_kernel(K_ref)
    denom = np.linalg.norm(A, "fro") * np.linalg.norm(B, "fro")
    return float(np.sum(A * B) / denom) if denom > 0 else float("nan")


def centered_kernel_target_alignment(K: np.ndarray, y: np.ndarray) -> float:
    y = np.asarray(y).astype(float)
    y = np.where(y > 0, 1.0, -1.0)
    Y = np.outer(y, y)
    return cka(K, Y)


def effective_rank(K: np.ndarray) -> float:
    S = (K + K.T) / 2.0
    eigvals = np.linalg.eigvalsh(S)
    eigvals = np.clip(eigvals, 0, None)
    total = float(np.sum(eigvals))
    if total <= 0:
        return float("nan")
    p = eigvals / total
    p = p[p > 0]
    return float(np.exp(-np.sum(p * np.log(p))))


def scalar_metrics(K_hw: np.ndarray, K_sv: np.ndarray) -> dict:
    hw = offdiag_values(K_hw)
    sv = offdiag_values(K_sv)
    diff = hw - sv
    return {
        "spearman": float(spearmanr(sv, hw, nan_policy="omit").statistic),
        "pearson": float(pearsonr(sv, hw).statistic),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff ** 2))),
        "medae": float(np.median(np.abs(diff))),
        "maxae": float(np.max(np.abs(diff))),
        "offdiag_variance": float(np.var(hw)),
    }


def matrix_metrics(K_hw: np.ndarray, K_sv: np.ndarray, y: np.ndarray) -> dict:
    return {
        "cka": cka(K_hw, K_sv),
        "effective_rank": effective_rank(K_hw),
        "kta_centered": centered_kernel_target_alignment(K_hw, y),
    }


def all_metrics(K_hw: np.ndarray, K_sv: np.ndarray, y: np.ndarray) -> dict:
    out = scalar_metrics(K_hw, K_sv)
    out.update(matrix_metrics(K_hw, K_sv, y))
    return out


def force_diagonal_to_one(K: np.ndarray) -> np.ndarray:
    out = np.array(K, copy=True)
    np.fill_diagonal(out, 1.0)
    return out


def jackknife_se(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    n = len(values)
    mean = float(np.mean(values))
    return float(np.sqrt(((n - 1) / n) * np.sum((values - mean) ** 2)))


def jackknife_diagonal_policy(metric: str) -> str:
    # CKA and centered KTA are full-matrix metrics evaluated with the measured hardware diagonal;
    # spearman/pearson/mae are evaluated on the off-diagonal set only.
    if metric in {"cka", "kta_centered"}:
        return "measured_diagonal_full_matrix"
    return "offdiagonal_only"


def submatrix(K: np.ndarray, keep: np.ndarray) -> np.ndarray:
    return K[np.ix_(keep, keep)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    out_dir = root / "hardware_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    K_sv_path = root / "statevector_reference/zz4_K_all_all.npy"
    labels_path = root / "frozen_subset/hardware_subset_event_onset_next_1h.csv"
    kernels = {r: np.load(root / f"hardware_kernels/zz4_{r}_kernel.npy") for r in REGIMES}
    K_sv = np.load(K_sv_path)

    labels = pd.read_csv(labels_path)
    if "hardware_row_order" in labels.columns:
        labels = labels.sort_values("hardware_row_order").reset_index(drop=True)
    if "y_event_onset_next_1h" not in labels.columns:
        raise ValueError("Missing required label column: y_event_onset_next_1h")
    y = labels["y_event_onset_next_1h"].to_numpy(dtype=int)

    if K_sv.shape != (24, 24) or len(y) != 24:
        raise SystemExit(f"Unexpected shape/label length: K_sv={K_sv.shape}, len(y)={len(y)}")
    for r, K in kernels.items():
        if K.shape != (24, 24):
            raise SystemExit(f"Unexpected kernel shape for {r}: {K.shape}")

    rows = []

    # Statevector reference full-matrix diagnostics.
    rows.append({
        "analysis_block": "reference",
        "metric": "effective_rank",
        "configuration": "SV",
        "artifact_regime": "SV",
        "point_estimate": effective_rank(K_sv),
        "jackknife_se": np.nan,
        "diagonal_policy": "statevector_native",
        "contrast": "",
        "delta": np.nan,
        "jackknife_se_delta": np.nan,
        "z_descriptive": np.nan,
        "notes": "Statevector reference effective rank.",
    })
    rows.append({
        "analysis_block": "reference",
        "metric": "kta_centered",
        "configuration": "SV",
        "artifact_regime": "SV",
        "point_estimate": centered_kernel_target_alignment(K_sv, y),
        "jackknife_se": np.nan,
        "diagonal_policy": "statevector_native",
        "contrast": "",
        "delta": np.nan,
        "jackknife_se_delta": np.nan,
        "z_descriptive": np.nan,
        "notes": "Statevector reference centered kernel-target alignment.",
    })

    # Directed-vs-unique off-diagonal equivalence check.
    for r, K in kernels.items():
        directed_sv = offdiag_values(K_sv)
        directed_hw = offdiag_values(K)
        unique_sv = unique_offdiag_values(K_sv)
        unique_hw = unique_offdiag_values(K)

        directed = {
            "spearman": float(spearmanr(directed_sv, directed_hw, nan_policy="omit").statistic),
            "pearson": float(pearsonr(directed_sv, directed_hw).statistic),
            "mae": float(np.mean(np.abs(directed_hw - directed_sv))),
            "rmse": float(np.sqrt(np.mean((directed_hw - directed_sv) ** 2))),
            "medae": float(np.median(np.abs(directed_hw - directed_sv))),
            "maxae": float(np.max(np.abs(directed_hw - directed_sv))),
            "offdiag_variance": float(np.var(directed_hw)),
        }
        unique = {
            "spearman": float(spearmanr(unique_sv, unique_hw, nan_policy="omit").statistic),
            "pearson": float(pearsonr(unique_sv, unique_hw).statistic),
            "mae": float(np.mean(np.abs(unique_hw - unique_sv))),
            "rmse": float(np.sqrt(np.mean((unique_hw - unique_sv) ** 2))),
            "medae": float(np.median(np.abs(unique_hw - unique_sv))),
            "maxae": float(np.max(np.abs(unique_hw - unique_sv))),
            "offdiag_variance": float(np.var(unique_hw)),
        }

        for metric in directed:
            rows.append({
                "analysis_block": "directed_vs_unique_offdiag_check",
                "metric": metric,
                "configuration": ALIAS[r],
                "artifact_regime": r,
                "point_estimate": directed[metric],
                "jackknife_se": np.nan,
                "diagonal_policy": "offdiagonal_only",
                "contrast": "directed_minus_unique",
                "delta": directed[metric] - unique[metric],
                "jackknife_se_delta": np.nan,
                "z_descriptive": np.nan,
                "notes": "Machine-precision equivalence check for symmetric kernels.",
            })

    # Diagonal robustness.
    for r, K in kernels.items():
        native = matrix_metrics(K, K_sv, y)
        unit = matrix_metrics(force_diagonal_to_one(K), K_sv, y)

        for metric in ["cka", "effective_rank", "kta_centered"]:
            rows.append({
                "analysis_block": "diagonal_robustness",
                "metric": metric,
                "configuration": ALIAS[r],
                "artifact_regime": r,
                "point_estimate": unit[metric],
                "jackknife_se": np.nan,
                "diagonal_policy": "hardware_diagonal_forced_to_one",
                "contrast": "unit_diagonal_minus_measured_diagonal",
                "delta": unit[metric] - native[metric],
                "jackknife_se_delta": np.nan,
                "z_descriptive": np.nan,
                "notes": "Sensitivity only; reported kernels retain measured diagonal.",
            })

    # Leave-one-window-out jackknife for selected manuscript Table 4 metrics.
    jk_metrics = ["spearman", "pearson", "mae", "cka", "kta_centered"]
    jk_values = {r: {m: [] for m in jk_metrics} for r in REGIMES}

    n = K_sv.shape[0]
    for leave_out in range(n):
        keep = np.array([i for i in range(n) if i != leave_out], dtype=int)
        K_sv_sub = submatrix(K_sv, keep)
        y_sub = y[keep]
        for r, K in kernels.items():
            K_sub = submatrix(K, keep)
            metrics = all_metrics(K_sub, K_sv_sub, y_sub)
            for m in jk_metrics:
                jk_values[r][m].append(metrics[m])

    # Point estimates and jackknife SE.
    point_metrics = {r: all_metrics(K, K_sv, y) for r, K in kernels.items()}
    for r in REGIMES:
        for metric in jk_metrics:
            vals = np.asarray(jk_values[r][metric], dtype=float)
            rows.append({
                "analysis_block": "leave_one_window_out_jackknife",
                "metric": metric,
                "configuration": ALIAS[r],
                "artifact_regime": r,
                "point_estimate": point_metrics[r][metric],
                "jackknife_se": jackknife_se(vals),
                "diagonal_policy": jackknife_diagonal_policy(metric),
                "contrast": "",
                "delta": np.nan,
                "jackknife_se_delta": np.nan,
                "z_descriptive": np.nan,
                "notes": "Point estimate plus leave-one-window-out jackknife SE.",
            })

    # Paired contrasts.
    contrasts = [("M1-M0", "H1", "H0"), ("M2-M1", "H2", "H1"), ("M2-M0", "H2", "H0")]
    for label, r_hi, r_lo in contrasts:
        for metric in jk_metrics:
            point_delta = point_metrics[r_hi][metric] - point_metrics[r_lo][metric]
            jk_delta = np.asarray(jk_values[r_hi][metric]) - np.asarray(jk_values[r_lo][metric])
            se_delta = jackknife_se(jk_delta)
            z = point_delta / se_delta if se_delta > 0 else np.nan
            rows.append({
                "analysis_block": "paired_jackknife_contrast",
                "metric": metric,
                "configuration": "",
                "artifact_regime": "",
                "point_estimate": np.nan,
                "jackknife_se": np.nan,
                "diagonal_policy": jackknife_diagonal_policy(metric),
                "contrast": label,
                "delta": point_delta,
                "jackknife_se_delta": se_delta,
                "z_descriptive": z,
                "notes": "Descriptive paired jackknife contrast; not a significance test.",
            })

    df = pd.DataFrame(rows)
    csv_path = out_dir / "zz4_wave1_distortion_uncertainty.csv"
    json_path = out_dir / "zz4_wave1_distortion_uncertainty.json"

    df.to_csv(csv_path, index=False)

    summary = {
        "artifact_type": "zz4_wave1_distortion_uncertainty",
        "created_utc": utc_now(),
        "method": "leave_one_window_out_jackknife_and_diagonal_robustness",
        "resampling_unit": "frozen_subset_window",
        "n_windows": int(n),
        "regimes": REGIMES,
        "alias": ALIAS,
        "inputs": {
            "statevector_kernel": str(K_sv_path.relative_to(root)),
            "labels": str(labels_path.relative_to(root)),
            "hardware_kernels": [
                f"hardware_kernels/zz4_{r}_kernel.npy" for r in REGIMES
            ],
        },
        "outputs": {
            "csv": str(csv_path.relative_to(root)),
            "json": str(json_path.relative_to(root)),
        },
        "inferential_policy": (
            "Descriptive robustness and window-level resampling only; "
            "not a formal significance test and not a classifier-performance claim."
        ),
        "diagonal_policy": (
            "Reported kernels retain measured diagonal; unit-diagonal calculations are sensitivity checks only."
        ),
        "notes": [
            "Scalar off-diagonal metrics use directed i != j entries.",
            "Directed-vs-unique off-diagonal equivalence is checked for symmetric kernels.",
            "Paired contrasts include M1-M0, M2-M1, and M2-M0.",
            "Leave-one-window-out jackknife rows include spearman, pearson, mae, cka, and kta_centered."
        ],
    }

    json_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"[09c] wrote {csv_path}")
    print(f"[09c] wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
