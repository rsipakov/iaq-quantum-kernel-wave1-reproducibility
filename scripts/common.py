#!/usr/bin/env python3
"""
Common utilities for the v9 ZZ4 Wave 1 hardware package.

Design rules:
- Never persist IBM token values.
- Keep every generated artifact hashable and JSON-serializable.
- Treat scope drift as a hard stop before submission.
- Use conservative, auditable failure records instead of silent fallbacks.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import importlib.metadata
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCOPE_CONFIG = PACKAGE_ROOT / "config" / "wave1_scope.json"
DEFAULT_PATHS_CONFIG = PACKAGE_ROOT / "config" / "wave1_paths.json"
DEFAULT_RUNTIME_OPTIONS_TEMPLATE = PACKAGE_ROOT / "config" / "runtime_options_template.json"

SECRET_PATTERNS = [
    # Detect explicit token-like assignments. The package itself contains field names
    # such as token_value_absent_from_artifact, so this intentionally checks values.
    re.compile(r"(?i)(?:ibm[_-]?quantum[_-]?token|api[_-]?token|token)\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{32,})"),
    re.compile(r"(?i)Authorization\s*:\s*Bearer\s+([A-Za-z0-9._\-]{32,})"),
]

ALLOWED_DECISIONS = {
    "STOP_AFTER_WAVE1_REPORT_RESULTS",
    "PROCEED_TO_WAVE2_SENTINEL_ONLY",
    "RETRY_WAVE1_WITH_DOCUMENTED_REASON",
    "NO_GO_HARDWARE_RESULTS_UNUSABLE",
}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_obj(obj: Any) -> str:
    return sha256_text(canonical_json(obj))


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=2, sort_keys=False, ensure_ascii=False)
    # A newline makes diffs and checksum review easier.
    path.write_text(text + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_log(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def resolve_project_path(project_root: Path, rel_or_abs: str | Path) -> Path:
    p = Path(rel_or_abs)
    return p if p.is_absolute() else project_root / p


def load_scope(scope_config: Optional[Path] = None) -> Dict[str, Any]:
    return read_json(scope_config or DEFAULT_SCOPE_CONFIG)


def load_paths(paths_config: Optional[Path] = None) -> Dict[str, Any]:
    return read_json(paths_config or DEFAULT_PATHS_CONFIG)


def default_runtime_options() -> Dict[str, Any]:
    return read_json(DEFAULT_RUNTIME_OPTIONS_TEMPLATE)


def ensure_output_dirs(project_root: Path, paths: Mapping[str, Any]) -> None:
    outputs = paths.get("outputs", {})
    for key, rel in outputs.items():
        if key.endswith("_dir"):
            resolve_project_path(project_root, rel).mkdir(parents=True, exist_ok=True)


def parser_with_project(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--project-root", default=".", help="Repository/project root. Default: current directory.")
    p.add_argument("--scope-config", default=str(DEFAULT_SCOPE_CONFIG), help="Path to wave1_scope.json.")
    p.add_argument("--paths-config", default=str(DEFAULT_PATHS_CONFIG), help="Path to wave1_paths.json.")
    p.add_argument("--operator", default=os.environ.get("WAVE1_OPERATOR", "unspecified"), help="Operator identifier to archive.")
    return p


def fail_record(artifact_type: str, failure_reasons: Sequence[str], **extra: Any) -> Dict[str, Any]:
    rec = {
        "artifact_type": artifact_type,
        "created_utc": utc_now(),
        "status": "failed",
        "failure_reasons": list(failure_reasons),
    }
    rec.update(extra)
    return rec


def package_versions() -> Dict[str, Optional[str]]:
    names = ["qiskit", "qiskit-ibm-runtime", "numpy", "pandas", "scipy", "matplotlib"]
    out: Dict[str, Optional[str]] = {}
    for name in names:
        try:
            out[name.replace("-", "_") + "_version"] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name.replace("-", "_") + "_version"] = None
    return out


def safe_getattr_or_call(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    value = getattr(obj, name, default)
    if callable(value):
        try:
            return value()
        except TypeError:
            return value
        except Exception:
            return default
    return value


def to_jsonable(obj: Any, max_str_len: int = 20000) -> Any:
    """Best-effort conversion of Qiskit/IBM objects into JSON-safe structures."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return str(obj)
        if isinstance(obj, str) and len(obj) > max_str_len:
            return obj[:max_str_len] + "...[truncated]"
        return obj
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(x, max_str_len=max_str_len) for x in obj]
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v, max_str_len=max_str_len) for k, v in obj.items()}
    for method_name in ("to_dict", "model_dump"):
        method = getattr(obj, method_name, None)
        if callable(method):
            try:
                return to_jsonable(method(), max_str_len=max_str_len)
            except Exception:
                pass
    if hasattr(obj, "__dict__"):
        try:
            d = {k: v for k, v in vars(obj).items() if not k.lower().endswith("token")}
            return to_jsonable(d, max_str_len=max_str_len)
        except Exception:
            pass
    return str(obj)[:max_str_len]


def scan_text_for_secret_values(text: str) -> List[str]:
    findings: List[str] = []
    for pattern in SECRET_PATTERNS:
        for m in pattern.finditer(text):
            tokenish = m.group(1)
            findings.append(f"secret-like token value detected: sha256={sha256_text(tokenish)[:16]}")
    return findings


def scan_file_for_secret_values(path: Path) -> List[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    return scan_text_for_secret_values(text)


def scan_tree_for_secret_values(root: Path, include_suffixes: Sequence[str] = (".json", ".csv", ".md", ".txt", ".py", ".log")) -> Dict[str, List[str]]:
    findings: Dict[str, List[str]] = {}
    if not root.exists():
        return findings
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in include_suffixes:
            f = scan_file_for_secret_values(path)
            if f:
                findings[str(path)] = f
    return findings


def file_record(project_root: Path, rel: str) -> Dict[str, Any]:
    p = resolve_project_path(project_root, rel)
    return {
        "path": rel,
        "exists": p.exists(),
        "is_file": p.is_file(),
        "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
        "sha256": sha256_file(p),
    }


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Optional[Sequence[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: List[str] = []
        for row in rows:
            for k in row.keys():
                if k not in keys:
                    keys.append(k)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames))
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def infer_column(columns: Iterable[str], candidates: Sequence[str], purpose: str) -> str:
    cols = list(columns)
    lower_map = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in cols:
            return cand
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise ValueError(f"Cannot infer {purpose} column. Available columns={cols}; candidates={list(candidates)}")


def normalize_regimes(regimes: Sequence[str]) -> List[str]:
    return sorted(str(r).strip() for r in regimes)


def validate_runtime_options_structure(obj: Mapping[str, Any], scope: Mapping[str, Any]) -> List[str]:
    reasons: List[str] = []
    regimes = obj.get("regimes", {})
    expected_regimes = normalize_regimes(scope.get("allowed_wave1_regimes", []))
    actual_regimes = normalize_regimes(regimes.keys() if isinstance(regimes, dict) else [])
    if actual_regimes != expected_regimes:
        reasons.append(f"runtime options regimes mismatch: expected {expected_regimes}, got {actual_regimes}")
    shots = obj.get("shots_planned_per_circuit")
    if shots != scope.get("shots_planned_per_circuit"):
        reasons.append(f"shots mismatch: expected {scope.get('shots_planned_per_circuit')}, got {shots}")
    # H1 and H2 must stay separate: H1 DD only, H2 twirling only.
    for regime in expected_regimes:
        opts = regimes.get(regime, {}).get("sampler_options", {}) if isinstance(regimes, dict) else {}
        dd = opts.get("dynamical_decoupling", {})
        tw = opts.get("twirling", {})
        if regime == "H1":
            if dd.get("enable") is not True:
                reasons.append("H1 must enable dynamical_decoupling")
            if tw.get("enable_gates") or tw.get("enable_measure"):
                reasons.append("H1 must not enable twirling")
        if regime == "H2":
            if dd.get("enable"):
                reasons.append("H2 must not enable dynamical_decoupling")
            if tw.get("enable_gates") is not True:
                reasons.append("H2 must enable gate twirling")
            if tw.get("enable_measure"):
                reasons.append("H2 must not enable measurement twirling in this Wave 1 package")
        if regime == "H0":
            if dd.get("enable") or tw.get("enable_gates") or tw.get("enable_measure"):
                reasons.append("H0 must be unmitigated baseline")
    return reasons


def get_runtime_options_hashes(runtime_options: Mapping[str, Any]) -> Dict[str, str]:
    regimes = runtime_options.get("regimes", {})
    out = {}
    for regime, payload in regimes.items():
        out[f"runtime_options_sha256_{regime}"] = sha256_obj(payload.get("sampler_options", {}))
    out["runtime_options_all_sha256"] = sha256_obj(runtime_options)
    return out


def load_service():
    """Instantiate QiskitRuntimeService without writing token values anywhere."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    channel = os.environ.get("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")
    instance = os.environ.get("IBM_QUANTUM_INSTANCE") or None
    token = os.environ.get("IBM_QUANTUM_TOKEN") or None

    kwargs = {"channel": channel}
    if instance:
        kwargs["instance"] = instance
    if token:
        kwargs["token"] = token

    return QiskitRuntimeService(**kwargs)


def get_backend(service: Any, backend_name: str) -> Any:
    try:
        return service.backend(backend_name)
    except Exception:
        backs = service.backends(name=backend_name)
        if not backs:
            raise
        return backs[0]


def backend_metadata_snapshot(backend: Any) -> Dict[str, Any]:
    status = None
    try:
        status = backend.status()
    except Exception:
        pass

    target = None
    try:
        target = backend.target
    except Exception:
        pass

    # Avoid archiving very large backend properties by default; keep high-level audit metadata.
    return {
        "backend_name": safe_getattr_or_call(backend, "name"),
        "backend_version": safe_getattr_or_call(backend, "version", safe_getattr_or_call(backend, "backend_version")),
        "backend_num_qubits": safe_getattr_or_call(backend, "num_qubits"),
        "backend_status_or_availability_snapshot": to_jsonable(status),
        "operation_names": sorted(list(getattr(target, "operation_names", []) or [])) if target is not None else None,
        "dt": to_jsonable(safe_getattr_or_call(backend, "dt")),
        "online_date": str(safe_getattr_or_call(backend, "online_date", "")),
    }


def assert_no_token_env_written(obj: Any) -> None:
    text = canonical_json(obj)
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if token and token in text:
        raise RuntimeError("IBM token value would be written to an artifact; refusing to write.")


def write_safe_json(path: Path, obj: Mapping[str, Any]) -> None:
    assert_no_token_env_written(obj)
    write_json(path, obj)


def count_csv_rows(path: Path) -> Optional[int]:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8", newline="") as f:
        return max(sum(1 for _ in f) - 1, 0)


def parse_intish(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("bool is not an integer index")
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return int(s)


def all_zero_key(num_qubits: int) -> str:
    return "0" * int(num_qubits)


def probability_of_all_zero(counts: Mapping[str, Any], num_qubits: int, shots_hint: Optional[int] = None) -> Tuple[float, int, int, str]:
    """Return P(00..0), all_zero_count, total_count, key_used."""
    target = all_zero_key(num_qubits)
    normalized: Dict[str, int] = {}
    for k, v in counts.items():
        key = str(k).replace(" ", "")
        try:
            normalized[key] = normalized.get(key, 0) + int(v)
        except Exception:
            continue
    total = sum(normalized.values())
    if total <= 0 and shots_hint:
        total = shots_hint
    count0 = normalized.get(target, 0)
    return (float(count0) / float(total) if total else float("nan"), count0, total, target)


def pair_indices_from_inventory_rows(rows: Sequence[Mapping[str, Any]], paths: Mapping[str, Any]) -> Tuple[str, str, Optional[str]]:
    candidates = paths.get("pair_column_candidates", {})
    if not rows:
        raise ValueError("pair inventory is empty")
    cols = rows[0].keys()
    i_col = infer_column(cols, candidates.get("i", []), "pair i")
    j_col = infer_column(cols, candidates.get("j", []), "pair j")
    pair_id_col = None
    try:
        pair_id_col = infer_column(cols, candidates.get("pair_id", []), "pair id")
    except Exception:
        pair_id_col = None
    return i_col, j_col, pair_id_col


def read_matrix_csv(path: Path) -> "Any":
    import numpy as np
    import pandas as pd
    df = pd.read_csv(path, header=None)
    # If the first row/column look like labels, retry with index_col.
    arr = df.values
    try:
        arr = arr.astype(float)
    except Exception:
        df = pd.read_csv(path, index_col=0)
        arr = df.values.astype(float)
    return np.asarray(arr, dtype=float)


def write_matrix_csv(path: Path, matrix: "Any") -> None:
    import pandas as pd
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(matrix).to_csv(path, index=False, header=False)


def nearest_psd_by_eigenclip(matrix: "Any") -> Tuple["Any", Dict[str, float]]:
    import numpy as np
    sym = 0.5 * (matrix + matrix.T)
    eigvals, eigvecs = np.linalg.eigh(sym)
    clipped = np.clip(eigvals, 0.0, None)
    psd = (eigvecs * clipped) @ eigvecs.T
    denom = np.linalg.norm(sym, ord="fro")
    frob = np.linalg.norm(psd - sym, ord="fro")
    return psd, {
        "min_eigenvalue_before_psd": float(np.min(eigvals)),
        "min_eigenvalue_after_psd": float(np.min(np.linalg.eigvalsh(psd))),
        "psd_correction_frobenius_norm": float(frob),
        "psd_correction_frobenius_relative": float(frob / denom) if denom else float("nan"),
    }


def centered_kernel(matrix: "Any") -> "Any":
    import numpy as np
    n = matrix.shape[0]
    h = np.eye(n) - np.ones((n, n)) / n
    return h @ matrix @ h


def kernel_target_alignment(matrix: "Any", labels: Sequence[int]) -> float:
    import numpy as np
    y = np.asarray(labels)
    y = np.where(y > 0, 1.0, -1.0)
    yy = np.outer(y, y)
    denom = np.linalg.norm(matrix, "fro") * np.linalg.norm(yy, "fro")
    return float(np.sum(matrix * yy) / denom) if denom else float("nan")


def centered_kernel_alignment(matrix: "Any", labels: Sequence[int]) -> float:
    import numpy as np
    k = centered_kernel(matrix)
    y = np.asarray(labels)
    y = np.where(y > 0, 1.0, -1.0)
    yy = centered_kernel(np.outer(y, y))
    denom = np.linalg.norm(k, "fro") * np.linalg.norm(yy, "fro")
    return float(np.sum(k * yy) / denom) if denom else float("nan")


def effective_rank_from_eigvals(eigvals: Sequence[float]) -> float:
    import numpy as np
    vals = np.clip(np.asarray(eigvals, dtype=float), 0.0, None)
    total = vals.sum()
    if total <= 0:
        return float("nan")
    p = vals / total
    p = p[p > 0]
    entropy = -float(np.sum(p * np.log(p)))
    return float(np.exp(entropy))
