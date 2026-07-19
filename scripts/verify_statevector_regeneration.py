#!/usr/bin/env python3
"""Verify that the statevector reference kernel regenerates from the frozen subset.

Regenerates the ZZ4 statevector kernel K_SV(i,j) = |<phi(x_i)|phi(x_j)>|^2 from the
public frozen-subset table alone (columns scaled__F_quantum_4__*), using a pure-NumPy
implementation of the manuscript Section 2.3 feature map: Qiskit ZZFeatureMap
convention, 4 qubits, linear entanglement pairs (0,1),(1,2),(2,3), two repetitions,
first-order angles phi_k = x_k and second-order angles phi_ab = (pi - x_a)(pi - x_b),
with the phase applied as exp(-i * sum phi_S Z_S) per repetition after a Hadamard
layer. The result is compared entrywise against the released artifact
statevector_reference/zz4_K_all_all.npy.

Exit code 0 if the maximum absolute deviation is below 1e-12 (expected ~4e-15).

Usage: python3 scripts/verify_statevector_regeneration.py [--package-root PATH]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--package-root", default=str(Path(__file__).resolve().parents[1]))
A = ap.parse_args()
P = Path(A.package_root)

df = pd.read_csv(P / "frozen_subset" / "hardware_subset_event_onset_next_1h.csv")
df = df.sort_values("hardware_row_order")
X = df[[f"scaled__F_quantum_4__{c}" for c in
        ("pm25_mean_last_1h", "pm10_mean_last_1h", "hcho_mean_last_1h", "tvoc_mean_last_1h")]].to_numpy()
Ksv = np.load(P / "statevector_reference" / "zz4_K_all_all.npy")
N = X.shape[0]

Hg = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
H4 = np.kron(np.kron(Hg, Hg), np.kron(Hg, Hg))
Zd = []
for q in range(4):
    ops = [np.ones(2)] * 4
    ops[q] = np.array([1.0, -1.0])
    d = ops[0]
    for o in ops[1:]:
        d = np.kron(d, o)
    Zd.append(d)
PAIRS = [(0, 1), (1, 2), (2, 3)]


def phi(x):
    psi = np.zeros(16, complex)
    psi[0] = 1.0
    for _ in range(2):
        psi = H4 @ psi
        ang = np.zeros(16)
        for q in range(4):
            ang += x[q] * Zd[q]
        for a, b in PAIRS:
            ang += (np.pi - x[a]) * (np.pi - x[b]) * (Zd[a] * Zd[b])
        psi = np.exp(-1j * ang) * psi
    return psi


states = [phi(X[i]) for i in range(N)]
Kre = np.abs(np.array([[np.vdot(a, b) for b in states] for a in states])) ** 2
err = float(np.max(np.abs(Kre - Ksv)))
print(f"statevector regeneration: N={N}, max |K_regenerated - K_artifact| = {err:.3e}")
ok = err < 1e-12
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
