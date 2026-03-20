# NB06 — Validation Report

**Date**: 2026-03-19
**Notebook**: `notebook/NB06_validation.ipynb`
**Status**: COMPLETED — no errors

---

## 1. STOP Check

PASSED — no stop conditions triggered.

---

## 2. Distribution Comparison (Observed vs SoilGrids, after unit scaling)

For each property: percentiles of observed values vs SoilGrids raster values scaled to WoSIS units.
`median_ratio` = median(observed) / median(SoilGrids_scaled). Values near 1.0 = unit alignment.
ERROR threshold: ratio outside [0.1, 10.0].
WARN threshold: ratio outside [0.4, 2.5] (geographic bias zone).

| property       |   n_obs |   n_sg |   p5_obs |   p50_obs |   p95_obs |   p5_sg |   p50_sg |   p95_sg |   median_ratio | flag                  |
|:---------------|--------:|-------:|---------:|----------:|----------:|--------:|---------:|---------:|---------------:|:----------------------|
| BD             |     445 |  47153 |    0.483 |     1.41  |     1.798 |    0.98 |     1.21 |    1.49  |          1.165 | OK                    |
| CEC            |   11999 |  47192 |    2.1   |    11     |    47.2   |    9.9  |    22.8  |   33.645 |          0.482 | OK                    |
| CF             |    9166 |  47194 |    0     |     2.073 |    40     |    3.3  |     9.4  |   16.3   |          0.221 | WARN: geographic bias |
| clay           |   26561 |  47194 |    3.1   |    20     |    58     |    7.4  |    20    |   44.4   |          1     | OK                    |
| N              |   15694 |  47194 |    0.216 |     0.9   |     4.114 |    0.56 |     2.08 |    6.323 |          0.433 | OK                    |
| occ            |   29402 |  47158 |    3.18  |    14.413 |    66.627 |    7.6  |    33    |   85.6   |          0.437 | OK                    |
| pH             |   39314 |  47192 |    4     |     5.6   |     8.215 |    4.9  |     6.2  |    7.745 |          0.903 | OK                    |
| sand           |   10252 |  47194 |    7.6   |    50.718 |    92     |   23.5  |    59.4  |   86.8   |          0.854 | OK                    |
| silt           |   25939 |  47194 |    2.5   |    16.5   |    54.1   |    4.5  |    16.2  |   47.9   |          1.019 | OK                    |
| WR_volumetric  |     429 |  47193 |   11.1   |    30     |    49     |   29.5  |    36.8  |   46.8   |          0.815 | OK                    |
| WR_gravimetric |    4765 |  47192 |    3.4   |    19.07  |    50.988 |    6.4  |    11.9  |   20.7   |          1.603 | OK                    |

### Geographic Bias Warnings

- CF: ratio=0.221 — likely geographic bias (Africa/Australia sampling)

**Note on CEC, N, CF, occ divergence**: The observed dataset is dominated by African stations
(Burkina Faso, Angola, Cameroon, Benin) and Australia, which systematically show lower CEC, N, and
organic carbon than the global SoilGrids prediction surface. This is a real geographic effect,
not a unit mismatch. SoilGrids values for these properties are valid as fallback — they are in
the correct units. Users should be aware that for properties with low observed coverage
(especially BD and WR_*), the SoilGrids fallback may overestimate true values in African sites.

---

## 3. KS Test Results (Observed vs scaled SoilGrids)

Two-sample Kolmogorov–Smirnov test. D ∈ [0,1]: 0 = identical, 1 = maximally different.
ERROR: D > 0.8. WARN: D > 0.3 (geographic divergence).
Min N = 100. Focus on D-statistic, not p-value (p is inflated by large N).

| property       |   n_obs |   n_sg |   ks_d |   ks_p | flag                        |
|:---------------|--------:|-------:|-------:|-------:|:----------------------------|
| BD             |     445 |  47153 | 0.3931 |      0 | WARN: geographic divergence |
| CEC            |   11999 |  47192 | 0.4304 |      0 | WARN: geographic divergence |
| CF             |    9166 |  47194 | 0.5077 |      0 | WARN: geographic divergence |
| clay           |   26561 |  47194 | 0.1182 |      0 | OK                          |
| N              |   15694 |  47194 | 0.4017 |      0 | WARN: geographic divergence |
| occ            |   29402 |  47158 | 0.3475 |      0 | WARN: geographic divergence |
| pH             |   39314 |  47192 | 0.3039 |      0 | WARN: geographic divergence |
| sand           |   10252 |  47194 | 0.1785 |      0 | OK                          |
| silt           |   25939 |  47194 | 0.0611 |      0 | OK                          |
| WR_volumetric  |     429 |  47193 | 0.4808 |      0 | WARN: geographic divergence |
| WR_gravimetric |    4765 |  47192 | 0.4176 |      0 | WARN: geographic divergence |

---

## 4. Coverage Audit

### 4.1 Per-country summary (min/mean coverage across SG-backed properties)

| iso3   |   n_stations |   min_coverage |   mean_coverage |
|:-------|-------------:|---------------:|----------------:|
| AGO    |         1571 |           99.6 |            99.9 |
| ALB    |           67 |           91   |            97.8 |
| AUS    |        33748 |           97.6 |            98.2 |
| BDI    |           28 |           96.4 |            99.7 |
| BEN    |          716 |           98.3 |            99.1 |
| BFA    |         1671 |           99.8 |            99.9 |
| BWA    |         1253 |           98.2 |            99.2 |
| CAF    |           80 |          100   |           100   |
| CMR    |         1323 |           98.1 |            99.4 |
| DEU    |         2873 |           94.4 |            95.6 |
| DZA    |           10 |           90   |            96.4 |
| EST    |          202 |           99.5 |            99.9 |
| FRA    |         2962 |           96   |            97.5 |
| GEO    |           18 |           94.4 |            98   |
| GRC    |          305 |           94.8 |            96.7 |
| HRV    |           79 |           97.5 |            98.5 |
| MAR    |          114 |           93.9 |            95.5 |
| MDA    |           35 |           91.4 |            96.6 |
| MNE    |           24 |          100   |           100   |
| NLD    |         1287 |           94.6 |            96.3 |
| PNG    |           16 |          100   |           100   |
| TCD    |           13 |          100   |           100   |
| TUN    |           40 |           87.5 |            93.6 |

### 4.2 Coverage warnings (< 80.0%)

None — all countries meet the coverage threshold.

---

## 5. Next Step

→ **NB07 — Country Export Engine**
Generate 3 CSV variants per country:
- `{iso3}_soil_observed.csv` — WoSIS observed values only
- `{iso3}_soil_soilgrid_only.csv` — SoilGrids raster values only
- `{iso3}_soil_unified.csv` — Observed priority + SoilGrids fallback (the integration output)
