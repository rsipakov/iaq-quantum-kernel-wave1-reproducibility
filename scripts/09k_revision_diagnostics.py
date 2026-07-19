#!/usr/bin/env python3
"""Revision diagnostics for the Wave 1 ZZ4 manuscript (peer-review revision; package v1.3).

Computes, from the frozen v1.2 reproducibility-package artifacts only:
  (i)   diagonal-robust CKA variants (unit-diagonal, centered off-diagonal cosine,
        U-centered HSIC_1 alignment per Song et al. 2012);
  (ii)  numerator/denominator attribution of the centered-KTA uplift;
  (iii) count-level finite-shot resampling references (binomial at S=1024) around
        the statevector and around each measured hardware kernel;
  (iv)  per-regime hardware label-permutation references (B=5000) and a
        split-preserving permutation variant;
  (v)   classical comparator kernels (linear, RBF median heuristic) with
        permutation references;
  (vi)  leave-one-window-out jackknife for RMSE and for the single-regime
        centered-KTA uplift; cross-checks against persisted jackknife values;
  (vii) frozen-window temporal ledger summaries;
  (viii) statevector regeneration check from the frozen scaled inputs (pure numpy).

Deterministic quantities are seed-free; stochastic references use the fixed
seeds in SEEDS below. Nothing in the frozen package is modified.

Run from anywhere; by default the package root is resolved as the parent of the
scripts/ directory and the output is written to
hardware_analysis/zz4_wave1_revision_diagnostics.json inside the package.

Usage: python3 scripts/09k_revision_diagnostics.py [--package-root PATH]
       [--out PATH] [--check] [--rtol FLOAT] [--atol FLOAT]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEEDS = {"shot_null_sv": 101, "shot_null_hw": 102, "perm_hw_sv": 104,
         "perm_strat": 105, "perm_classical": 106, "perm_rbf_alt": 107}
B_SHOT = 20000
B_PERM = 5000
S_SHOTS = 1024
N = 24

_DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--package-root", default=str(_DEFAULT_ROOT))
ap.add_argument("--out", default=None)
ap.add_argument(
    "--check",
    action="store_true",
    help="compare regenerated values numerically with the persisted JSON without overwriting it",
)
ap.add_argument("--rtol", type=float, default=1e-12)
ap.add_argument("--atol", type=float, default=1e-12)
A = ap.parse_args()
P = Path(A.package_root)
OUTPUT_PATH = Path(A.out) if A.out else P / "hardware_analysis" / "zz4_wave1_revision_diagnostics.json"

Ksv = np.load(f"{P}/statevector_reference/zz4_K_all_all.npy")
KH = {r: np.load(f"{P}/hardware_kernels/zz4_{r}_kernel.npy") for r in ("H0", "H1", "H2")}
df = pd.read_csv(f"{P}/frozen_subset/hardware_subset_event_onset_next_1h.csv").sort_values("hardware_row_order")
y = np.where(df["y_event_onset_next_1h"].to_numpy() > 0, 1.0, -1.0)
assert int((y > 0).sum()) == 12 and int((y < 0).sum()) == 12
H = np.eye(N) - np.ones((N, N)) / N
Y = np.outer(y, y)
OFF = ~np.eye(N, dtype=bool)
REG = ("H0", "H1", "H2")
out = {"seeds": SEEDS, "B_shot": B_SHOT, "B_perm": B_PERM, "shots": S_SHOTS}

def cka_pair(A_, B_):
    Ac, Bc = H @ A_ @ H, H @ B_ @ H
    return float(np.sum(Ac * Bc) / (np.linalg.norm(Ac) * np.linalg.norm(Bc)))

def kta_c(K):  # centered KTA against frozen labels
    return cka_pair(K, Y)

def cka_gen(A_, B_):  # size-generic (for jackknife)
    n = A_.shape[0]; Hn = np.eye(n) - np.ones((n, n)) / n
    Ac, Bc = Hn @ A_ @ Hn, Hn @ B_ @ Hn
    return float(np.sum(Ac * Bc) / (np.linalg.norm(Ac) * np.linalg.norm(Bc)))

def kta_gen(K, yv):
    return cka_gen(K, np.outer(yv, yv))

def rmse_gen(A_, B_):
    n = A_.shape[0]; m = ~np.eye(n, dtype=bool)
    return float(np.sqrt(np.mean((A_ - B_)[m] ** 2)))

def cka_offdiag(A_, B_):
    Ac, Bc = (H @ A_ @ H)[OFF], (H @ B_ @ H)[OFF]
    return float(np.sum(Ac * Bc) / (np.linalg.norm(Ac) * np.linalg.norm(Bc)))

def hsic_u(K, L):  # HSIC_1 estimator (Song et al., 2012); n inferred (>=4)
    n = K.shape[0]
    Kt, Lt = K.copy(), L.copy()
    np.fill_diagonal(Kt, 0); np.fill_diagonal(Lt, 0)
    one = np.ones(n)
    t1 = float(np.sum(Kt * Lt))
    t2 = float(one @ Kt @ one) * float(one @ Lt @ one) / ((n - 1) * (n - 2))
    t3 = 2.0 / (n - 2) * float(one @ Kt @ Lt @ one)
    return (t1 + t2 - t3) / (n * (n - 3))

def cka_u(A_, B_):
    return hsic_u(A_, B_) / np.sqrt(hsic_u(A_, A_) * hsic_u(B_, B_))

# ---------- (0) reproduce headline values ----------
out["headline"] = {r: {"CKA": cka_pair(KH[r], Ksv), "KTAc": kta_c(KH[r]),
                       "RMSE": rmse_gen(KH[r], Ksv)} for r in REG}
out["headline"]["SV_KTAc"] = kta_c(Ksv)

# ---------- (i) diagonal-robust CKA ----------
dr = {}
for r in REG:
    Ku = KH[r].copy(); np.fill_diagonal(Ku, 1.0)
    dr[r] = {"cka_full": cka_pair(KH[r], Ksv), "cka_unit_diag": cka_pair(Ku, Ksv),
             "cka_offdiag_cos": cka_offdiag(KH[r], Ksv), "cka_u_centered_hsic1": cka_u(KH[r], Ksv)}
out["diag_robust_cka"] = dr

# ---------- (ii) numerator/denominator attribution ----------
num_sv, den_sv = float(y @ Ksv @ y), float(np.linalg.norm(H @ Ksv @ H))
att = {"SV": {"num": num_sv, "den": den_sv, "KTAc": num_sv / (den_sv * N)}}
for r in REG:
    numh, denh = float(y @ KH[r] @ y), float(np.linalg.norm(H @ KH[r] @ H))
    att[r] = {"num": numh, "den": denh, "num_pct": 100 * (numh / num_sv - 1),
              "den_pct": 100 * (denh / den_sv - 1), "KTAc": numh / (denh * N),
              "mixed_hwnum_svden": numh / (den_sv * N), "mixed_svnum_hwden": num_sv / (denh * N),
              "dKTA": numh / (denh * N) - num_sv / (den_sv * N)}
out["kta_attribution"] = att

# ---------- (iii) finite-shot resampling references ----------
IU = np.triu_indices(N, k=0)
def sample_kernel(rng, Kbase):
    p = np.clip(Kbase[IU], 0.0, 1.0)
    c = rng.binomial(S_SHOTS, p) / S_SHOTS
    M = np.zeros((N, N)); M[IU] = c
    return M + M.T - np.diag(np.diag(M))

rng = np.random.default_rng(SEEDS["shot_null_sv"])
kt_sv = kta_c(Ksv)
dk = np.empty(B_SHOT); ck = np.empty(B_SHOT); rm = np.empty(B_SHOT)
for b in range(B_SHOT):
    M = sample_kernel(rng, Ksv)
    dk[b] = kta_c(M) - kt_sv; ck[b] = cka_pair(M, Ksv); rm[b] = rmse_gen(M, Ksv)
sn = {"dKTA_mean": float(dk.mean()), "dKTA_sd": float(dk.std()),
      "dKTA_q025": float(np.quantile(dk, .025)), "dKTA_q975": float(np.quantile(dk, .975)),
      "dKTA_q995": float(np.quantile(dk, .995)), "dKTA_max": float(dk.max()),
      "CKA_mean": float(ck.mean()), "CKA_q025": float(np.quantile(ck, .025)),
      "RMSE_mean": float(rm.mean()), "RMSE_q975": float(np.quantile(rm, .975)),
      "RMSE_q99": float(np.quantile(rm, .99)), "RMSE_max": float(rm.max()), "p_ge_obs": {}}
for r in REG:
    obs = kta_c(KH[r]) - kt_sv
    sn["p_ge_obs"][r] = {"obs_dKTA": obs, "n_null_ge": int(np.sum(dk >= obs)),
                         "p_upper_add1": float((np.sum(dk >= obs) + 1) / (B_SHOT + 1))}
out["shot_null_sv"] = sn

rng = np.random.default_rng(SEEDS["shot_null_hw"])
rs = {}
for r in REG:
    vals = np.empty(B_SHOT)
    for b in range(B_SHOT):
        vals[b] = kta_c(sample_kernel(rng, KH[r]))
    obs = kta_c(KH[r]) - kt_sv
    rs[r] = {"KTAc_resample_sd": float(vals.std()), "uplift": obs,
             "uplift_over_sd": float(obs / vals.std())}
out["shot_resample_hw"] = rs

# ---------- (iv) label-permutation references ----------
rng = np.random.default_rng(SEEDS["perm_hw_sv"])
pm = {}
for name, K in [("SV", Ksv)] + [(r, KH[r]) for r in REG]:
    obs = kta_c(K); Ac = H @ K @ H; nA = np.linalg.norm(Ac)
    null = np.empty(B_PERM)
    for b in range(B_PERM):
        yp = rng.permutation(y); Yp = np.outer(yp, yp); Bc = H @ Yp @ H
        null[b] = np.sum(Ac * Bc) / (nA * np.linalg.norm(Bc))
    pm[name] = {"obs": obs, "null_mean": float(null.mean()), "null_sd": float(null.std()),
                "null_q95": float(np.quantile(null, .95)),
                "p_upper": float((np.sum(null >= obs) + 1) / (B_PERM + 1))}
out["label_perm"] = pm

rng = np.random.default_rng(SEEDS["perm_strat"])
tr = (df["hardware_split"] == "train").to_numpy(); te = ~tr
obs = kta_c(Ksv); Ac = H @ Ksv @ H; nA = np.linalg.norm(Ac)
null = np.empty(B_PERM)
for b in range(B_PERM):
    yp = y.copy(); yp[tr] = rng.permutation(y[tr]); yp[te] = rng.permutation(y[te])
    Yp = np.outer(yp, yp); Bc = H @ Yp @ H
    null[b] = np.sum(Ac * Bc) / (nA * np.linalg.norm(Bc))
out["label_perm_split_preserving_SV"] = {
    "obs": obs, "null_mean": float(null.mean()),
    "p_upper": float((np.sum(null >= obs) + 1) / (B_PERM + 1))}

# ---------- (v) classical comparators ----------
X = df[[f"scaled__F_quantum_4__{c}" for c in
        ("pm25_mean_last_1h", "pm10_mean_last_1h", "hcho_mean_last_1h", "tvoc_mean_last_1h")]].to_numpy()
Klin = X @ X.T
D2 = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2)
gamma = float(1.0 / np.median(D2[np.triu_indices(N, 1)]))
Krbf = np.exp(-gamma * D2)
rng = np.random.default_rng(SEEDS["perm_classical"])
cl = {"gamma_median_heuristic": gamma}
for name, K in (("linear", Klin), ("rbf", Krbf)):
    obs = kta_gen(K, y); Ac = H @ K @ H; nA = np.linalg.norm(Ac)
    null = np.empty(B_PERM)
    for b in range(B_PERM):
        yp = rng.permutation(y); Yp = np.outer(yp, yp); Bc = H @ Yp @ H
        null[b] = np.sum(Ac * Bc) / (nA * np.linalg.norm(Bc))
    cl[name] = {"KTAc": obs, "null_mean": float(null.mean()),
                "null_q95": float(np.quantile(null, .95)),
                "p_upper": float((np.sum(null >= obs) + 1) / (B_PERM + 1))}
gamma_alt = float(1.0 / (2.0 * np.median(D2[np.triu_indices(N, 1)])))
Kalt = np.exp(-gamma_alt * D2)
rng = np.random.default_rng(SEEDS["perm_rbf_alt"])
obs = kta_gen(Kalt, y); Ac = H @ Kalt @ H; nA = np.linalg.norm(Ac)
null = np.empty(B_PERM)
for b in range(B_PERM):
    yp = rng.permutation(y); Yp = np.outer(yp, yp); Bc = H @ Yp @ H
    null[b] = np.sum(Ac * Bc) / (nA * np.linalg.norm(Bc))
cl["rbf_alt"] = {"gamma": gamma_alt, "KTAc": obs, "null_mean": float(null.mean()),
                 "null_q95": float(np.quantile(null, .95)),
                 "p_upper": float((np.sum(null >= obs) + 1) / (B_PERM + 1))}
out["classical_comparators"] = cl

# ---------- (v-b) numerator trace / off-diagonal signed split ----------
spl = {}
for name, K in [("SV", Ksv)] + [(r, KH[r]) for r in REG]:
    tr = float(np.trace(K)); num = float(y @ K @ y)
    spl[name] = {"trace": tr, "offdiag_signed": num - tr}
out["kta_numerator_split"] = spl

# ---------- (vi) jackknives ----------
def jack(stat):
    reps = np.array([stat(np.delete(np.arange(N), l)) for l in range(N)])
    return reps, float(np.sqrt((N - 1) / N * np.sum((reps - reps.mean()) ** 2)))

jk = {"rmse": {}, "rmse_contrast": {}, "dKTA": {}, "cka_crosscheck": {}}
rmse_reps = {}
for r in REG:
    reps, se = jack(lambda idx, r=r: rmse_gen(KH[r][np.ix_(idx, idx)], Ksv[np.ix_(idx, idx)]))
    rmse_reps[r] = reps
    jk["rmse"][r] = {"point": rmse_gen(KH[r], Ksv), "se_jk": se}
for a, b_ in (("H1", "H0"), ("H2", "H1"), ("H2", "H0")):
    d = rmse_reps[a] - rmse_reps[b_]
    se = float(np.sqrt((N - 1) / N * np.sum((d - d.mean()) ** 2)))
    pt = rmse_gen(KH[a], Ksv) - rmse_gen(KH[b_], Ksv)
    jk["rmse_contrast"][f"{a}-{b_}"] = {"delta": pt, "se_jk": se, "z_desc": pt / se}
for r in REG:
    reps, se = jack(lambda idx, r=r: kta_gen(KH[r][np.ix_(idx, idx)], y[idx])
                    - kta_gen(Ksv[np.ix_(idx, idx)], y[idx]))
    pt = kta_c(KH[r]) - kt_sv
    jk["dKTA"][r] = {"point": pt, "se_jk": se, "z_desc": pt / se}
# cross-check: persisted CKA contrasts (Table 5: M2-M1 z=3.09, M2-M0 z=2.83)
cka_reps = {}
for r in REG:
    reps, se = jack(lambda idx, r=r: cka_gen(KH[r][np.ix_(idx, idx)], Ksv[np.ix_(idx, idx)]))
    cka_reps[r] = reps
    jk["cka_crosscheck"][r] = {"se_jk": se}
for a, b_ in (("H2", "H1"), ("H2", "H0")):
    d = cka_reps[a] - cka_reps[b_]
    se = float(np.sqrt((N - 1) / N * np.sum((d - d.mean()) ** 2)))
    pt = cka_pair(KH[a], Ksv) - cka_pair(KH[b_], Ksv)
    jk["cka_crosscheck"][f"{a}-{b_}_z"] = pt / se
# LOWO jackknife for the U-centered (diagonal-excluded) CKA
cka_u_reps = {}
jk["cka_u"] = {}
for r in REG:
    reps, se = jack(lambda idx, r=r: cka_u(KH[r][np.ix_(idx, idx)], Ksv[np.ix_(idx, idx)]))
    cka_u_reps[r] = reps
    jk["cka_u"][r] = {"point": cka_u(KH[r], Ksv), "se_jk": se}
for a, b_ in (("H1", "H0"), ("H2", "H1"), ("H2", "H0")):
    d = cka_u_reps[a] - cka_u_reps[b_]
    se = float(np.sqrt((N - 1) / N * np.sum((d - d.mean()) ** 2)))
    pt = cka_u(KH[a], Ksv) - cka_u(KH[b_], Ksv)
    jk["cka_u"][f"{a}-{b_}"] = {"delta": pt, "se_jk": se, "z_desc": pt / se}
out["jackknife"] = jk

# ---------- (vii) temporal ledger ----------
t = pd.to_datetime(df["window_end"])
ts = t.sort_values().reset_index(drop=True)
gaps = ts.diff().dropna().dt.total_seconds() / 60.0
close = [(str(ts[i]), str(ts[i + 1]), float(g)) for i, g in enumerate(gaps) if g < 60]
out["temporal"] = {"first": str(ts.iloc[0]), "last": str(ts.iloc[-1]),
                   "median_gap_min": float(gaps.median()), "min_gap_min": float(gaps.min()),
                   "n_gaps_lt_60min": int((gaps < 60).sum()), "pairs_lt_60min": close,
                   "per_day_counts": {str(k): int(v) for k, v in t.dt.date.value_counts().sort_index().items()}}
out["ledger_rows"] = [
    {"row": int(r.hardware_row_order), "window_end": str(r.window_end),
     "split": r.hardware_split, "label": int(r.y_event_onset_next_1h)}
    for r in df.itertuples()]

# ---------- (viii) statevector regeneration from frozen inputs ----------
Hg = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
H4 = np.kron(np.kron(Hg, Hg), np.kron(Hg, Hg))
Zd = []
for q in range(4):
    ops = [np.ones(2)] * 4; ops[q] = np.array([1.0, -1.0])
    d = ops[0]
    for o in ops[1:]:
        d = np.kron(d, o)
    Zd.append(d)
PAIRS = [(0, 1), (1, 2), (2, 3)]
def phi(x):
    psi = np.zeros(16, complex); psi[0] = 1.0
    for _ in range(2):
        psi = H4 @ psi
        ang = np.zeros(16)
        for q in range(4):
            ang += x[q] * Zd[q]
        for a, b_ in PAIRS:
            ang += (np.pi - x[a]) * (np.pi - x[b_]) * (Zd[a] * Zd[b_])
        psi = np.exp(-1j * ang) * psi
    return psi
states = [phi(X[i]) for i in range(N)]
Kre = np.abs(np.array([[np.vdot(a, b_) for b_ in states] for a in states])) ** 2
out["statevector_regeneration_max_abs_err"] = float(np.max(np.abs(Kre - Ksv)))

if A.check:
    if not OUTPUT_PATH.is_file():
        print(f"FAIL: reference JSON not found: {OUTPUT_PATH}", file=sys.stderr)
        sys.exit(2)

    expected = json.loads(OUTPUT_PATH.read_text())
    generated = json.loads(json.dumps(out))
    mismatches = []
    max_abs_diff = 0.0

    def compare(got, ref, path="$"):
        global max_abs_diff
        if isinstance(ref, dict):
            if not isinstance(got, dict):
                mismatches.append(f"{path}: expected object, got {type(got).__name__}")
                return
            if set(got) != set(ref):
                missing = sorted(set(ref) - set(got))
                extra = sorted(set(got) - set(ref))
                mismatches.append(f"{path}: key mismatch; missing={missing}, extra={extra}")
                return
            for key in ref:
                compare(got[key], ref[key], f"{path}.{key}")
            return
        if isinstance(ref, list):
            if not isinstance(got, list) or len(got) != len(ref):
                got_len = len(got) if isinstance(got, list) else "not-a-list"
                mismatches.append(f"{path}: list length mismatch; got={got_len}, expected={len(ref)}")
                return
            for idx, (got_item, ref_item) in enumerate(zip(got, ref)):
                compare(got_item, ref_item, f"{path}[{idx}]")
            return
        if isinstance(ref, bool) or isinstance(got, bool):
            if got != ref:
                mismatches.append(f"{path}: got={got!r}, expected={ref!r}")
            return
        if isinstance(ref, int) and isinstance(got, int):
            if got != ref:
                mismatches.append(f"{path}: got={got}, expected={ref}")
            return
        if isinstance(ref, (int, float)) and isinstance(got, (int, float)):
            diff = abs(float(got) - float(ref))
            max_abs_diff = max(max_abs_diff, diff)
            if not np.isclose(float(got), float(ref), rtol=A.rtol, atol=A.atol, equal_nan=True):
                mismatches.append(f"{path}: got={got!r}, expected={ref!r}, abs_diff={diff:.3e}")
            return
        if got != ref:
            mismatches.append(f"{path}: got={got!r}, expected={ref!r}")

    compare(generated, expected)
    if mismatches:
        print(f"FAIL: {len(mismatches)} mismatch(es); max numeric abs diff={max_abs_diff:.3e}")
        for item in mismatches[:20]:
            print(item)
        sys.exit(1)
    print(
        f"PASS: regenerated diagnostics match {OUTPUT_PATH} within "
        f"rtol={A.rtol:g}, atol={A.atol:g}; max numeric abs diff={max_abs_diff:.3e}"
    )
else:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in ("headline", "diag_robust_cka", "kta_attribution",
          "kta_numerator_split", "shot_null_sv", "shot_resample_hw", "label_perm",
          "label_perm_split_preserving_SV", "classical_comparators", "jackknife", "temporal",
          "statevector_regeneration_max_abs_err")}, indent=1, default=str))
