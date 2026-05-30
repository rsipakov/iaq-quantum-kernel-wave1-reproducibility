#!/usr/bin/env bash
set -euo pipefail

REPRO="${1:-/Users/rostyslavsipakov/Documents/GitHub/reproducibility/iaq-quantum-kernel-wave1-reproducibility}"
if [[ ! -d "$REPRO" ]]; then
  echo "ERROR: REPRO does not exist: $REPRO" >&2
  exit 1
fi

cd "$REPRO"

python - <<'PY'
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp; tolerate a trailing 'Z' and a space separator."""
    text = str(value).strip().replace("Z", "+00:00")
    if "T" not in text and " " in text:
        text = text.replace(" ", "T", 1)
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


required = [
    "metadata/zz_only_step8_execution_manifest.json",
    "metadata/zz4_wave1_runtime_options.json",
    "metadata/zz4_wave1_runtime_options_sha256.txt",
    "metadata/zz_only_step9_live_backend_metadata.json",
    "hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.json",
    "hardware_compile/zz4_step9_backend_compile_confirmation_ibm_fez.csv",
    "job_metadata/zz4_wave1_job_manifest.json",
    "job_metadata/zz4_wave1_job_manifest.csv",
    "job_metadata/zz4_wave1_job_manifest_H0_1024.json",
    "job_metadata/zz4_wave1_job_manifest_H0_1024.csv",
    "job_metadata/zz4_wave1_job_manifest_H1_1024.json",
    "job_metadata/zz4_wave1_job_manifest_H1_1024.csv",
    "job_metadata/zz4_wave1_job_manifest_H2_1024.json",
    "job_metadata/zz4_wave1_job_manifest_H2_1024.csv",
    "job_metadata/zz4_wave1_retrieval_manifest.json",
    "logs/zz4_wave1_submission_log.md",
    "logs/zz4_wave1_retrieval_log.md",
    "hardware_results/zz4_H0_raw_results.json",
    "hardware_results/zz4_H1_raw_results.json",
    "hardware_results/zz4_H2_raw_results.json",
    "hardware_kernels/zz4_wave1_kernel_entries_long.csv",
]

missing = [p for p in required if not (ROOT / p).is_file()]
if missing:
    raise SystemExit("Missing Section 3.1 support files:\n" + "\n".join(missing))

manifest = json.loads((ROOT / "job_metadata/zz4_wave1_job_manifest.json").read_text())
selected = manifest.get("selected_regimes")
assert selected == ["H0", "H1", "H2"], selected
assert manifest.get("shots_submitted_per_circuit") == [1024], manifest.get("shots_submitted_per_circuit")
assert manifest.get("total_circuits_submitted") == 900, manifest.get("total_circuits_submitted")
rows = manifest.get("rows", [])
assert len(rows) == 3, len(rows)
expected_jobs = {
    "H0": "d7vf6n3ack5s73bfc0eg",
    "H1": "d7vf8ocinasc738u1bhg",
    "H2": "d7vfbsfmrars73d84u20",
}
for row in rows:
    regime = row["regime_id"]
    assert regime in expected_jobs, regime
    assert row["job_id"] == expected_jobs[regime], row
    assert int(row["shots_submitted"]) == 1024, row
    assert int(row["circuit_count_submitted"]) == 300, row
    assert int(row["pair_count_covered"]) == 300, row
    assert bool(row["scope_lock_confirmed"]) is True, row
    assert bool(row["rma_excluded"]) is True, row
    assert bool(row["wave2_excluded"]) is True, row

retrieval = json.loads((ROOT / "job_metadata/zz4_wave1_retrieval_manifest.json").read_text())
assert retrieval.get("retrieved_or_failures_recorded") is True, retrieval
assert retrieval.get("failure_reasons") == [], retrieval.get("failure_reasons")
for row in retrieval.get("rows", []):
    regime = row["regime_id"]
    assert row["job_id"] == expected_jobs[regime], row
    assert row["retrieved_status"] == "retrieved", row
    assert row["job_status"] == "DONE", row
    assert int(row["pub_result_count"]) == 300, row
    assert row.get("failure_or_exception_if_any", "") == "", row

# ---------------------------------------------------------------------------
# Section 3.1 billed-quantum-second grounding.
#
# The IBM-reported usage seconds ARE persisted in each raw-result file, under
# the top-level "job_metrics" object (a sibling of "entries"). They are NOT in
# the job/retrieval manifests, so a manifest-only inspection misses them. For
# every regime the three reported sub-fields agree:
#     job_metrics.usage.quantum_seconds == job_metrics.usage.seconds == job_metrics.bss.seconds
# This block makes that grounding a required, machine-checked invariant rather
# than a hand-entered value.
# ---------------------------------------------------------------------------
expected_quantum_seconds = {"H0": 80, "H1": 80, "H2": 84}
billed_quantum_seconds: dict[str, int] = {}

for regime in ["H0", "H1", "H2"]:
    raw_path = ROOT / f"hardware_results/zz4_{regime}_raw_results.json"
    raw = json.loads(raw_path.read_text())
    assert raw["regime_id"] == regime, raw["regime_id"]
    assert raw["job_id"] == expected_jobs[regime], raw["job_id"]
    assert int(raw["circuit_count_hint"]) == 300, raw["circuit_count_hint"]
    assert int(raw["pub_result_count"]) == 300, raw["pub_result_count"]
    entries = raw.get("entries", [])
    assert len(entries) == 300, (regime, len(entries))
    shots = {int(e["shots_observed"]) for e in entries}
    assert shots == {1024}, (regime, shots)
    if regime == "H2":
        randomizations = {
            e.get("metadata", {}).get("num_randomizations")
            for e in entries
            if "metadata" in e
        }
        assert randomizations == {16}, randomizations

    # --- IBM-reported billed quantum seconds (job-level usage telemetry) ---
    jmetrics = raw.get("job_metrics")
    assert isinstance(jmetrics, dict), f"{regime}: job_metrics object missing from raw-result file"
    usage = jmetrics.get("usage", {})
    bss = jmetrics.get("bss", {})
    q_usage = usage.get("quantum_seconds")
    s_usage = usage.get("seconds")
    s_bss = bss.get("seconds")
    assert q_usage is not None, f"{regime}: job_metrics.usage.quantum_seconds missing"
    assert s_usage is not None, f"{regime}: job_metrics.usage.seconds missing"
    assert s_bss is not None, f"{regime}: job_metrics.bss.seconds missing"
    # The three reported usage sub-fields must agree (integrity cross-check).
    assert int(q_usage) == int(s_usage) == int(s_bss), (
        f"{regime}: usage sub-fields disagree: "
        f"usage.quantum_seconds={q_usage}, usage.seconds={s_usage}, bss.seconds={s_bss}"
    )
    # And the billed value must match the per-regime expectation.
    assert int(q_usage) == expected_quantum_seconds[regime], (
        f"{regime}: billed quantum seconds = {q_usage}, expected {expected_quantum_seconds[regime]}"
    )
    billed_quantum_seconds[regime] = int(q_usage)

    # Job-lifecycle timestamps: present and monotonic (created <= running <= finished).
    ts = jmetrics.get("timestamps", {})
    for key in ("created", "running", "finished"):
        assert ts.get(key), f"{regime}: job_metrics.timestamps.{key} missing"
    t_created = parse_iso(ts["created"])
    t_running = parse_iso(ts["running"])
    t_finished = parse_iso(ts["finished"])
    assert t_created <= t_running <= t_finished, f"{regime}: timestamps not monotonic: {ts}"

total_billed = sum(billed_quantum_seconds[r] for r in expected_jobs)
assert total_billed == 244, total_billed

long_path = ROOT / "hardware_kernels/zz4_wave1_kernel_entries_long.csv"
with long_path.open(newline="") as f:
    reader = csv.DictReader(f)
    long_rows = list(reader)
assert len(long_rows) == 900, len(long_rows)
regime_counts = {r: 0 for r in expected_jobs}
shots_seen = set()
for row in long_rows:
    regime = row.get("regime") or row.get("regime_id") or row.get("artifact_regime")
    if regime not in regime_counts:
        raise AssertionError(f"Unexpected regime in kernel entries: {regime!r}")
    regime_counts[regime] += 1
    shots_key = "shots_observed" if "shots_observed" in row else "observed_shots"
    shots_seen.add(int(float(row[shots_key])))
assert regime_counts == {"H0": 300, "H1": 300, "H2": 300}, regime_counts
assert shots_seen == {1024}, shots_seen

if (ROOT / "NewSection_3.1.md").exists():
    raise SystemExit("NewSection_3.1.md is present in the repository root; remove it before committing.")

# ---------------------------------------------------------------------------
# Optional hand-entered usage CSV.
#
# The billed quantum seconds are already repository-grounded from job_metrics
# above, so this CSV is redundant. If it is nonetheless present, it must AGREE
# with the raw-file telemetry (it is treated as a derived convenience copy, not
# as an independent source of truth).
# ---------------------------------------------------------------------------
usage_path = ROOT / "hardware_analysis/zz4_wave1_quantum_usage_seconds.csv"
if usage_path.exists():
    with usage_path.open(newline="") as f:
        usage_rows = list(csv.DictReader(f))
    by_regime = {row["artifact_label"]: row for row in usage_rows}
    for regime, seconds in expected_quantum_seconds.items():
        row = by_regime.get(regime)
        assert row is not None, f"missing usage row for {regime}"
        assert row["job_id"] == expected_jobs[regime], row
        csv_value = int(float(row["actual_quantum_seconds"]))
        assert csv_value == seconds, row
        # Must also agree with the grounded raw-file telemetry.
        assert csv_value == billed_quantum_seconds[regime], (
            f"{regime}: usage CSV ({csv_value}) disagrees with job_metrics telemetry "
            f"({billed_quantum_seconds[regime]})"
        )
    total_csv = sum(int(float(by_regime[r]["actual_quantum_seconds"])) for r in expected_quantum_seconds)
    assert total_csv == 244, total_csv
    usage_msg = (
        "optional usage-seconds CSV present and consistent with job_metrics telemetry "
        "(total=244)."
    )
else:
    usage_msg = (
        "optional usage-seconds CSV not present; billed quantum seconds are already "
        "repository-grounded from job_metrics.usage.quantum_seconds (no hand-entered file needed)."
    )

print("Section 3.1 verification passed.")
print("selected regimes:", ", ".join(selected))
print("submitted shots per circuit: 1024")
print("submitted circuit-regime configurations: 900")
print("retrieved PUB results per regime: 300")
print("job statuses: DONE, DONE, DONE")
print("raw-result observed shots: 1024 for every entry")
print("kernel-entry long table: 900 rows; H0=300, H1=300, H2=300")
print(
    "billed quantum seconds (job_metrics.usage.quantum_seconds): "
    f"H0={billed_quantum_seconds['H0']}, H1={billed_quantum_seconds['H1']}, H2={billed_quantum_seconds['H2']}"
)
print("usage sub-fields agree per regime: usage.quantum_seconds = usage.seconds = bss.seconds")
print(f"total billed quantum seconds: {total_billed} (~{total_billed / 60:.2f} min)")
print(usage_msg)
PY
