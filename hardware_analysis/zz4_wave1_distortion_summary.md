# ZZ4 Wave 1 Hardware Distortion Summary

- Created UTC: 2026-05-30T20:54:59Z
- Mode: budget-safe H0/H1/H2, 1024 shots per circuit
- All required regimes reported: `True`
- Regimes reported: `H0, H1, H2`

## Key metrics

| regime_id   |   offdiag_spearman_vs_statevector |   offdiag_pearson_vs_statevector |   kernel_mae |   kernel_rmse |   KTA_hardware |   KTA_statevector |   CKA_hardware_vs_statevector |   effective_rank_hardware |   min_eigenvalue_before_psd |   psd_correction_frobenius_relative |
|:------------|----------------------------------:|---------------------------------:|-------------:|--------------:|---------------:|------------------:|------------------------------:|--------------------------:|----------------------------:|------------------------------------:|
| H0          |                          0.741297 |                         0.827253 |    0.0490359 |     0.0877705 |       0.183308 |          0.158511 |                      0.933391 |                   21.1842 |                    0.428763 |                         1.48762e-15 |
| H1          |                          0.774951 |                         0.842774 |    0.0472895 |     0.0864275 |       0.181463 |          0.158511 |                      0.937373 |                   21.217  |                    0.462156 |                         1.39114e-15 |
| H2          |                          0.943744 |                         0.986203 |    0.0257256 |     0.0427274 |       0.171025 |          0.158511 |                      0.988668 |                   19.7882 |                    0.232164 |                         1.51424e-15 |

## Interpretation discipline

These results support only a hardware kernel-survival / distortion discussion.
They do not support a quantum advantage claim, a hardware classifier-superiority claim, or any RMA hardware-readiness claim.
