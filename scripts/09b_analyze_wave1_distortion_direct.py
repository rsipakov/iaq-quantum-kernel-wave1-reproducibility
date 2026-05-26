#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def offdiag_values(K: np.ndarray) -> np.ndarray:
    mask = ~np.eye(K.shape[0], dtype=bool)
    return K[mask]


def center_kernel(K: np.ndarray) -> np.ndarray:
    n = K.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    return H @ K @ H


def centered_kernel_alignment(K: np.ndarray, y: np.ndarray) -> float:
    y = np.asarray(y).astype(float)
    y = np.where(y > 0, 1.0, -1.0)
    Y = np.outer(y, y)
    Kc = center_kernel(K)
    Yc = center_kernel(Y)
    denom = np.linalg.norm(Kc, "fro") * np.linalg.norm(Yc, "fro")
    return float(np.sum(Kc * Yc) / denom) if denom > 0 else float("nan")


def cka(K: np.ndarray, K_ref: np.ndarray) -> float:
    A = center_kernel(K)
    B = center_kernel(K_ref)
    denom = np.linalg.norm(A, "fro") * np.linalg.norm(B, "fro")
    return float(np.sum(A * B) / denom) if denom > 0 else float("nan")


def psd_correction_diagnostics(K: np.ndarray) -> dict:
    S = (K + K.T) / 2.0
    eigvals, eigvecs = np.linalg.eigh(S)
    eigvals_clipped = np.clip(eigvals, 0, None)
    K_psd = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
    fro = float(np.linalg.norm(K_psd - S, "fro"))
    rel = float(fro / max(np.linalg.norm(S, "fro"), 1e-12))
    return {
        "min_eigenvalue_before_psd": float(np.min(eigvals)),
        "min_eigenvalue_after_psd": float(np.min(np.linalg.eigvalsh((K_psd + K_psd.T) / 2.0))),
        "psd_correction_frobenius": fro,
        "psd_correction_frobenius_relative": rel,
    }


def effective_rank(K: np.ndarray) -> float:
    S = (K + K.T) / 2.0
    eigvals = np.linalg.eigvalsh(S)
    eigvals = np.clip(eigvals, 0, None)
    total = float(np.sum(eigvals))
    if total <= 0:
        return float("nan")
    p = eigvals / total
    p = p[p > 0]
    entropy = -float(np.sum(p * np.log(p)))
    return float(np.exp(entropy))


def pearson_statistic(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 2:
        return float("nan")
    x = x[mask]
    y = y[mask]
    if float(np.std(x)) == 0.0 or float(np.std(y)) == 0.0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def spearman_statistic(x: np.ndarray, y: np.ndarray) -> float:
    x_rank = pd.Series(np.asarray(x, dtype=float)).rank(method="average").to_numpy()
    y_rank = pd.Series(np.asarray(y, dtype=float)).rank(method="average").to_numpy()
    return pearson_statistic(x_rank, y_rank)


def regime_metrics(regime: str, K_hw: np.ndarray, K_sv: np.ndarray, y: np.ndarray) -> dict:
    hw_off = offdiag_values(K_hw)
    sv_off = offdiag_values(K_sv)
    diff = hw_off - sv_off

    sp = spearman_statistic(sv_off, hw_off)
    pr = pearson_statistic(sv_off, hw_off)

    psd = psd_correction_diagnostics(K_hw)

    kta_hw = centered_kernel_alignment(K_hw, y)
    kta_sv = centered_kernel_alignment(K_sv, y)

    cka_hw_sv = cka(K_hw, K_sv)
    cka_sv_sv = cka(K_sv, K_sv)

    return {
        "regime_id": regime,
        "n": int(K_hw.shape[0]),
        "shots_submitted_per_circuit": 1024,

        "offdiag_spearman_vs_statevector": sp,
        "offdiag_spearman_pvalue": float("nan"),
        "offdiag_pearson_vs_statevector": pr,
        "offdiag_pearson_pvalue": float("nan"),

        "kernel_mae": float(np.mean(np.abs(diff))),
        "kernel_rmse": float(np.sqrt(np.mean(diff ** 2))),
        "median_absolute_kernel_error": float(np.median(np.abs(diff))),
        "max_absolute_kernel_error": float(np.max(np.abs(diff))),

        "hardware_offdiag_variance": float(np.var(hw_off)),
        "statevector_offdiag_variance": float(np.var(sv_off)),
        "offdiag_variance_change": float(np.var(hw_off) - np.var(sv_off)),

        "effective_rank_hardware": effective_rank(K_hw),
        "effective_rank_statevector": effective_rank(K_sv),
        "effective_rank_change": effective_rank(K_hw) - effective_rank(K_sv),

        "KTA_hardware": kta_hw,
        "KTA_statevector": kta_sv,
        "KTA_drop_relative_to_statevector": float(kta_sv - kta_hw),

        "CKA_hardware_vs_statevector": cka_hw_sv,
        "CKA_statevector_self": cka_sv_sv,
        "CKA_drop_relative_to_statevector": float(cka_sv_sv - cka_hw_sv),

        **psd,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()

    K_sv_path = root / "statevector_reference/zz4_K_all_all.npy"
    labels_path = root / "frozen_subset/hardware_subset_event_onset_next_1h.csv"
    kernels_dir = root / "hardware_kernels"
    analysis_dir = root / "hardware_analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    K_sv = np.load(K_sv_path)
    labels = pd.read_csv(labels_path)

    if "y_event_onset_next_1h" not in labels.columns:
        raise ValueError(
            "Expected column 'y_event_onset_next_1h' in frozen subset file: "
            f"{labels_path}"
        )

    if "hardware_row_order" in labels.columns:
        labels = labels.sort_values("hardware_row_order").reset_index(drop=True)

    y = labels["y_event_onset_next_1h"].to_numpy(dtype=int)

    if K_sv.shape != (24, 24):
        raise SystemExit(f"Unexpected statevector shape: {K_sv.shape}")
    if len(y) != 24:
        raise SystemExit(f"Unexpected labels length: {len(y)}")

    rows = []
    failure_reasons = []

    for regime in ["H0", "H1", "H2"]:
        p = kernels_dir / f"zz4_{regime}_kernel.npy"
        if not p.exists():
            failure_reasons.append(f"missing hardware kernel: {p}")
            continue

        K_hw = np.load(p)
        if K_hw.shape != (24, 24):
            failure_reasons.append(f"{regime} wrong shape: {K_hw.shape}")
            continue
        if not np.isfinite(K_hw).all():
            failure_reasons.append(f"{regime} contains non-finite values")
            continue

        rows.append(regime_metrics(regime, K_hw, K_sv, y))

    metrics = pd.DataFrame(rows)
    metrics_path = analysis_dir / "zz4_wave1_distortion_metrics.csv"
    summary_json_path = analysis_dir / "zz4_wave1_distortion_summary.json"
    summary_md_path = analysis_dir / "zz4_wave1_distortion_summary.md"

    metrics.to_csv(metrics_path, index=False)

    all_required = set(metrics["regime_id"]) == {"H0", "H1", "H2"} if not metrics.empty else False

    summary = {
        "artifact_type": "zz4_wave1_distortion_summary",
        "created_utc": utc_now(),
        "analysis_mode": "direct_npy_loader_budget_safe_1024_shots",
        "all_required_regimes_reported": bool(all_required),
        "regimes_reported": metrics["regime_id"].tolist() if not metrics.empty else [],
        "statevector_kernel_path": str(K_sv_path.relative_to(root)),
        "labels_path": str(labels_path.relative_to(root)),
        "metrics_path": str(metrics_path.relative_to(root)),
        "failure_reasons": failure_reasons,
        "interpretation_policy": [
            "Kernel-survival / hardware-distortion analysis only.",
            "No quantum advantage claim.",
            "No hardware classifier superiority claim.",
            "RMA hardware remains DEFER.",
            "Budget-safe Wave 1 used 1024 shots per circuit, not the originally planned 4096."
        ],
    }

    summary_json_path.write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# ZZ4 Wave 1 Hardware Distortion Summary",
        "",
        f"- Created UTC: {summary['created_utc']}",
        "- Mode: budget-safe H0/H1/H2, 1024 shots per circuit",
        f"- All required regimes reported: `{summary['all_required_regimes_reported']}`",
        f"- Regimes reported: `{', '.join(summary['regimes_reported'])}`",
        "",
        "## Key metrics",
        "",
    ]

    if not metrics.empty:
        cols = [
            "regime_id",
            "offdiag_spearman_vs_statevector",
            "offdiag_pearson_vs_statevector",
            "kernel_mae",
            "kernel_rmse",
            "KTA_hardware",
            "KTA_statevector",
            "CKA_hardware_vs_statevector",
            "effective_rank_hardware",
            "min_eigenvalue_before_psd",
            "psd_correction_frobenius_relative",
        ]
        lines.append(metrics[cols].to_markdown(index=False))
        lines.append("")

    if failure_reasons:
        lines.append("## Failure reasons")
        for r in failure_reasons:
            lines.append(f"- {r}")
        lines.append("")

    lines.extend([
        "## Interpretation discipline",
        "",
        "These results support only a hardware kernel-survival / distortion discussion.",
        "They do not support a quantum advantage claim, a hardware classifier-superiority claim, or any RMA hardware-readiness claim.",
        "",
    ])

    summary_md_path.write_text("\n".join(lines))

    print(f"[analysis-direct] all_required_regimes_reported={all_required} -> {summary_json_path}")
    print(f"[analysis-direct] metrics -> {metrics_path}")
    print(f"[analysis-direct] summary -> {summary_md_path}")

    if failure_reasons:
        for r in failure_reasons:
            print("  -", r)
        return 2
    return 0 if all_required else 2


if __name__ == "__main__":
    raise SystemExit(main())
