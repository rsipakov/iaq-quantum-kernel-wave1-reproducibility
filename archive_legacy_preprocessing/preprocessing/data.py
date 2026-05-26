"""Dataset loading, filtering, and train-only preprocessing.

The core safeguards live here:
- only approved onset targets are accepted;
- only approved compact feature sets are accepted;
- the target-valid mask is applied before modeling;
- imputer/scaler are fitted on train only;
- features are scaled to [0, pi] and clipped if validation/external values exceed
  the training range.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler

from .config import (
    ALLOWED_TARGETS,
    FEATURE_SETS,
    ROW_ID_CANDIDATES,
    SPLIT_COLUMN_CANDIDATES,
    SPLIT_ORDER,
    TIME_SPLIT_WINDOWS,
    VALID_LABEL_CANDIDATES,
    WINDOW_END_CANDIDATES,
)


@dataclass
class PreparedFeatureSet:
    feature_set: str
    original_features: List[str]
    used_features: List[str]
    dropped_all_null_train_features: List[str]
    split_col: str
    window_col: Optional[str]
    row_id_col: str
    target: str
    valid_label_col: Optional[str]
    X_scaled: Dict[str, np.ndarray]
    y: Dict[str, np.ndarray]
    index_frames: Dict[str, pd.DataFrame]
    imputer: SimpleImputer
    scaler: MinMaxScaler
    scaling_report: pd.DataFrame


def load_forecasting_dataset(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Forecasting dataset not found: {path}")
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported dataset extension for {path}; use .parquet or .csv")


def find_first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def find_split_column_or_create(df: pd.DataFrame, window_col: Optional[str]) -> Tuple[pd.DataFrame, str, bool]:
    split_col = find_first_existing_column(df, SPLIT_COLUMN_CANDIDATES)
    if split_col is not None:
        return df, split_col, False
    if window_col is None:
        raise ValueError(
            "No split column was found and no window_end/timestamp column is available "
            "to recreate the v5 time-aware split."
        )
    out = df.copy()
    time = pd.to_datetime(out[window_col], errors="coerce")
    out["split"] = pd.NA
    for split_name, (start, end) in TIME_SPLIT_WINDOWS.items():
        mask = (time >= pd.Timestamp(start)) & (time <= pd.Timestamp(end))
        out.loc[mask, "split"] = split_name
    return out, "split", True


def find_valid_label_column(df: pd.DataFrame, target: str) -> Optional[str]:
    for col in VALID_LABEL_CANDIDATES.get(target, []):
        if col in df.columns:
            return col
    return None


def validate_target_and_feature_set(target: str, feature_set: str) -> None:
    if target not in ALLOWED_TARGETS:
        raise ValueError(
            f"Target {target!r} is not allowed in v5 Qiskit stage. "
            f"Allowed targets: {ALLOWED_TARGETS}"
        )
    if feature_set not in FEATURE_SETS:
        raise ValueError(
            f"Feature set {feature_set!r} is not allowed in v5 Qiskit stage. "
            f"Allowed feature sets: {tuple(FEATURE_SETS)}"
        )


def select_valid_labeled_rows(df: pd.DataFrame, target: str) -> Tuple[pd.DataFrame, Optional[str], str, Optional[str], bool]:
    """Filter to rows usable for an onset target.

    Returns filtered dataframe plus metadata:
    valid_label_col, split_col, window_col, split_created_from_dates.
    """
    if target not in df.columns:
        raise ValueError(f"Target column {target!r} not found in dataset.")

    window_col = find_first_existing_column(df, WINDOW_END_CANDIDATES)
    row_df = df.copy()
    if window_col is not None:
        row_df[window_col] = pd.to_datetime(row_df[window_col], errors="coerce")

    row_df, split_col, split_created = find_split_column_or_create(row_df, window_col)
    valid_col = find_valid_label_column(row_df, target)

    # Target-valid filtering: use explicit valid label when present; otherwise
    # fall back to non-null binary target. The fallback is logged by caller.
    mask = row_df[target].notna()
    if valid_col is not None:
        valid_values = row_df[valid_col]
        if valid_values.dtype == bool:
            mask &= valid_values
        else:
            mask &= valid_values.fillna(0).astype(float).astype(int).eq(1)

    mask &= row_df[split_col].isin(SPLIT_ORDER)
    out = row_df.loc[mask].copy()

    # Normalize labels to integer 0/1.
    out[target] = out[target].astype(float).round().astype(int)
    bad = set(out[target].unique()) - {0, 1}
    if bad:
        raise ValueError(f"Target {target!r} contains non-binary values after filtering: {bad}")

    if window_col is not None:
        out = out.sort_values([split_col, window_col]).reset_index(drop=True)
    else:
        out = out.reset_index(drop=True)

    return out, valid_col, split_col, window_col, split_created


def make_row_id(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    row_id_col = find_first_existing_column(df, ROW_ID_CANDIDATES)
    if row_id_col is not None:
        return df, row_id_col
    out = df.copy()
    out["qiskit_stage_row_id"] = np.arange(len(out), dtype=int)
    return out, "qiskit_stage_row_id"


def cap_splits_for_quick_runs(
    df: pd.DataFrame,
    target: str,
    split_col: str,
    window_col: Optional[str],
    max_train: Optional[int] = None,
    max_validation: Optional[int] = None,
    max_external_test: Optional[int] = None,
    balanced: bool = False,
    seed: int = 42,
) -> pd.DataFrame:
    """Optionally cap rows inside each fixed time split.

    This is for smoke tests and statevector development only. Final results should
    run with all valid rows. When balanced=True, sampling is stratified by label
    inside each split, then re-sorted by time.
    """
    caps = {
        "train": max_train,
        "validation": max_validation,
        "external_test": max_external_test,
    }
    rng = np.random.default_rng(seed)
    pieces = []
    for split_name in SPLIT_ORDER:
        part = df[df[split_col] == split_name].copy()
        cap = caps.get(split_name)
        if cap is None or cap <= 0 or len(part) <= cap:
            pieces.append(part)
            continue
        if not balanced:
            chosen = rng.choice(part.index.to_numpy(), size=cap, replace=False)
            sub = part.loc[chosen].copy()
        else:
            # Split cap roughly evenly between classes. If a class has too few
            # samples, use all available and fill the remainder from the other class.
            chosen_idx: List[int] = []
            per_class = max(1, cap // 2)
            for cls in [0, 1]:
                idx = part.index[part[target] == cls].to_numpy()
                take = min(per_class, len(idx))
                if take > 0:
                    chosen_idx.extend(rng.choice(idx, size=take, replace=False).tolist())
            if len(chosen_idx) < cap:
                remaining = np.setdiff1d(part.index.to_numpy(), np.array(chosen_idx, dtype=int))
                fill = min(cap - len(chosen_idx), len(remaining))
                if fill > 0:
                    chosen_idx.extend(rng.choice(remaining, size=fill, replace=False).tolist())
            sub = part.loc[chosen_idx].copy()
        if window_col is not None:
            sub = sub.sort_values(window_col)
        pieces.append(sub)
    return pd.concat(pieces, axis=0).reset_index(drop=True)


def prepare_feature_set(
    df: pd.DataFrame,
    target: str,
    feature_set: str,
    allow_drop_all_null_train: bool = True,
) -> PreparedFeatureSet:
    validate_target_and_feature_set(target, feature_set)
    valid_df, valid_col, split_col, window_col, _split_created = select_valid_labeled_rows(df, target)
    valid_df, row_id_col = make_row_id(valid_df)

    required_features = FEATURE_SETS[feature_set]
    missing = [c for c in required_features if c not in valid_df.columns]
    if missing:
        raise ValueError(
            f"Dataset is missing required columns for {feature_set}: {missing}. "
            "Do not silently substitute features in this v5 stage."
        )

    train_mask = valid_df[split_col].eq("train")
    train = valid_df.loc[train_mask, required_features]

    dropped = [c for c in required_features if train[c].isna().all()]
    if dropped and not allow_drop_all_null_train:
        raise ValueError(f"All-null train features in {feature_set}: {dropped}")
    used_features = [c for c in required_features if c not in dropped]
    if not used_features:
        raise ValueError(f"No usable features remain for {feature_set} after dropping all-null train columns.")

    imputer = SimpleImputer(strategy="median")
    scaler = MinMaxScaler(feature_range=(0.0, float(np.pi)))

    X_train_imputed = imputer.fit_transform(valid_df.loc[train_mask, used_features])
    scaler.fit(X_train_imputed)

    X_scaled: Dict[str, np.ndarray] = {}
    y: Dict[str, np.ndarray] = {}
    index_frames: Dict[str, pd.DataFrame] = {}
    report_rows = []

    for split_name in SPLIT_ORDER:
        part = valid_df[valid_df[split_col].eq(split_name)].copy()
        X_imp = imputer.transform(part[used_features])
        X_raw_scaled = scaler.transform(X_imp)
        low_count = int((X_raw_scaled < 0.0).sum())
        high_count = int((X_raw_scaled > np.pi).sum())
        X_clip = np.clip(X_raw_scaled, 0.0, np.pi)
        X_scaled[split_name] = X_clip.astype(float)
        y[split_name] = part[target].to_numpy(dtype=int)

        cols = [row_id_col, split_col, target]
        if window_col is not None:
            cols.insert(1, window_col)
        index_frame = part[cols].copy()
        index_frame = index_frame.rename(columns={split_col: "split", target: "target_label"})
        index_frame["target_name"] = target
        index_frame["feature_set"] = feature_set
        index_frame["split_row_number"] = np.arange(len(index_frame), dtype=int)
        index_frames[split_name] = index_frame.reset_index(drop=True)

        report_rows.append(
            {
                "target": target,
                "feature_set": feature_set,
                "split": split_name,
                "n_rows": int(len(part)),
                "n_positive": int(part[target].sum()),
                "n_negative": int(len(part) - part[target].sum()),
                "positive_rate": float(part[target].mean()) if len(part) else np.nan,
                "n_features_original": len(required_features),
                "n_features_used": len(used_features),
                "dropped_all_null_train_features": ",".join(dropped),
                "scaled_values_clipped_low": low_count,
                "scaled_values_clipped_high": high_count,
            }
        )

    scaling_report = pd.DataFrame(report_rows)
    return PreparedFeatureSet(
        feature_set=feature_set,
        original_features=list(required_features),
        used_features=used_features,
        dropped_all_null_train_features=dropped,
        split_col=split_col,
        window_col=window_col,
        row_id_col=row_id_col,
        target=target,
        valid_label_col=valid_col,
        X_scaled=X_scaled,
        y=y,
        index_frames=index_frames,
        imputer=imputer,
        scaler=scaler,
        scaling_report=scaling_report,
    )


def save_scaled_feature_table(prep: PreparedFeatureSet, out_path: str | Path) -> None:
    """Save scaled rows with IDs, labels and split metadata.

    The kernel matrices reference row order in these tables. This makes later
    inspection, case-study plotting and hardware-subset sampling traceable.
    """
    frames = []
    for split_name in SPLIT_ORDER:
        idx = prep.index_frames[split_name].copy()
        X = prep.X_scaled[split_name]
        for j, feature in enumerate(prep.used_features):
            idx[f"scaled__{feature}"] = X[:, j]
        frames.append(idx)
    table = pd.concat(frames, axis=0).reset_index(drop=True)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".parquet":
        try:
            table.to_parquet(out_path, index=False)
        except ImportError:
            # Useful for lightweight smoke tests before installing pyarrow.
            table.to_csv(out_path.with_suffix(".csv"), index=False)
    else:
        table.to_csv(out_path, index=False)


def split_count_table(df: pd.DataFrame, target: str) -> pd.DataFrame:
    valid_df, valid_col, split_col, window_col, split_created = select_valid_labeled_rows(df, target)
    rows = []
    for split_name in SPLIT_ORDER:
        part = valid_df[valid_df[split_col].eq(split_name)]
        rows.append(
            {
                "target": target,
                "split": split_name,
                "n_valid": int(len(part)),
                "n_positive": int(part[target].sum()) if len(part) else 0,
                "n_negative": int(len(part) - part[target].sum()) if len(part) else 0,
                "positive_rate": float(part[target].mean()) if len(part) else np.nan,
                "valid_label_col": valid_col,
                "split_col": split_col,
                "window_col": window_col,
                "split_created_from_v5_dates": bool(split_created),
            }
        )
    return pd.DataFrame(rows)
