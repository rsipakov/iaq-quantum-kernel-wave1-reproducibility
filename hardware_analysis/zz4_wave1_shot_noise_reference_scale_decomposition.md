# ZZ4 Wave 1 shot-noise reference-scale decomposition

- Shots per circuit: `1024`
- Global reference scale: `1/sqrt(2*S) = 0.022097086912`
- Matrix reference scale: `sqrt(mean(p_ij*(1-p_ij)/S))` over off-diagonal entries.
- Interpretation: diagnostic quadrature bookkeeping only; not a physical noise-model decomposition.

| Configuration | Regime | RMSE | sigma_global | residual_global | ShotShare_global | sigma_matrix | residual_matrix | ShotShare_matrix |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `M0` | `H0` | 0.087770 | 0.022097 | 0.084943 | 6.34% | 0.008266 | 0.087380 | 0.89% |
| `M1` | `H1` | 0.086428 | 0.022097 | 0.083555 | 6.54% | 0.008243 | 0.086034 | 0.91% |
| `M2` | `H2` | 0.042727 | 0.022097 | 0.036570 | 26.75% | 0.008528 | 0.041868 | 3.98% |

The matrix-aware scale is computed from reconstructed hardware all-zero probabilities. Under this plug-in calculation, finite-shot variance accounts for less than 1% of the off-diagonal RMSE variance in `M0/H0` and `M1/H1`, and about 4% in `M2/H2`.
