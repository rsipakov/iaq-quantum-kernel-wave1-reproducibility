#!/usr/bin/env python3
"""Optional 4096-shot finite-shot projection for Wave 1 ZZ4.

This script rescales the finite-shot reference terms used in the Wave 1
shot-noise reference-scale decomposition from the executed 1024-shot run to the
originally planned 4096-shot budget. It keeps the realized off-diagonal RMSE
fixed and does not simulate or claim a new hardware kernel.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List


REGIMES = ("H0", "H1", "H2")
EXPECTED_EXECUTED_SHOTS = 1024
EXPECTED_PROJECTED_SHOTS = 4096
POLICY = "fixed_RMSE_shot_reference_rescaled_only_no_new_hardware_kernel"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_decomposition(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 3:
        raise SystemExit(f"ERROR: expected 3 decomposition rows, observed {len(rows)} in {path}")
    by = {row.get("regime_id"): row for row in rows}
    if set(by) != set(REGIMES):
        raise SystemExit(f"ERROR: expected regimes {REGIMES}, observed {sorted(by)}")
    return [by[r] for r in REGIMES]


def _f(row: dict, key: str) -> float:
    try:
        return float(row[key])
    except Exception as exc:
        raise SystemExit(f"ERROR: cannot parse {key!r} from row {row}: {exc}") from exc


def _i(row: dict, key: str) -> int:
    return int(round(_f(row, key)))


def _validate_scope(project_root: Path) -> None:
    scope_path = project_root / "config" / "wave1_scope.json"
    runtime_path = project_root / "metadata" / "zz4_wave1_runtime_options.json"
    job_path = project_root / "job_metadata" / "zz4_wave1_job_manifest.json"

    scope = _load_json(scope_path)
    runtime = _load_json(runtime_path)
    jobs = _load_json(job_path)

    if int(scope.get("shots_planned_per_circuit")) != EXPECTED_PROJECTED_SHOTS:
        raise SystemExit("ERROR: config/wave1_scope.json does not record planned 4096 shots per circuit")
    if int(scope.get("pair_count_expected")) != 300 or int(scope.get("circuit_count_expected")) != 900:
        raise SystemExit("ERROR: scope pair/circuit counts do not match the Wave 1 inventory")
    if scope.get("claims_policy", {}).get("allowed_interpretation") != "kernel-survival / hardware-distortion only":
        raise SystemExit("ERROR: scope claims policy changed")

    if int(runtime.get("shots_planned_per_circuit")) != EXPECTED_PROJECTED_SHOTS:
        raise SystemExit("ERROR: runtime options do not record planned 4096 shots per circuit")
    for regime in REGIMES:
        opts = runtime.get("regimes", {}).get(regime, {}).get("sampler_options", {})
        if int(opts.get("default_shots")) != EXPECTED_PROJECTED_SHOTS:
            raise SystemExit(f"ERROR: runtime default_shots for {regime} is not 4096")

    submitted = jobs.get("shots_submitted_per_circuit")
    if submitted != [EXPECTED_EXECUTED_SHOTS]:
        raise SystemExit(f"ERROR: job manifest submitted-shot ledger is {submitted!r}, expected [1024]")
    if not jobs.get("budget_safe_partial_submission"):
        raise SystemExit("ERROR: job manifest does not record budget_safe_partial_submission=true")
    if int(jobs.get("total_circuits_submitted")) != 900:
        raise SystemExit("ERROR: job manifest total_circuits_submitted is not 900")

    rows = jobs.get("rows", [])
    if len(rows) != 3:
        raise SystemExit("ERROR: job manifest does not contain three regime rows")
    for row in rows:
        regime = row.get("regime_id")
        if regime not in REGIMES:
            raise SystemExit(f"ERROR: unexpected job-manifest regime {regime!r}")
        if int(row.get("shots_submitted")) != EXPECTED_EXECUTED_SHOTS:
            raise SystemExit(f"ERROR: {regime} submitted shots are not 1024")
        if int(row.get("circuit_count_submitted")) != 300 or int(row.get("pair_count_covered")) != 300:
            raise SystemExit(f"ERROR: {regime} circuit/pair coverage mismatch")
        if not row.get("scope_lock_confirmed"):
            raise SystemExit(f"ERROR: {regime} scope lock is not confirmed")


def compute_projection(project_root: Path) -> List[Dict[str, object]]:
    decomposition_path = project_root / "hardware_analysis" / "zz4_wave1_shot_noise_reference_scale_decomposition.csv"
    rows = _load_decomposition(decomposition_path)
    _validate_scope(project_root)

    scale = math.sqrt(EXPECTED_EXECUTED_SHOTS / EXPECTED_PROJECTED_SHOTS)
    sigma_global_projected = 1.0 / math.sqrt(2.0 * EXPECTED_PROJECTED_SHOTS)
    out_rows: List[Dict[str, object]] = []

    for row in rows:
        regime = row["regime_id"]
        rmse = _f(row, "kernel_rmse")
        sigma_matrix_projected = _f(row, "sigma_shot_matrix") * scale
        shot_share_global = sigma_global_projected ** 2 / rmse ** 2
        shot_share_matrix = sigma_matrix_projected ** 2 / rmse ** 2

        if _i(row, "shots_observed_per_entry") != EXPECTED_EXECUTED_SHOTS:
            raise SystemExit(f"ERROR: {regime} decomposition row is not based on 1024 observed shots")
        if _i(row, "n") != 24 or _i(row, "omega_size_directed") != 552 or _i(row, "omega_size_unique_unordered") != 276:
            raise SystemExit(f"ERROR: {regime} decomposition row has unexpected N/Omega sizes")
        if row.get("decomposition_policy") != "diagnostic_quadrature_reference_not_physical_noise_model":
            raise SystemExit(f"ERROR: {regime} decomposition policy mismatch")

        out_rows.append({
            "regime_id": regime,
            "manuscript_configuration": row["manuscript_configuration"],
            "n": _i(row, "n"),
            "shots_observed_per_entry": EXPECTED_EXECUTED_SHOTS,
            "shots_projected_per_entry": EXPECTED_PROJECTED_SHOTS,
            "omega_size_directed": _i(row, "omega_size_directed"),
            "omega_size_unique_unordered": _i(row, "omega_size_unique_unordered"),
            "kernel_rmse_fixed": rmse,
            "sigma_shot_global_1024": _f(row, "sigma_shot_global"),
            "sigma_shot_global_projected": sigma_global_projected,
            "shot_share_global_1024": _f(row, "shot_share_global"),
            "shot_share_global_projected": shot_share_global,
            "residual_global_projected": math.sqrt(max(rmse ** 2 - sigma_global_projected ** 2, 0.0)),
            "residual_fraction_global_projected": 1.0 - shot_share_global,
            "sigma_shot_matrix_1024": _f(row, "sigma_shot_matrix"),
            "sigma_shot_matrix_projected": sigma_matrix_projected,
            "shot_share_matrix_1024": _f(row, "shot_share_matrix"),
            "shot_share_matrix_projected": shot_share_matrix,
            "residual_matrix_projected": math.sqrt(max(rmse ** 2 - sigma_matrix_projected ** 2, 0.0)),
            "residual_fraction_matrix_projected": 1.0 - shot_share_matrix,
            "R_global_projected": rmse / sigma_global_projected,
            "R_matrix_projected": rmse / sigma_matrix_projected,
            "projection_policy": POLICY,
        })

    return out_rows


def write_outputs(project_root: Path, rows: List[Dict[str, object]]) -> None:
    out_dir = project_root / "hardware_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "zz4_wave1_4096_shot_projection.csv"
    json_path = out_dir / "zz4_wave1_4096_shot_projection.json"
    md_path = out_dir / "zz4_wave1_4096_shot_projection.md"

    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    artifact = {
        "artifact_type": "zz4_wave1_4096_shot_projection",
        "schema_version": "v1.section3_6_projection",
        "source_shots_observed_per_entry": EXPECTED_EXECUTED_SHOTS,
        "projected_shots_per_entry": EXPECTED_PROJECTED_SHOTS,
        "projection_factor_for_sigma": math.sqrt(EXPECTED_EXECUTED_SHOTS / EXPECTED_PROJECTED_SHOTS),
        "global_reference_formula_projected": "1/sqrt(2*S_projected)",
        "matrix_reference_formula_projected": "sigma_shot_matrix_1024*sqrt(1024/S_projected)",
        "projection_policy": POLICY,
        "scope_caveat": (
            "This artifact rescales finite-shot reference terms only. It does not simulate "
            "or claim a 4096-shot IBM hardware rerun, does not change reconstructed kernels, "
            "and does not project CKA, KTA, classifier performance, or quantum advantage."
        ),
        "inputs": [
            "hardware_analysis/zz4_wave1_shot_noise_reference_scale_decomposition.csv",
            "config/wave1_scope.json",
            "metadata/zz4_wave1_runtime_options.json",
            "job_metadata/zz4_wave1_job_manifest.json",
        ],
        "rows": rows,
    }
    json_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    def pct(x: float) -> str:
        return f"{100.0*x:.2f}%"

    md = [
        "# ZZ4 Wave 1 optional 4096-shot projection\n\n",
        "This artifact projects only the finite-shot reference scales from the executed 1024-shot Wave 1 run to the originally planned 4096-shot budget. It keeps the observed off-diagonal RMSE fixed and does not simulate a new hardware kernel.\n\n",
        "Projection rules:\n\n",
        "$$\n"
        "\\sigma_{\\mathrm{ref,global}}(4096)=\\frac{1}{\\sqrt{2\\cdot4096}},\\qquad\n"
        "\\sigma_{\\mathrm{shot,matrix},r}(4096)=\\sigma_{\\mathrm{shot,matrix},r}(1024)\\sqrt{\\frac{1024}{4096}}.\n"
        "$$\n\n",
        "| Regime | Manuscript config | Fixed RMSE | $\\sigma_{\\mathrm{ref,global}}(4096)$ | Global shot share | Global residual fraction | $\\sigma_{\\mathrm{shot,matrix}}(4096)$ | Matrix shot share | Matrix residual fraction | $R_{\\mathrm{matrix}}(4096)$ |\n",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n",
    ]
    for row in rows:
        md.append(
            f"| `{row['regime_id']}` | `{row['manuscript_configuration']}` | "
            f"{float(row['kernel_rmse_fixed']):.6f} | {float(row['sigma_shot_global_projected']):.6f} | "
            f"{pct(float(row['shot_share_global_projected']))} | {pct(float(row['residual_fraction_global_projected']))} | "
            f"{float(row['sigma_shot_matrix_projected']):.6f} | {pct(float(row['shot_share_matrix_projected']))} | "
            f"{pct(float(row['residual_fraction_matrix_projected']))} | {float(row['R_matrix_projected']):.2f} |\n"
        )
    md.extend([
        "\nThe projected 4096-shot matrix-aware finite-shot share remains at or below 1% for every regime. Under the conservative global reference it remains below 7% for every regime. The projection therefore leaves residual hardware distortion as the dominant squared-RMSE component under the fixed-RMSE assumption.\n\n",
        "This is a deterministic precision-budget calculation, not a hardware-noise model and not evidence for a realized 4096-shot rerun.\n",
    ])
    md_path.write_text("".join(md), encoding="utf-8")


EXPECTED = {
    "H0": {
        "sigma_shot_global_projected": 0.011048543456039804,
        "shot_share_global_projected": 0.015845765765962794,
        "residual_global_projected": 0.08707229568960918,
        "residual_fraction_global_projected": 0.9841542342340373,
        "sigma_shot_matrix_projected": 0.004132803580695225,
        "shot_share_matrix_projected": 0.002217137898912121,
        "residual_matrix_projected": 0.08767311403002706,
        "residual_fraction_matrix_projected": 0.9977828621010879,
        "R_global_projected": 7.944075885286367,
        "R_matrix_projected": 21.237512483450626,
    },
    "H1": {
        "sigma_shot_global_projected": 0.011048543456039804,
        "shot_share_global_projected": 0.016342021188257998,
        "residual_global_projected": 0.08571842902752577,
        "residual_fraction_global_projected": 0.983657978811742,
        "sigma_shot_matrix_projected": 0.004121649068044685,
        "shot_share_matrix_projected": 0.0022742475532162984,
        "residual_matrix_projected": 0.08632920361272227,
        "residual_fraction_matrix_projected": 0.9977257524467837,
        "R_global_projected": 7.82252780256904,
        "R_matrix_projected": 20.969164753214887,
    },
    "H2": {
        "sigma_shot_global_projected": 0.011048543456039804,
        "shot_share_global_projected": 0.06686467330588872,
        "residual_global_projected": 0.041274230035544736,
        "residual_fraction_global_projected": 0.9331353266941113,
        "sigma_shot_matrix_projected": 0.004264141852916225,
        "shot_share_matrix_projected": 0.00995978487543135,
        "residual_matrix_projected": 0.04251410909080974,
        "residual_fraction_matrix_projected": 0.9900402151245686,
        "R_global_projected": 3.8672445535163282,
        "R_matrix_projected": 10.02016841335551,
    },
}


def assert_close(name: str, got: float, expected: float, tol: float = 5e-12) -> None:
    if not math.isfinite(got) or abs(got - expected) > tol:
        raise SystemExit(f"ERROR: {name}: got {got!r}, expected {expected!r}")


def check_outputs(project_root: Path) -> None:
    rows = compute_projection(project_root)
    by = {row["regime_id"]: row for row in rows}
    for regime, expected in EXPECTED.items():
        row = by[regime]
        for key, value in expected.items():
            assert_close(f"{regime} {key}", float(row[key]), value)

    csv_path = project_root / "hardware_analysis" / "zz4_wave1_4096_shot_projection.csv"
    json_path = project_root / "hardware_analysis" / "zz4_wave1_4096_shot_projection.json"
    md_path = project_root / "hardware_analysis" / "zz4_wave1_4096_shot_projection.md"
    for path in (csv_path, json_path, md_path):
        if not path.exists():
            raise SystemExit(f"ERROR: projection output is missing: {path}")

    with csv_path.open(newline="", encoding="utf-8") as fh:
        persisted = list(csv.DictReader(fh))
    if len(persisted) != 3:
        raise SystemExit("ERROR: projection CSV should contain exactly three rows")
    persisted_by = {row["regime_id"]: row for row in persisted}
    for regime, expected in EXPECTED.items():
        for key, value in expected.items():
            assert_close(f"persisted {regime} {key}", float(persisted_by[regime][key]), value)

    js = _load_json(json_path)
    if js.get("artifact_type") != "zz4_wave1_4096_shot_projection":
        raise SystemExit("ERROR: projection JSON artifact_type mismatch")
    if js.get("projection_policy") != POLICY:
        raise SystemExit("ERROR: projection JSON policy mismatch")
    if js.get("source_shots_observed_per_entry") != EXPECTED_EXECUTED_SHOTS:
        raise SystemExit("ERROR: projection JSON source shot count mismatch")
    if js.get("projected_shots_per_entry") != EXPECTED_PROJECTED_SHOTS:
        raise SystemExit("ERROR: projection JSON projected shot count mismatch")
    if "does not simulate" not in js.get("scope_caveat", ""):
        raise SystemExit("ERROR: projection JSON caveat does not state non-simulation scope")

    print("[section3.6] optional 4096-shot projection checks passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="Path to the reproducibility repository root")
    parser.add_argument("--check", action="store_true", help="Validate persisted projection outputs without changing scope")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if args.check:
        check_outputs(project_root)
    else:
        rows = compute_projection(project_root)
        write_outputs(project_root, rows)
        print("[section3.6] wrote hardware_analysis/zz4_wave1_4096_shot_projection.{csv,json,md}")


if __name__ == "__main__":
    main()
