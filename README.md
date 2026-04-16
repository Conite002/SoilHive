# SoilHive

A soil data collection and analysis pipeline that aggregates open-source soil measurement databases into a unified dataset for exploratory analysis and machine learning research.

## Overview

SoilHive consolidates soil property observations from multiple global databases into a single structured dataset. The combined dataset contains over 2 million georeferenced measurements covering 24 soil properties across 56,000+ locations worldwide, spanning measurements from 1920 to 2015.

## Data Sources

| Source | Description |
|---|---|
| WoSIS | World Soil Information Service - primary source of physicochemical measurements (sole temporal coverage: 1920–2015) |
| CAROB | Harmonized crop and soil research data |
| iSDA Field Data | iSDA Africa field soil measurements |
| Global Soil Nematode DB | Nematode abundance by soil horizon |

## Dataset Schema

Each source file is loaded in long format (one row = one property measurement). The raw extracted files contain 15 columns:

| Column | Type | Description |
|---|---|---|
| `id` | int | Record identifier |
| `lat` / `lon` | float | Geographic coordinates |
| `property` | str | Soil property name (harmonised) |
| `original_name` | str | Property name as recorded in the source database |
| `upper_depth_cm` | float | Top of the sampling horizon (cm) |
| `lower_depth_cm` | float | Bottom of the sampling horizon (cm) |
| `value` | float | Measured value |
| `unit` | str | Unit of measurement (~20% missing, mainly nematode counts) |
| `sampling_date` | float | Year of soil sampling (~20% missing) |
| `license` | str | Data license (e.g., CC BY 4.0) |
| `h3_index` | str | Uber H3 spatial index at resolution 3 |
| `publication_date` | str | Date the record was published |
| `data_source` | str | Source database name |
| `source_file` | str | Name of the originating source folder |

A `country` column is added during EDA via a spatial join with Natural Earth boundaries.

## Soil Properties Covered

`sand`, `clay`, `silt`, `pH`, `N`, `occ` (organic carbon), `CaCO3`, `CEC`, `BD` (bulk density), `TC` (total carbon), `CF` (coarse fragments), `EC` (electrical conductivity), `P`, `K`, `Ca`, `Mg`, `Na`, `Al`, `Cu`, `Fe`, `Mn`, `WR_volumetric`, `WR_gravimetric`, `nematode`

## Dataset Statistics

- **Total observations:** 2,037,633
- **Unique locations:** 56,991
- **Soil properties:** 24 (73 original names harmonised)
- **Depth range:** 0 to 2,900 cm (mean layer thickness: 27 cm)
- **Temporal range:** 1920 to 2015 (peak: 1990s — 451,917 obs)
- **Sampling date coverage:** ~79.8% of records have a sampling date
- **Wide-format pivot** (one row per location, properties as columns): 45,241 rows × 18 columns

## Data Quality

| Issue | Detail |
|---|---|
| Missing `sampling_date` | ~20% overall; source-dependent |
| Missing `unit` | ~20% (mainly nematode records) |
| Functional duplicates | 1,138,087 rows (55.85%) — deduplicate before modelling |
| Spatial co-located replicates | 1,243,951 rows (61.05%) |
| Depth validity | 99.4% valid (upper < lower); 0.6% null depth |

## Key EDA Findings & ML Readiness

| Dimension | Finding | ML Implication |
|-----------|---------|----------------|
| **Format** | Long format, ~2M rows, 24 properties | Pivot to wide format before modelling; expect high sparsity |
| **Missing data** | `sampling_date` ~20% missing; `unit` ~20% | Temporal features unreliable; impute or drop |
| **Duplicates** | 55.85% functional duplicates | Deduplicate before train/test split to prevent leakage |
| **Depth** | Surface-biased (0–30 cm dominates) | Use `upper_depth_cm` as a feature; depth-stratified models recommended |
| **Distributions** | OC (`occ`), N, EC strongly right-skewed (skew > 4) | Log-transform skewed targets; robust scalers for features |
| **Texture** | Sand + clay + silt ≈ 100 constraint | Compositional data — use log-ratio transforms (e.g., Aitchison) |
| **Temporal** | Biased toward 1970s–80s; post-2000 only 18.7% | Models may not reflect current soil state; temporal reweighting advised |
| **Spatial** | Europe and North America dominant; Africa and tropics underrepresented | Spatial cross-validation required; regional bias correction needed |
| **Sources** | 4 sources with different property coverage and date completeness | Use `data_source` as a categorical feature; harmonise units before combining |

## Notebooks

### `01_eda.ipynb`
| Section | Topic |
|---------|-------|
| 1 | Dataset overview |
| 2 | Data quality analysis |
| 3 | Temporal analysis |
| 4 | Depth analysis |
| 5 | Distribution analysis (key soil variables) |
| 6 | Spatial analysis |

## Project Structure

```
SoilHive/
├── data/
│   ├── combined_output_data_points.csv   # Merged output (generated)
│   └── ...                               # Raw source CSV files
├── notebook/
│   ├── 01_eda.ipynb                  
│   └── 02_build_clean_dataset.ipynb             
│
└── README.md
```

## Dependencies

```
pandas
numpy
matplotlib
seaborn
scipy
geopandas
```
