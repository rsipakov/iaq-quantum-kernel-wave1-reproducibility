#!/usr/bin/env python3
"""
Step 9.9: hardware-vs-statevector distortion analysis.

This reports kernel-survival / hardware-distortion metrics only. It does not
train a hardware classifier and it does not make quantum-advantage claims.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from common import (
    centered_kernel_alignment,
    effective_rank_from_eigvals,
    ensure_output_dirs,
    kernel_target_alignment,
    load_paths,
    load_scope,
    nearest_psd_by_eigenclip,
    parser_with_project,
    read_json,
    read_matrix_csv,
    resolve_project_path,
    utc_now,
    write_csv_rows,
    write_safe_json,
    write_text,
)


def _pearson(x, y) -> float:
    import numpy as np
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    x = x[mask]
    y = y[mask]
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _rankdata(a):
    import numpy as np
    a = np.asarray(a, dtype=float)
    order = np.argsort(a)
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(len(a), dtype=float)
    # Average ranks for ties.
    unique, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
    for k, count in enumerate(counts):
        if count > 1:
            ranks[inv == k] = ranks[inv == k].mean()
    return ranks


def _spearman(x, y) -> float:
    import numpy as np
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    try:
        from scipy.stats import spearmanr
        return float(spearmanr(x[mask], y[mask]).correlation)
    except Exception:
        return _pearson(_rankdata(x[mask]), _rankdata(y[mask]))


def _offdiag_values(matrix):
    import numpy as np
    n = matrix.shape[0]
    mask = ~np.eye(n, dtype=bool)
    return matrix[mask]


def _upper_offdiag_pairs(a, b):
    import numpy as np
    n = a.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    return a[mask], b[mask]


def _load_labels(labels_path: Path, paths: Dict[str, Any], n: int) -> List[int]:
    import pandas as pd
    df = pd.read_csv(labels_path)
    col = None
    for c in paths.get("label_column_candidates", []):
        if c in df.columns:
            col = c
            break
    if col is None:
        # Fallback: first numeric column.
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                col = c
                break
    if col is None:
        raise ValueError(f"cannot infer label column from {labels_path}; columns={list(df.columns)}")
    labels = [int(v) for v in df[col].tolist()]
    if len(labels) != n:
        raise ValueError(f"label count mismatch: expected {n}, got {len(labels)}")
    return labels


def _save_figures(project_root: Path, paths: Dict[str, Any], regime: str, sv_off, hw_off, errors, eig_hw, eig_sv) -> List[str]:
    import matplotlib.pyplot as plt
    import numpy as np

    fig_paths: List[str] = []
    figures_dir = resolve_project_path(project_root, paths["outputs"]["figures_dir"])
    figures_dir.mkdir(parents=True, exist_ok=True)

    scatter_path = figures_dir / f"hardware_vs_statevector_{regime}_scatter.png"
    plt.figure()
    plt.scatter(sv_off, hw_off, s=12)
    plt.xlabel("Statevector off-diagonal kernel entry")
    plt.ylabel(f"Hardware {regime} off-diagonal kernel entry")
    plt.title(f"ZZ4 {regime}: hardware vs statevector")
    plt.tight_layout()
    plt.savefig(scatter_path, dpi=180)
    plt.close()
    fig_paths.append(str(scatter_path.relative_to(project_root)) if scatter_path.is_relative_to(project_root) else str(scatter_path))

    err_path = figures_dir / f"hardware_vs_statevector_{regime}_absolute_error_hist.png"
    plt.figure()
    plt.hist(np.abs(errors), bins=30)
    plt.xlabel("Absolute kernel error")
    plt.ylabel("Count")
    plt.title(f"ZZ4 {regime}: absolute kernel error")
    plt.tight_layout()
    plt.savefig(err_path, dpi=180)
    plt.close()
    fig_paths.append(str(err_path.relative_to(project_root)) if err_path.is_relative_to(project_root) else str(err_path))

    eig_path = figures_dir / f"hardware_vs_statevector_{regime}_eigenvalues.png"
    plt.figure()
    plt.plot(np.sort(eig_sv)[::-1], marker="o", label="statevector")
    plt.plot(np.sort(eig_hw)[::-1], marker="x", label=regime)
    plt.xlabel("Eigenvalue rank")
    plt.ylabel("Eigenvalue")
    plt.title(f"ZZ4 {regime}: eigenvalue spectrum")
    plt.legend()
    plt.tight_layout()
    plt.savefig(eig_path, dpi=180)
    plt.close()
    fig_paths.append(str(eig_path.relative_to(project_root)) if eig_path.is_relative_to(project_root) else str(eig_path))
    return fig_paths



def load_kernel_matrix(path: Path) -> np.ndarray:
    """Load a kernel matrix from .npy or CSV."""
    path = Path(path)
    if path.suffix.lower() == ".npy":
        return np.load(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, index_col=0).to_numpy()
    raise ValueError(f"Unsupported kernel file type: {path}")

def main() -> int:
    parser = parser_with_project("Step 9.9 analyze hardware-vs-statevector distortion.")
    parser.add_argument("--statevector-kernel", default=None, help="Override statevector ZZ4 kernel CSV path.")
    parser.add_argument("--labels-csv", default=None, help="Override labels CSV path.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    scope = load_scope(Path(args.scope_config))
    paths = load_paths(Path(args.paths_config))
    ensure_output_dirs(project_root, paths)
    outputs = paths["outputs"]

    import numpy as np

    n = int(scope["frozen_subset_n"])
    failure_reasons: List[str] = []
    metrics_rows: List[Dict[str, Any]] = []
    figures: Dict[str, List[str]] = {}

    sv_path = resolve_project_path(project_root, args.statevector_kernel or paths["input_artifacts"]["statevector_kernel"])
    labels_path = resolve_project_path(project_root, args.labels_csv or paths["input_artifacts"]["frozen_subset_labels"])

    try:
        K_sv = read_matrix_csv(sv_path)
        if K_sv.shape != (n, n):
            raise ValueError(f"statevector kernel shape mismatch: expected {(n, n)}, got {K_sv.shape}")
    except Exception as exc:
        failure_reasons.append(f"cannot load statevector kernel: {type(exc).__name__}: {exc}")
        K_sv = None

    try:
        labels = _load_labels(labels_path, paths, n)
    except Exception as exc:
        failure_reasons.append(f"cannot load labels: {type(exc).__name__}: {exc}")
        labels = None

    if K_sv is not None:
        K_sv_psd, sv_psd_diag = nearest_psd_by_eigenclip(K_sv)
        eig_sv = np.linalg.eigvalsh(0.5 * (K_sv + K_sv.T))
        kta_sv = kernel_target_alignment(K_sv, labels) if labels is not None else float("nan")
        cka_sv = centered_kernel_alignment(K_sv, labels) if labels is not None else float("nan")
        off_sv_all = _offdiag_values(K_sv)
        eff_rank_sv = effective_rank_from_eigvals(eig_sv)
    else:
        eig_sv = None
        kta_sv = cka_sv = eff_rank_sv = float("nan")

    if K_sv is not None:
        for regime in scope["allowed_wave1_regimes"]:
            k_path = resolve_project_path(project_root, f"step6b_hardware_subset_package/outputs/hardware_kernels/zz4_{regime}_kernel.csv")
            try:
                K_hw = read_matrix_csv(k_path)
                if K_hw.shape != (n, n):
                    raise ValueError(f"hardware kernel shape mismatch: expected {(n, n)}, got {K_hw.shape}")
                finite_mask = np.isfinite(K_hw) & np.isfinite(K_sv)
                if not finite_mask.all():
                    # Leave missing entries visible but use finite overlap for pairwise metrics.
                    pass

                hw_for_metrics = np.where(np.isfinite(K_hw), K_hw, np.nan)
                sv_upper, hw_upper = _upper_offdiag_pairs(K_sv, hw_for_metrics)
                mask = np.isfinite(sv_upper) & np.isfinite(hw_upper)
                sv_off = sv_upper[mask]
                hw_off = hw_upper[mask]
                errors = hw_off - sv_off

                K_hw_filled = np.nan_to_num(K_hw, nan=0.0)
                K_hw_psd, hw_psd_diag = nearest_psd_by_eigenclip(K_hw_filled)
                eig_hw = np.linalg.eigvalsh(0.5 * (K_hw_filled + K_hw_filled.T))

                kta_hw = kernel_target_alignment(K_hw_filled, labels) if labels is not None else float("nan")
                cka_hw = centered_kernel_alignment(K_hw_filled, labels) if labels is not None else float("nan")

                row = {
                    "regime_id": regime,
                    "offdiag_pair_count_used": int(mask.sum()),
                    "off_diagonal_spearman_correlation": _spearman(sv_off, hw_off),
                    "pearson_correlation": _pearson(sv_off, hw_off),
                    "median_absolute_kernel_error": float(np.median(np.abs(errors))) if len(errors) else float("nan"),
                    "kernel_MAE": float(np.mean(np.abs(errors))) if len(errors) else float("nan"),
                    "kernel_RMSE": float(np.sqrt(np.mean(errors ** 2))) if len(errors) else float("nan"),
                    "max_absolute_error": float(np.max(np.abs(errors))) if len(errors) else float("nan"),
                    "PSD_correction_Frobenius_norm": hw_psd_diag["psd_correction_frobenius_norm"],
                    "PSD_correction_Frobenius_relative": hw_psd_diag["psd_correction_frobenius_relative"],
                    "KTA_hardware": kta_hw,
                    "KTA_statevector": kta_sv,
                    "KTA_drop_relative_to_statevector": float((kta_sv - kta_hw) / abs(kta_sv)) if np.isfinite(kta_sv) and abs(kta_sv) > 0 else float("nan"),
                    "CKA_hardware": cka_hw,
                    "CKA_statevector": cka_sv,
                    "CKA_drop_relative_to_statevector": float((cka_sv - cka_hw) / abs(cka_sv)) if np.isfinite(cka_sv) and abs(cka_sv) > 0 else float("nan"),
                    "off_diagonal_variance_hardware": float(np.nanvar(_offdiag_values(K_hw_filled))),
                    "off_diagonal_variance_statevector": float(np.nanvar(off_sv_all)),
                    "off_diagonal_variance_change": float(np.nanvar(_offdiag_values(K_hw_filled)) - np.nanvar(off_sv_all)),
                    "effective_rank_hardware": effective_rank_from_eigvals(eig_hw),
                    "effective_rank_statevector": eff_rank_sv,
                    "effective_rank_change": float(effective_rank_from_eigvals(eig_hw) - eff_rank_sv) if np.isfinite(eff_rank_sv) else float("nan"),
                    "minimum_eigenvalue_before_PSD_correction_hardware": hw_psd_diag["min_eigenvalue_before_psd"],
                    "minimum_eigenvalue_after_PSD_correction_hardware": hw_psd_diag["min_eigenvalue_after_psd"],
                    "minimum_eigenvalue_before_PSD_correction_statevector": sv_psd_diag["min_eigenvalue_before_psd"],
                    "minimum_eigenvalue_after_PSD_correction_statevector": sv_psd_diag["min_eigenvalue_after_psd"],
                    "finite_entry_count_hardware": int(np.isfinite(K_hw).sum()),
                    "missing_entry_count_hardware": int(np.isnan(K_hw).sum()),
                }
                metrics_rows.append(row)
                figures[regime] = _save_figures(project_root, paths, regime, sv_off, hw_off, errors, eig_hw, eig_sv)
            except Exception as exc:
                failure_reasons.append(f"{regime}: cannot compute distortion metrics: {type(exc).__name__}: {exc}")

    metrics_path = resolve_project_path(project_root, outputs["distortion_metrics"])
    if metrics_rows:
        write_csv_rows(metrics_path, metrics_rows)

    all_regimes_reported = len(metrics_rows) == len(scope["allowed_wave1_regimes"])
    summary = {
        "artifact_type": "zz4_wave1_distortion_summary",
        "schema_version": "v9.0.distortion.1",
        "created_utc": utc_now(),
        "operator_identifier": args.operator,
        "distortion_metrics_computed_and_interpreted_conservatively": all_regimes_reported and not failure_reasons,
        "all_required_regimes_reported": all_regimes_reported,
        "failure_reasons": failure_reasons,
        "metrics_csv": outputs["distortion_metrics"],
        "figures": figures,
        "interpretation_scope": scope["claims_policy"]["allowed_interpretation"],
        "quantum_advantage_claim_allowed": False,
        "hardware_classifier_superiority_claim_allowed": False,
        "rma_hardware_readiness_claim_allowed": False,
        "rma_excluded": True,
        "wave2_excluded": True,
        "token_value_absent_from_artifact": True,
        "metrics_preview": metrics_rows,
    }

    json_path = resolve_project_path(project_root, outputs["distortion_summary_json"])
    md_path = resolve_project_path(project_root, outputs["distortion_summary_md"])
    write_safe_json(json_path, summary)

    lines = [
        "# ZZ4 Wave 1 hardware-vs-statevector distortion summary\n\n",
        f"- created_utc: {summary['created_utc']}\n",
        f"- scope: {summary['interpretation_scope']}\n",
        "- claims: no quantum advantage; no hardware classifier superiority; no RMA hardware-readiness claim\n\n",
        "## Metrics\n\n",
    ]
    if metrics_rows:
        cols = [
            "regime_id",
            "off_diagonal_spearman_correlation",
            "pearson_correlation",
            "median_absolute_kernel_error",
            "kernel_MAE",
            "kernel_RMSE",
            "KTA_hardware",
            "KTA_statevector",
            "CKA_hardware",
            "CKA_statevector",
            "effective_rank_hardware",
            "minimum_eigenvalue_before_PSD_correction_hardware",
        ]
        lines.append("| " + " | ".join(cols) + " |\n")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |\n")
        for row in metrics_rows:
            lines.append("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |\n")
    if failure_reasons:
        lines.append("\n## Failures / limitations\n\n")
        for reason in failure_reasons:
            lines.append(f"- {reason}\n")
    write_text(md_path, "".join(lines))

    print(f"[analysis] all_required_regimes_reported={all_regimes_reported} -> {json_path}")
    if failure_reasons:
        for reason in failure_reasons:
            print(f"  - {reason}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
