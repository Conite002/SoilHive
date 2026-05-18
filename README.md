# SoilHive

A geospatial soil data pipeline that aggregates open-source soil measurement databases,
builds a clean surface soil dataset, and integrates it with crop yield observations to
produce an ML-ready Soil × Yield dataset for yield prediction and fertilizer recommendation.

---

## Project Objectives

- Consolidate heterogeneous soil observations from 4 global databases into a single long-format dataset
- Apply depth-aware aggregation restricted to the 0–30 cm surface layer
- Produce a clean, wide-format global soil dataset after temporal and spatial deduplication
- Spatially join the soil dataset with GYGA crop yield observations
- Output a combined Soil × Yield dataset ready for supervised ML

---

## Data Sources

| Source | Records | Description |
|---|---|---|
| WoSIS | 1,872,802 | World Soil Information Service — primary physicochemical measurements (1920–2015) |
| iSDA Field Data | 122,572 | iSDA Africa field soil measurements |
| Global Soil Nematode DB | 25,158 | Nematode abundance by soil horizon |
| CAROB | 17,101 | Harmonized crop and soil research data |
| **GYGA** | 56,516 | Global Yield Gap Atlas — crop yield observations at research stations |

**Note on source folders:** `data/csv_country/` and `data/extracted/` contain the same 77 files
with identical content (1,971,722 rows each). The pipeline uses `extracted/` as the single
canonical source; `csv_country/` is a redundant copy.

---

## Soil Properties

24 harmonised properties across 73 original field names:

| Category | Properties |
|---|---|
| Texture | `sand`, `clay`, `silt` |
| Chemistry | `pH`, `N`, `occ` (organic C), `TC`, `CaCO3`, `CEC`, `EC`, `P` |
| Cations | `K`, `Ca`, `Mg`, `Na`, `Al`, `Cu`, `Fe`, `Mn` |
| Physical | `BD` (bulk density), `CF` (coarse fragments), `WR_gravimetric`, `WR_volumetric` |
| Biology | `nematode` |

---

## Pipeline — `02_build_clean_dataset.ipynb`

| Step | Description | Output |
|---|---|---|
| 1. Load | Concatenate all 77 `output_data_points.csv` from `extracted/` | 1,971,722 rows, long format |
| 2. Clean | Drop null coordinates/values; depth consistency check; drop exact duplicates | ~2,024,191 rows |
| 3. Surface filter | Keep layers that intersect 0–30 cm; compute overlap weight | Rows with `overlap_weight > 0` |
| 4. Depth-weighted agg | Average values weighted by layer overlap within 0–30 cm, per (lat, lon, property, date) | 200,877 rows |
| 5. Temporal filter | Retain records with `sampling_date >= 2000` | Subset with known modern dates |
| 6. Spatial agg | Aggregate multiple observations per (lat, lon, property) — mean, std, count | 52,714 rows |
| 7. Pivot wide | One row per location; properties as columns | 10,662 rows x 17 columns |
| 8. Uncertainty | Add `{property}_std` and `{property}_n` columns | 47 columns |
| 9. Add country | Spatial join with Natural Earth boundaries | 10,432 rows (230 offshore dropped) |
| 10. Global export | Drop columns > 70% missing; impute remainder with global median | `soil_clean_global.csv` |
| 11. Per-country export | Adaptive threshold cleaning per country | `clean_by_country/` |
| 12. Soil x Yield join | cKDTree spatial join (1 degree radius, k=5) with GYGA yield data | `soil_x_yield_combined.csv` |

---

## Output Datasets

### `data/soil_clean_global.csv`

Global soil dataset in wide format after full pipeline cleaning.

- **Countries:** 15 (Australia, France, Germany, Netherlands, Switzerland, Cameroon,
  Burkina Faso, Albania, Georgia, Belgium, Benin, Italy, Luxembourg, Tunisia, Spain)
- **Columns:** soil features + `{feature}_std` + `{feature}_n` + `country`
- **Missing strategy:** columns > 70% missing dropped; remainder imputed with global median

### `data/clean_by_country/`

Per-country wide-format CSVs with adaptive threshold cleaning and median imputation.
Currently produced for: Australia, France, Germany, Netherlands.

### `data/soil_x_yield_combined.csv`

Spatially joined Soil x Yield dataset. One row = one crop x station x year observation
enriched with mean topsoil properties from the nearest SoilHive soil points.

**Join method:** `scipy.spatial.cKDTree` — for each GYGA station with valid coordinates,
finds up to 5 nearest soil points within 1 degree (~110 km) and averages their soil features.

**Coverage note:** The temporal filter (`sampling_date >= 2000`) limits soil coverage to
15 countries. Yield stations outside that geographic footprint are excluded from the combined
dataset.

| Column group | Columns |
|---|---|
| Yield targets | `YA`, `YW`, `YP`, `YG`, `log_YA`, `yield_gap_pct` |
| Soil features | Available subset from `soil_clean_global` |
| Metadata | `STATIONNAME`, `COUNTRY`, `LATITUDE`, `LONGITUDE`, `ELEVATION_METER`, `HARVESTYEAR`, `CROP`, `crop_clean` |
| Join QA | `n_soil_samples`, `min_dist_deg` |

---

## Raw Dataset Statistics

| Metric | Value |
|---|---|
| Total raw observations | 1,971,722 |
| Unique locations | 56,991 |
| Soil properties | 24 harmonised (73 original names) |
| Depth range | 0–2,900 cm |
| Temporal range | 1920–2015 |
| Records with sampling date | ~79.8% |
| Source folders | `csv_country/` and `extracted/` are exact duplicates — use one only |

---

## Data Quality Notes

| Issue | Detail |
|---|---|
| Duplicate source folders | `csv_country/` = `extracted/` — identical byte-for-byte; pipeline uses `extracted/` |
| Missing `sampling_date` | ~20% of raw records; WoSIS-dominant |
| Temporal filter impact | Only records with `sampling_date >= 2000` are retained — major row reduction |
| Post-pipeline sparsity | Most locations have only a subset of the 24 properties |
| Spatial imbalance | Australia (~77% of clean rows) and Western Europe dominate post-2000 |
| Skewed distributions | `occ`, `N`, `EC`, `Al` strongly right-skewed (skew > 4) |
| Texture constraint | sand + clay + silt ~= 100 — treat as compositional data |

---

## Project Structure

```
SoilHive/
├── data/
│   ├── extracted/                        # 77 source folders (canonical source)
│   │   └── {id}/output_data_points.csv
│   ├── csv_country/                      # Identical copy of extracted/ — redundant
│   ├── clean_by_country/                 # Per-country cleaned CSVs (4 countries)
│   ├── global_yield_clean.csv            # GYGA yield observations (56,516 rows)
│   ├── soil_clean_global.csv             # Global clean soil dataset (generated)
│   └── soil_x_yield_combined.csv         # Soil x Yield joined dataset (generated)
│
├── notebook/
│   ├── 01_eda.ipynb                      # Exploratory analysis of raw soil data
│   └── 02_build_clean_dataset.ipynb      # Full pipeline: cleaning -> join -> export
│
├── reports/
│   └── report_01.md
│
└── README.md
```

---

## ML Preprocessing Notes

**Log-transform** (right-skewed features): `occ`, `N`, `EC`, `Al`, `Fe`, `Mn`, `Cu`, `CEC`, `P`

**Standard scaling:** all continuous soil and coordinate features after log-transform

**Targets:**
- Regression: `log_YA` — back-transform predictions with `expm1()`
- Gap classification: bin `yield_gap_pct` into low / medium / high tertiles

**Categorical encoding:** `COUNTRY`, `crop_clean` — target encoding or one-hot

**Spatial cross-validation:** required — random splits overestimate generalization due to
spatial autocorrelation in both soil and yield observations

**Data leakage:** `YW`, `YP`, `YG` are yield-gap components — exclude from predictor set,
use only as targets

---

## Dependencies

```
pandas
numpy
scipy
matplotlib
seaborn
geopandas
scikit-learn
```
