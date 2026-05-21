"""Qiskit feature-map builders for the v5 kernel stage.

Two circuit families are implemented:
1. standard ZZ feature map for pollutant-only F_quantum_4;
2. custom RMA-QFM for F_quantum_5_RMA and F_quantum_6_RMA_plus.

The RMA-QFM implementation is intentionally fixed-parameter at this stage. Do
not train feature-map parameters before the baseline statevector diagnostics are
stable; otherwise external-test interpretation gets muddy.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

from .config import MOMENTUM_FEATURE, POLLUTANT_FEATURES, RELIABILITY_FEATURE


def _require_qiskit() -> None:
    try:
        import qiskit  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on environment
        raise ImportError(
            "Qiskit is required for statevector quantum kernels. Install this package's "
            "requirements.txt first, then rerun."
        ) from exc


def parameter_sort_key(param: object) -> tuple:
    """Sort Qiskit Parameters as x[0], x[1], ... ."""
    name = getattr(param, "name", str(param))
    match = re.search(r"\[(\d+)\]$", name)
    if match:
        return (name.split("[")[0], int(match.group(1)))
    return (name, -1)


def parameter_order(circuit: object) -> List[object]:
    return sorted(list(circuit.parameters), key=parameter_sort_key)


def build_zz_feature_map(
    n_features: int,
    reps: int = 1,
    entanglement: str | Sequence[Sequence[int]] = "linear",
    alpha: float = 2.0,
):
    """Build the standard ZZ feature map using the modern function API.

    The v5 plan says to prefer ``qiskit.circuit.library.zz_feature_map`` and avoid
    relying on the older class API. A fallback to ``ZZFeatureMap`` is included only
    for older local environments.
    """
    _require_qiskit()
    try:
        from qiskit.circuit.library import zz_feature_map

        return zz_feature_map(
            feature_dimension=n_features,
            reps=reps,
            entanglement=entanglement,
            alpha=alpha,
            parameter_prefix="x",
            name=f"ZZ_F_quantum_{n_features}",
        )
    except Exception:  # pragma: no cover - compatibility fallback
        from qiskit.circuit.library import ZZFeatureMap

        return ZZFeatureMap(
            feature_dimension=n_features,
            reps=reps,
            entanglement=entanglement,
            alpha=alpha,
            parameter_prefix="x",
            name=f"ZZ_F_quantum_{n_features}",
        )


def build_rma_qfm(
    feature_names: Sequence[str],
    reps: int = 1,
    pollutant_scale: float = 1.0,
    reliability_scale: float = 1.0,
    momentum_scale: float = 1.0,
    pollutant_interaction_scale: float = 0.25,
    reliability_interaction_scale: float = 0.10,
    momentum_interaction_scale: float = 0.15,
    insert_barriers: bool = False,
):
    """Build the custom redundancy/missingness-aware feature map.

    Expected feature order is the v5 order:
    [PM2.5, PM10, HCHO, TVOC, reliability, optional momentum].

    Design choices:
    - pollutant levels are encoded on their own qubits using RY/RZ rotations;
    - reliability is encoded on a reliability qubit when present;
    - pollutant-pollutant interactions are damped by scaled reliability;
    - momentum gets its own qubit in F_quantum_6_RMA_plus and interacts with
      pollutant qubits, also damped by reliability.

    Since all input columns have already been scaled to [0, pi], the reliability
    factor is x_reliability / pi, so low-reliability rows reduce interaction
    strength instead of merely adding another raw feature.
    """
    _require_qiskit()
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector

    n_features = len(feature_names)
    if n_features not in (5, 6):
        raise ValueError(f"RMA-QFM expects 5 or 6 features, got {n_features}: {feature_names}")

    x = ParameterVector("x", n_features)
    qc = QuantumCircuit(n_features, name=f"RMA_QFM_{n_features}q")

    pollutant_indices = [i for i, name in enumerate(feature_names) if name in POLLUTANT_FEATURES]
    rel_idx = feature_names.index(RELIABILITY_FEATURE) if RELIABILITY_FEATURE in feature_names else None
    mom_idx = feature_names.index(MOMENTUM_FEATURE) if MOMENTUM_FEATURE in feature_names else None

    if len(pollutant_indices) != 4:
        raise ValueError(
            "RMA-QFM expects exactly the four pollutant features from F_quantum_4; "
            f"found pollutant indices {pollutant_indices} in {feature_names}."
        )
    if rel_idx is None:
        raise ValueError("RMA-QFM requires reliability_mean_core.")

    # Initial superposition layer. We use one H layer at the beginning and then
    # data re-uploading rotations for additional repetitions.
    for q in range(n_features):
        qc.h(q)
    if insert_barriers:
        qc.barrier()

    rel_factor = x[rel_idx] / np.pi

    for rep in range(reps):
        # Local pollutant encodings.
        for i in pollutant_indices:
            qc.ry(pollutant_scale * x[i], i)
            qc.rz(0.5 * pollutant_scale * x[i], i)

        # Reliability encoding.
        qc.ry(reliability_scale * x[rel_idx], rel_idx)
        qc.rz(0.5 * reliability_scale * x[rel_idx], rel_idx)

        # Optional momentum encoding.
        if mom_idx is not None:
            qc.ry(momentum_scale * x[mom_idx], mom_idx)
            qc.rz(0.5 * momentum_scale * x[mom_idx], mom_idx)

        if insert_barriers:
            qc.barrier()

        # Reliability-damped pollutant interactions.
        for a_pos, i in enumerate(pollutant_indices):
            for j in pollutant_indices[a_pos + 1 :]:
                angle = pollutant_interaction_scale * x[i] * x[j] * rel_factor
                qc.rzz(angle, i, j)

        # Explicit reliability-pollutant couplings. These keep reliability as a
        # geometric modulator, not merely a standalone appended feature.
        for i in pollutant_indices:
            qc.rzz(reliability_interaction_scale * x[rel_idx] * x[i], rel_idx, i)

        # Momentum-pollutant couplings for F_quantum_6_RMA_plus.
        if mom_idx is not None:
            for i in pollutant_indices:
                angle = momentum_interaction_scale * x[mom_idx] * x[i] * rel_factor
                qc.rzz(angle, mom_idx, i)

        if insert_barriers and rep < reps - 1:
            qc.barrier()

    return qc


def circuit_summary(circuit: object, kernel_name: str, feature_set: str, feature_names: Sequence[str]) -> Dict[str, object]:
    ops = circuit.count_ops() if hasattr(circuit, "count_ops") else {}
    try:
        depth = int(circuit.depth())
    except Exception:
        depth = None
    try:
        nonlocal_gates = int(circuit.num_nonlocal_gates())
    except Exception:
        nonlocal_gates = None
    return {
        "kernel_name": kernel_name,
        "feature_set": feature_set,
        "n_features": len(feature_names),
        "feature_names": list(feature_names),
        "num_qubits": int(getattr(circuit, "num_qubits", len(feature_names))),
        "num_parameters": int(getattr(circuit, "num_parameters", len(feature_names))),
        "depth": depth,
        "num_nonlocal_gates": nonlocal_gates,
        "operation_counts": dict(ops),
        "parameters_order": [getattr(p, "name", str(p)) for p in parameter_order(circuit)],
    }


def save_circuit_text(circuit: object, out_path: str | Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(str(circuit.draw(output="text")))
        f.write("\n")


def save_qasm_if_available(circuit: object, out_path: str | Path) -> None:
    """Save OpenQASM 2 text when supported by the installed Qiskit version."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:  # Qiskit 1.x/2.x
        import qiskit.qasm2 as qasm2

        text = qasm2.dumps(circuit)
    except Exception:  # pragma: no cover - version dependent
        try:
            text = circuit.qasm()
        except Exception as exc:
            text = f"OpenQASM export unavailable for this circuit/Qiskit version: {exc}\n"
    with out_path.open("w", encoding="utf-8") as f:
        f.write(text)
