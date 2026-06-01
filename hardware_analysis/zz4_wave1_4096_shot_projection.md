# ZZ4 Wave 1 optional 4096-shot projection

This artifact projects only the finite-shot reference scales from the executed 1024-shot Wave 1 run to the originally planned 4096-shot budget. It keeps the observed off-diagonal RMSE fixed and does not simulate a new hardware kernel.

Projection rules:

$$
\sigma_{\mathrm{ref,global}}(4096)=\frac{1}{\sqrt{2\cdot4096}},\qquad
\sigma_{\mathrm{shot,matrix},r}(4096)=\sigma_{\mathrm{shot,matrix},r}(1024)\sqrt{\frac{1024}{4096}}.
$$

| Regime | Manuscript config | Fixed RMSE | $\sigma_{\mathrm{ref,global}}(4096)$ | Global shot share | Global residual fraction | $\sigma_{\mathrm{shot,matrix}}(4096)$ | Matrix shot share | Matrix residual fraction | $R_{\mathrm{matrix}}(4096)$ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `H0` | `M0` | 0.087770 | 0.011049 | 1.58% | 98.42% | 0.004133 | 0.22% | 99.78% | 21.24 |
| `H1` | `M1` | 0.086428 | 0.011049 | 1.63% | 98.37% | 0.004122 | 0.23% | 99.77% | 20.97 |
| `H2` | `M2` | 0.042727 | 0.011049 | 6.69% | 93.31% | 0.004264 | 1.00% | 99.00% | 10.02 |

The projected 4096-shot matrix-aware finite-shot share remains at or below 1% for every regime. Under the conservative global reference it remains below 7% for every regime. The projection therefore leaves residual hardware distortion as the dominant squared-RMSE component under the fixed-RMSE assumption.

This is a deterministic precision-budget calculation, not a hardware-noise model and not evidence for a realized 4096-shot rerun.
