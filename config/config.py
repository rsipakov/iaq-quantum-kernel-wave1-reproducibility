"""Project constants for the v5 Qiskit kernel stage.

This file deliberately freezes only the compact feature sets and onset targets
approved in the v5 plan. Do not add broad feature sets here during this stage;
that would make the QSVC comparison less defensible and more expensive.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

PRIMARY_TARGET = "event_onset_next_1h"
SECONDARY_TARGET = "event_onset_next_6h"
ALLOWED_TARGETS = (PRIMARY_TARGET, SECONDARY_TARGET)

# The three feature sets allowed for the Qiskit/statevector stage.
FEATURE_SETS: Dict[str, List[str]] = {
    "F_quantum_4": [
        "pm25_mean_last_1h",
        "pm10_mean_last_1h",
        "hcho_mean_last_1h",
        "tvoc_mean_last_1h",
    ],
    "F_quantum_5_RMA": [
        "pm25_mean_last_1h",
        "pm10_mean_last_1h",
        "hcho_mean_last_1h",
        "tvoc_mean_last_1h",
        "reliability_mean_core",
    ],
    "F_quantum_6_RMA_plus": [
        "pm25_mean_last_1h",
        "pm10_mean_last_1h",
        "hcho_mean_last_1h",
        "tvoc_mean_last_1h",
        "reliability_mean_core",
        "momentum_core_mean",
    ],
}

# Feature-map families to run for each feature set. Classical kernels are
# included for geometry diagnostics; the quantum kernels are the main stage.
KERNELS_BY_FEATURE_SET: Dict[str, List[str]] = {
    "F_quantum_4": ["linear", "rbf", "zz_statevector"],
    "F_quantum_5_RMA": ["linear", "rbf", "rma_statevector"],
    "F_quantum_6_RMA_plus": ["linear", "rbf", "rma_statevector"],
}

POLLUTANT_FEATURES = FEATURE_SETS["F_quantum_4"]
RELIABILITY_FEATURE = "reliability_mean_core"
MOMENTUM_FEATURE = "momentum_core_mean"

# Strict time-aware split from v5. Used only if the dataset lacks an explicit
# split column. Existing split columns take precedence.
TIME_SPLIT_WINDOWS: Dict[str, Tuple[str, str]] = {
    "train": ("2024-12-13 09:00:00", "2025-08-31 23:30:00"),
    "validation": ("2025-09-01 00:00:00", "2025-11-26 23:30:00"),
    "external_test": ("2026-02-01 00:00:00", "2026-04-29 23:30:00"),
}

SPLIT_ORDER = ("train", "validation", "external_test")

# Classical floors from v5. These are used for context; the package also
# computes precomputed linear/RBF kernels on the same scaled compact matrices.
CLASSICAL_FLOORS = {
    "event_onset_next_1h": {
        "gradient_boosting_F_quantum_4": {
            "feature_set": "F_quantum_4",
            "model": "Gradient Boosting",
            "pr_auc": 0.437991,
            "roc_auc": 0.776930,
            "balanced_accuracy": 0.710993,
            "precision": 0.364706,
            "recall": 0.873239,
            "f1": 0.514523,
            "tn": 394,
            "fp": 324,
            "fn": 27,
            "tp": 186,
        },
        "rbf_svm_F_quantum_4": {
            "feature_set": "F_quantum_4",
            "model": "RBF SVM",
            "pr_auc": 0.407941,
            "roc_auc": 0.759158,
            "balanced_accuracy": 0.690945,
            "precision": 0.369128,
            "recall": 0.774648,
            "f1": 0.500000,
            "tn": 436,
            "fp": 282,
            "fn": 48,
            "tp": 165,
        },
        "gradient_boosting_F_quantum_5_RMA": {
            "feature_set": "F_quantum_5_RMA",
            "model": "Gradient Boosting",
            "pr_auc": 0.414414,
            "roc_auc": 0.776963,
            "balanced_accuracy": 0.730233,
            "precision": 0.387029,
            "recall": 0.868545,
            "f1": 0.535456,
            "tn": 425,
            "fp": 293,
            "fn": 28,
            "tp": 185,
        },
    }
}

VALID_LABEL_CANDIDATES = {
    "event_onset_next_1h": [
        "label_valid_1h",
        "valid_label_1h",
        "is_label_valid_1h",
        "event_onset_next_1h_valid",
        "event_onset_next_1h_label_valid",
    ],
    "event_onset_next_6h": [
        "label_valid_6h",
        "valid_label_6h",
        "is_label_valid_6h",
        "event_onset_next_6h_valid",
        "event_onset_next_6h_label_valid",
    ],
}

SPLIT_COLUMN_CANDIDATES = [
    "split",
    "data_split",
    "dataset_split",
    "ml_split",
    "time_split",
]

WINDOW_END_CANDIDATES = ["window_end", "timestamp", "datetime", "time"]

ROW_ID_CANDIDATES = ["row_id", "sample_id", "id"]


@dataclass(frozen=True)
class StagePolicy:
    """Frozen v5 model-selection and evaluation policy."""

    allowed_targets: Tuple[str, str] = ALLOWED_TARGETS
    default_target: str = PRIMARY_TARGET
    default_selection_metric: str = "pr_auc"
    allowed_feature_sets: Tuple[str, str, str] = tuple(FEATURE_SETS.keys())
    external_split_name: str = "external_test"
    validation_split_name: str = "validation"
    train_split_name: str = "train"
