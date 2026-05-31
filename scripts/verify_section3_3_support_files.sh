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
import math
from pathlib import Path

ROOT = Path.cwd()

required = [
    "frozen_subset/hardware_subset_event_onset_next_1h.csv",
    "statevector_reference/zz4_K_all_all.npy",
    "hardware_kernels/zz4_H0_kernel.npy",
    "hardware_kernels/zz4_H1_kernel.npy",
    "hardware_kernels/zz4_H2_kernel.npy",
    "hardware_analysis/zz4_wave1_distortion_metrics.csv",
    "hardware_analysis/zz4_wave1_distortion_uncertainty.csv",
    "hardware_analysis/zz4_wave1_distortion_uncertainty.json",
    "hardware_analysis/qiskit_kta_cka_permutation_tests.csv",
    "hardware_analysis/zz4_wave1_label_permutation_reference.csv",
    "hardware_analysis/zz4_wave1_label_permutation_reference.json",
    "scripts/09b_analyze_wave1_distortion_direct.py",
    "scripts/09c_wave1_distortion_uncertainty.py",
    "scripts/09e_label_permutation_reference.py",
    "scripts/copy_section3_3_support_files.sh",
    "scripts/verify_section3_3_support_files.sh",
    "scripts/publish_section3_3_updates.sh",
    "scripts/run_section3_3_copy_verify_publish.sh",
]

missing = [p for p in required if not (ROOT / p).is_file()]
if missing:
    raise SystemExit("Missing Section 3.3 support files:\n" + "\n".join(missing))

if (ROOT / "NewSection_3.3.md").exists():
    raise SystemExit("NewSection_3.3.md is present in the repository root; remove it before committing.")

def isclose(got: float, exp: float, tol: float = 2e-12) -> bool:
    return math.isclose(float(got), float(exp), rel_tol=0.0, abs_tol=tol)

def assert_close(label: str, got: float, exp: float, tol: float = 2e-12) -> None:
    if not isclose(got, exp, tol):
        raise AssertionError(f"{label}: got {got!r}, expected {exp!r}")

# Main metric table: centered KTA, CKA loss, RMSE point estimates, and blank correlation p-values.
with (ROOT / "hardware_analysis/zz4_wave1_distortion_metrics.csv").open(newline="") as f:
    metric_rows = list(csv.DictReader(f))
by_regime = {row["regime_id"]: row for row in metric_rows}
if set(by_regime) != {"H0", "H1", "H2"}:
    raise AssertionError(f"Unexpected regimes in distortion metrics: {sorted(by_regime)}")

expected_metrics = {
    "H0": {
        "KTA_hardware": 0.18330845936020965,
        "KTA_statevector": 0.15851109235208113,
        "CKA_hardware_vs_statevector": 0.9333906746578973,
        "CKA_drop_relative_to_statevector": 0.06660932534210273,
        "kernel_rmse": 0.08777046763666438,
    },
    "H1": {
        "KTA_hardware": 0.18146337847595853,
        "KTA_statevector": 0.15851109235208113,
        "CKA_hardware_vs_statevector": 0.9373725928446407,
        "CKA_drop_relative_to_statevector": 0.0626274071553593,
        "kernel_rmse": 0.08642753836276364,
    },
    "H2": {
        "KTA_hardware": 0.17102484410377672,
        "KTA_statevector": 0.15851109235208113,
        "CKA_hardware_vs_statevector": 0.9886681278100088,
        "CKA_drop_relative_to_statevector": 0.01133187218999121,
        "kernel_rmse": 0.042727419504658484,
    },
}
for regime, exp_row in expected_metrics.items():
    row = by_regime[regime]
    if int(float(row["n"])) != 24:
        raise AssertionError(f"{regime}: n is not 24")
    if int(float(row["shots_submitted_per_circuit"])) != 1024:
        raise AssertionError(f"{regime}: shots_submitted_per_circuit is not 1024")
    for key, exp in exp_row.items():
        assert_close(f"{regime}:{key}", float(row[key]), exp)
    for key in ("offdiag_spearman_pvalue", "offdiag_pearson_pvalue"):
        value = row.get(key, "")
        if value not in ("", "nan", "NaN"):
            raise AssertionError(f"{regime}:{key} should be blank/NaN, found {value!r}")

sv_kta = expected_metrics["H0"]["KTA_statevector"]
uplift = {r: expected_metrics[r]["KTA_hardware"] - sv_kta for r in expected_metrics}
expected_uplift = {
    "H0": 0.024797367008128512,
    "H1": 0.022952286123877397,
    "H2": 0.012513751751695584,
}
for regime, exp in expected_uplift.items():
    assert_close(f"{regime}:KTA_uplift", uplift[regime], exp)
if min(uplift, key=uplift.get) != "H2":
    raise AssertionError(f"H2 is not the smallest KTA uplift: {uplift}")
if min(expected_metrics, key=lambda r: expected_metrics[r]["CKA_drop_relative_to_statevector"]) != "H2":
    raise AssertionError("H2 is not the smallest CKA loss")
if max(expected_metrics, key=lambda r: expected_metrics[r]["KTA_hardware"]) != "H0":
    raise AssertionError("H0 is not the largest absolute hardware centered KTA")

# Uncertainty table: jackknife SEs, paired contrasts, diagonal sensitivity, and absence of RMSE jackknife.
with (ROOT / "hardware_analysis/zz4_wave1_distortion_uncertainty.csv").open(newline="") as f:
    unc_rows = list(csv.DictReader(f))

def find_unc(block: str, metric: str, *, configuration: str = "", contrast: str = "") -> dict[str, str]:
    for row in unc_rows:
        if row["analysis_block"] == block and row["metric"] == metric:
            if configuration and row["configuration"] != configuration:
                continue
            if contrast and row["contrast"] != contrast:
                continue
            return row
    raise AssertionError(f"Missing uncertainty row: block={block}, metric={metric}, configuration={configuration}, contrast={contrast}")

expected_jk = {
    ("spearman", "M0"): (0.741297081842571, 0.05166885705375388),
    ("spearman", "M1"): (0.7749509552911102, 0.04589102325987636),
    ("spearman", "M2"): (0.9437436780691297, 0.012376311673864835),
    ("pearson", "M0"): (0.8272527142734244, 0.08594432627666433),
    ("pearson", "M1"): (0.8427741783413908, 0.06277675376939476),
    ("pearson", "M2"): (0.9862028716378275, 0.004459596499479317),
    ("mae", "M0"): (0.04903588514843187, 0.007897398198223937),
    ("mae", "M1"): (0.04728950462019737, 0.00829447068845154),
    ("mae", "M2"): (0.025725586521733776, 0.003548693125357637),
    ("cka", "M0"): (0.9333906746578973, 0.02187344180828574),
    ("cka", "M1"): (0.9373725928446407, 0.01900059452538718),
    ("cka", "M2"): (0.9886681278100088, 0.002567019685430395),
    ("kta_centered", "M0"): (0.18330845936020965, 0.03622250597571749),
    ("kta_centered", "M1"): (0.18146337847595853, 0.03504521184642253),
    ("kta_centered", "M2"): (0.17102484410377672, 0.03596248412517801),
}
for (metric, config), (point, se) in expected_jk.items():
    row = find_unc("leave_one_window_out_jackknife", metric, configuration=config)
    assert_close(f"JK:{metric}:{config}:point", float(row["point_estimate"]), point)
    assert_close(f"JK:{metric}:{config}:se", float(row["jackknife_se"]), se)

expected_pairs = {
    ("spearman", "M2-M0"): (0.2024465962265587, 0.04988991625448438, 4.0578660263507995),
    ("spearman", "M2-M1"): (0.1687927227780195, 0.04280048977562128, 3.943710075816985),
    ("pearson", "M2-M0"): (0.1589501573644031, 0.08293699972115262, 1.9165168489192856),
    ("pearson", "M2-M1"): (0.1434286932964367, 0.05975686035230524, 2.4002046367702725),
    ("mae", "M2-M0"): (-0.023310298626698096, 0.004719830045904061, -4.938800422893854),
    ("mae", "M2-M1"): (-0.021563918098463593, 0.0050119937433453785, -4.302463092076852),
    ("cka", "M2-M0"): (0.05527745315211152, 0.019542775411780962, 2.828536478948054),
    ("cka", "M2-M1"): (0.051295534965368095, 0.016621093966445333, 3.086170806140891),
    ("kta_centered", "M2-M0"): (-0.012283615256432928, 0.014087845055608046, -0.8719300367051599),
    ("kta_centered", "M2-M1"): (-0.010438534372181812, 0.013435522037200404, -0.776935525339432),
}
for (metric, contrast), (delta, se_delta, z) in expected_pairs.items():
    row = find_unc("paired_jackknife_contrast", metric, contrast=contrast)
    assert_close(f"PAIR:{metric}:{contrast}:delta", float(row["delta"]), delta)
    assert_close(f"PAIR:{metric}:{contrast}:se_delta", float(row["jackknife_se_delta"]), se_delta)
    assert_close(f"PAIR:{metric}:{contrast}:z", float(row["z_descriptive"]), z)
    if "not a significance test" not in row["notes"]:
        raise AssertionError(f"PAIR:{metric}:{contrast} missing non-test note")

expected_diag_kta = {
    "M0": (0.18565077198604624, 0.00234231262583659),
    "M1": (0.18397549003914176, 0.0025121115631832336),
    "M2": (0.17414500728075, 0.0031201631769732785),
}
for config, (point, delta) in expected_diag_kta.items():
    row = find_unc("diagonal_robustness", "kta_centered", configuration=config, contrast="unit_diagonal_minus_measured_diagonal")
    assert_close(f"DIAG_KTA:{config}:point", float(row["point_estimate"]), point)
    assert_close(f"DIAG_KTA:{config}:delta", float(row["delta"]), delta)

for row in unc_rows:
    if row["metric"] == "rmse" and row["analysis_block"] in {"leave_one_window_out_jackknife", "paired_jackknife_contrast"}:
        raise AssertionError("RMSE should not have a persisted leave-one-window jackknife or paired contrast")

# Label-permutation reference: centered label alignment and provenance row.
with (ROOT / "hardware_analysis/zz4_wave1_label_permutation_reference.csv").open(newline="") as f:
    perm_rows = list(csv.DictReader(f))
perm = {(row["kernel_name"], row["metric"]): row for row in perm_rows}
if set(perm) != {("zz4", "CKA"), ("zz4", "KTA")}:
    raise AssertionError(f"Unexpected label-permutation rows: {sorted(perm)}")
expected_perm = {
    ("zz4", "CKA"): {
        "alignment_convention": "centered_label_alignment",
        "seed": 0,
        "n_perm": 5000,
        "n_rows": 24,
        "observed": 0.15851109235208113,
        "null_mean": 0.17097863873640975,
        "null_std": 0.035529129136444355,
        "null_q95": 0.23538745613549725,
        "null_q99": 0.26810527579522103,
        "p_upper_tail": 0.5988,
        "p_upper_tail_addone": 0.598880223955209,
        "p_two_sided_centered": 0.7294,
        "p_two_sided_2min": 0.8024,
    },
    ("zz4", "KTA"): {
        "alignment_convention": "uncentered_label_alignment",
        "seed": 0,
        "n_perm": 5000,
        "n_rows": 24,
        "observed": 0.13290938949796374,
        "null_mean": 0.1433632571351765,
        "null_std": 0.02979069030973804,
        "null_q95": 0.19736917225299094,
        "null_q99": 0.22480261790119554,
        "p_upper_tail": 0.5988,
        "p_upper_tail_addone": 0.598880223955209,
        "p_two_sided_centered": 0.7294,
        "p_two_sided_2min": 0.8024,
    },
}
for key, exp_row in expected_perm.items():
    row = perm[key]
    if row["alignment_convention"] != exp_row["alignment_convention"]:
        raise AssertionError(f"{key}: wrong alignment convention")
    for int_key in ("seed", "n_perm", "n_rows"):
        if int(row[int_key]) != int(exp_row[int_key]):
            raise AssertionError(f"{key}:{int_key} = {row[int_key]}, expected {exp_row[int_key]}")
    for float_key in (
        "observed", "null_mean", "null_std", "null_q95", "null_q99",
        "p_upper_tail", "p_upper_tail_addone", "p_two_sided_centered", "p_two_sided_2min",
    ):
        assert_close(f"PERM:{key}:{float_key}", float(row[float_key]), exp_row[float_key])

with (ROOT / "hardware_analysis/zz4_wave1_label_permutation_reference.json").open() as f:
    perm_json = json.load(f)
if perm_json.get("label_balance") != {"positive": 12, "negative": 12}:
    raise AssertionError(f"Unexpected label balance: {perm_json.get('label_balance')}")
if perm_json.get("inferential_policy") != "Statevector random-label reference only; not a hardware-configuration selection test and not a classifier-performance claim.":
    raise AssertionError("Unexpected permutation inferential policy")
if "source metric label CKA denotes the centered label-alignment row" not in perm_json.get("convention_note", ""):
    raise AssertionError("Missing permutation convention note")

# Static source-derived permutation table retained for provenance.
with (ROOT / "hardware_analysis/qiskit_kta_cka_permutation_tests.csv").open(newline="") as f:
    static_rows = list(csv.DictReader(f))
static_zz4 = {(row["kernel_name"], row["metric"]): row for row in static_rows if row["kernel_name"] == "zz4"}
if set(static_zz4) != {("zz4", "CKA"), ("zz4", "KTA")}:
    raise AssertionError(f"Unexpected static zz4 rows: {sorted(static_zz4)}")
assert_close("STATIC:zz4:CKA:observed", float(static_zz4[("zz4", "CKA")]["observed"]), 0.15851109235208113)
assert_close("STATIC:zz4:KTA:observed", float(static_zz4[("zz4", "KTA")]["observed"]), 0.13290938949796374)
for key in (("zz4", "CKA"), ("zz4", "KTA")):
    p_static = float(static_zz4[key]["p_perm_two_sided"])
    if not (0.58 < p_static < 0.61):
        raise AssertionError(f"Static source p field is outside expected upper-tail envelope for {key}: {p_static}")
    if static_zz4[key]["significant_alignment"] != "False" or static_zz4[key]["strong_alignment"] != "False":
        raise AssertionError(f"Static source significance flags are unexpected for {key}")

print("Section 3.3 verification passed.")
print("statistical table: jackknife SEs and paired z_desc only; no adjusted hardware-contrast p-values")
print("RMSE: point estimate only; no persisted jackknife or paired contrast")
print("label permutation: centered statevector alignment below null mean; p_upper_tail=0.5988")
print("CKA/KTA tension: H2 has smallest CKA loss and smallest KTA uplift; H0 has largest hardware KTA")
print("diagonal sensitivity: unit-diagonal KTA change <= 0.0032 and does not change ordering")
PY
