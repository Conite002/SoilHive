# NB07 — Country Export Report

**Date**: 2026-03-19
**Notebook**: `notebook/NB07_country_export.ipynb`
**Status**: COMPLETED — no errors

---

## 1. Output Structure

```
data/output/
  {iso3}/
    {iso3}_soil_observed.csv      ← WoSIS observations only
    {iso3}_soil_soilgrid_only.csv ← SoilGrids raster values (scaled to WoSIS units)
    {iso3}_soil_unified.csv       ← Observed priority + SoilGrids fallback + _src flags
```

Total: **69 files** across 23 countries  |  **28.8 MB**

---

## 2. Per-Country Export Summary

- **Obs%** = % of (station × property) cells filled from WoSIS observations
- **SG%** = % of cells filled from SoilGrids fallback
- **Miss%** = % of cells still NaN (neither observed nor raster available)

| iso3   | country              |   n_total_stations |   n_observed_stations |   n_sg_stations |   pct_obs_cells |   pct_sg_cells |   pct_missing_cells |   obs_csv_kb |   sg_csv_kb |   unified_csv_kb |
|:-------|:---------------------|-------------------:|----------------------:|----------------:|----------------:|---------------:|--------------------:|-------------:|------------:|-----------------:|
| AGO    | Angola               |               1571 |                  1571 |            1568 |            38.1 |           21.8 |                40.1 |        260   |       179.1 |            584.8 |
| ALB    | Albania              |                 67 |                    67 |              63 |            33.8 |           17.7 |                48.6 |          9.6 |         8.3 |             23.4 |
| AUS    | Australia            |              33748 |                 33748 |           33094 |            17   |           31.3 |                51.7 |       4634.4 |      4129.1 |          11592.4 |
| BDI    | Burundi              |                 28 |                    28 |              27 |            35.9 |           13.1 |                51   |          4.1 |         3.2 |              9.9 |
| BEN    | Benin                |                716 |                   716 |             707 |            32.7 |           16.4 |                51   |         90   |        77.7 |            235.4 |
| BFA    | Burkina Faso         |               1671 |                  1671 |            1669 |            22.8 |           26.7 |                50.5 |        239.2 |       216.6 |            582.6 |
| BWA    | Botswana             |               1253 |                  1253 |            1230 |            35.4 |           24.5 |                40.1 |        186.2 |       143.9 |            446.2 |
| CAF    | Central African Rep. |                 80 |                    80 |              80 |            34.2 |           15.9 |                49.9 |         13.4 |        10.2 |             29.8 |
| CMR    | Cameroon             |               1323 |                  1323 |            1310 |            29.5 |           21.4 |                49.1 |        203.2 |       165.8 |            473.9 |
| DEU    | Germany              |               2873 |                  2873 |            2759 |            10.1 |           34.8 |                55.1 |        395.8 |       379.8 |            988.4 |
| DZA    | Algeria              |                 10 |                    10 |              10 |            27.9 |           21.7 |                50.4 |          1.8 |         1.3 |              4   |
| EST    | Estonia              |                202 |                   202 |             201 |            17.5 |           33.5 |                49   |         27.5 |        25.6 |             69.6 |
| FRA    | France               |               2962 |                  2962 |            2873 |            27   |           24.7 |                48.3 |        426.2 |       382.6 |           1034.9 |
| GEO    | Georgia              |                 18 |                    18 |              17 |            34.7 |           16.7 |                48.6 |          3   |         2.4 |              6.8 |
| GRC    | Greece               |                305 |                   305 |             296 |            12.4 |           35.9 |                51.6 |         41.8 |        39.3 |            105.3 |
| HRV    | Croatia              |                 79 |                    79 |              78 |            11.9 |           37.4 |                50.6 |         11.1 |        10.6 |             27.7 |
| MAR    | Morocco              |                114 |                   114 |             109 |            22.4 |           25.6 |                52   |         15.8 |        14.1 |             39.4 |
| MDA    | Moldova              |                 35 |                    35 |              33 |            27.5 |           19.4 |                53.1 |          5   |         4.3 |             12.3 |
| MNE    | Montenegro           |                 24 |                    24 |              24 |             8.9 |           41.1 |                50   |          3.4 |         3.2 |              8.6 |
| NLD    | Netherlands          |               1287 |                  1287 |            1229 |            13.5 |           33.3 |                53.2 |        178.2 |       163.4 |            443.9 |
| PNG    | Papua New Guinea     |                 16 |                    16 |              16 |            34.4 |           18.5 |                47.1 |          3   |         2.3 |              6.5 |
| TCD    | Chad                 |                 13 |                    13 |              13 |            33.3 |           18.3 |                48.4 |          2.2 |         1.7 |              5   |
| TUN    | Tunisia              |                 40 |                    40 |              35 |            36.1 |           13.1 |                50.7 |          6.8 |         5.1 |             15.1 |

---

## 3. Column Dictionary

### Observed-only CSV
| Column | Description | Unit |
|--------|-------------|------|
| station_id | Unique station identifier | — |
| lat / lon | WGS84 coordinates | degrees |
| iso3 | ISO 3166-1 alpha-3 country code | — |
| country | Country name | — |
| QC_FLAG | Coordinate quality flag (VALID, NEAR_BORDER, OVERSEAS_TERRITORY) | — |
| BD | Bulk density (observed) | g/cm³ |
| CEC | Cation exchange capacity | cmol(c)/kg |
| CF | Coarse fragments | % |
| clay / sand / silt | Particle size fractions | g/kg |
| N | Total nitrogen | g/kg |
| occ | Organic carbon content | g/kg |
| pH | Soil pH (H2O) | — |
| WR_volumetric | Volumetric water retention (0.01 bar) | % |
| WR_gravimetric | Gravimetric water retention (15 bar) | % |
| EC | Electrical conductivity | dS/m |
| CaCO3 | Calcium carbonate | g/kg |
| P | Available phosphorus | mg/kg |
| TC | Total carbon | g/kg |
| Al, Ca, Cu, Fe, K, Mg, Mn, Na | Extractable elements | cmol(c)/kg or mg/kg |
| nematode | Nematode count | count/g |

### SoilGrids-only CSV
Same metadata columns. Property columns are SoilGrids 250m values **scaled to WoSIS units** (WR × 100).
Extra: `sg_occ_ocd` (organic carbon density, g/dm³), `sg_WR_volumetric2` (0.33 bar, cm³/cm³).

### Unified CSV
Same property columns as observed. Each property has a companion `{prop}_src` column:
- `observed` — value from WoSIS measurement
- `soilgrids` — value from SoilGrids 250m raster (scaled)
- `missing` — no data available

---

## 4. Pipeline Complete

```
NB01 — Data Audit & Country Mapping      ✓
NB02 — Surface Extraction (WoSIS → wide) ✓  53,708 stations × 29 properties
NB03 — Coordinate Validation & QC        ✓  48,435 USABLE (90.2%)
NB04 — SoilGrids Raster Extraction       ✓  48,435 stations × 13 SG layers
NB05 — Integration (observed + fallback) ✓  WR unit fix (×100), source flags
NB06 — Validation                        ✓  All STOP checks passed
NB07 — Country Export                    ✓  69 CSV files
```
