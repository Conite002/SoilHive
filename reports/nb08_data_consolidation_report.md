# NB08 — SoilHive Data Consolidation Report

**Notebook:** `08_data_consolidation.ipynb`
**Date:** 2026-03-18
**Author:** SoilHive Data Pipeline

---

## 1. Objectives

Notebook 08 consolidates two independent soil data sources into a single analysis-ready dataset:

1. **WoSIS** (World Soil Information Service) — in-situ soil point measurements downloaded via the SoilHive scraping pipeline.
2. **SoilGrids 250m** — global soil property predictions at 250 m resolution extracted at each WoSIS station coordinate.

The merge strategy uses **surface measurements only**: WoSIS observations with `upper_depth_cm ≤ 10 cm`, matched to SoilGrids `0–5 cm` mean layers.

---

## 2. Data Sources

### 2.1 WoSIS Observations

| Item | Value |
|------|-------|
| Source | `output_data_points.csv` per country folder |
| Coverage | 55 countries |
| Raw records (all depths) | ~864,228 |
| Surface records (≤10 cm) | 42,298 |
| Properties available | 16 soil variables |

WoSIS soil variables included:

| Variable | Description | Coverage |
|----------|-------------|----------|
| `pH` | Soil pH | 72.9% |
| `clay` | Clay content (%) | 83.0% |
| `sand` | Sand content (%) | 55.3% |
| `silt` | Silt content (%) | 62.3% |
| `CaCO3` | Calcium carbonate (%) | 56.6% |
| `TC` | Total carbon (g/kg) | 19.4% |
| `occ` | Organic carbon content | 34.3% |
| `CEC` | Cation exchange capacity | 13.5% |
| `N` | Total nitrogen | 9.6% |
| `P` | Phosphorus | 7.8% |
| `BD` | Bulk density | 7.5% |
| `EC` | Electrical conductivity | 20.5% |
| `CF` | Coarse fragments | 23.6% |
| `WR_gravimetric` | Gravimetric water retention | 0.8% |
| `WR_volumetric` | Volumetric water retention | 0.4% |
| `nematode` | Nematode count | 2.3% |

### 2.2 SoilGrids 250m

| Item | Value |
|------|-------|
| Source | `SoilGrids_250m/*.tif` per country folder |
| Depth layer | 0–5 cm (surface) |
| Extraction method | `rasterio.sample()` — windowed reads, no full raster load |
| Script | `script/extract_soilgrids_surface.py` |
| Cache | `data/_sg_cache/{country}.parquet` |
| Final file | `data/soilgrids_surface_all_countries.parquet` |
| Shape | 42,563 × 16 |

SoilGrids properties and unit conversions applied:

| Property | Raw unit | Final unit | Divisor |
|----------|----------|------------|---------|
| `sg_bdod` | cg/cm³ | g/cm³ | 100 |
| `sg_cec` | mmol/kg | cmolc/kg | 10 |
| `sg_cfvo` | cm³/dm³ | % | 10 |
| `sg_clay` | g/kg | % | 10 |
| `sg_nitrogen` | cg/kg | g/kg | 100 |
| `sg_ocd` | — | — | 10 |
| `sg_phh2o` | pH × 10 | pH | 10 |
| `sg_sand` | g/kg | % | 10 |
| `sg_silt` | g/kg | % | 10 |
| `sg_soc` | dg/kg | g/kg | 10 |
| `sg_wv0010` | — | — | 10 |
| `sg_wv0033` | — | — | 10 |
| `sg_wv1500` | — | — | 10 |

---

## 3. Final Consolidated Dataset

**File:** `data/combined_soilhive_dataset.parquet`
**Shape:** 42,298 rows × 32 columns
**Columns:** `country`, `lat`, `lon` + 16 WoSIS properties + 13 SoilGrids properties

### 3.1 Country Coverage

55 countries represented. Top 15 by station count:

| Country | Stations |
|---------|----------|
| Switzerland | 10,429 |
| Mexico | 7,446 |
| Belgium | 6,962 |
| French_Guiana | 3,122 |
| United_Kingdom | 1,455 |
| Hungary | 1,370 |
| Bonaire, Sint Eustatius and Saba | 1,300 |
| Spain | 829 |
| Canary_Islands | 829 |
| Poland | 672 |
| Czechia | 638 |
| Sweden | 596 |
| Costa_Rica | 542 |
| Italy | 500 |
| Ukraine | 460 |

The three countries added in the last extraction run:
- **Canary_Islands**: 829 stations (835/846 with SoilGrids data)
- **Thailand_North**: 367 stations (351/378 with SoilGrids data)
- **Bangladesh**: 200 stations (187/200 with SoilGrids data)

### 3.2 SoilGrids Coverage

| Property | Stations with data | Coverage |
|----------|--------------------|----------|
| `sg_bdod` | 39,427 | 93.2% |
| `sg_cec` | 39,435 | 93.2% |
| `sg_cfvo` | 39,085 | 92.4% |
| `sg_clay` | 31,342 | 74.1% |
| `sg_nitrogen` | 31,340 | 74.1% |
| `sg_ocd` | 31,301 | 74.0% |
| `sg_phh2o` | 31,339 | 74.1% |
| `sg_sand` | 31,340 | 74.1% |
| `sg_silt` | 31,252 | 73.9% |
| `sg_soc` | 31,251 | 73.9% |
| `sg_wv0010` | 31,252 | 73.9% |
| `sg_wv0033` | 31,253 | 73.9% |
| `sg_wv1500` | 31,095 | 73.5% |

The split in coverage (~93% vs ~74%) reflects that `bdod`, `cec`, and `cfvo` tiles were available for more countries than the remaining properties.

---

## 4. Technical Implementation

### 4.1 Memory-Efficient Raster Extraction

SoilGrids GeoTIFFs reach up to **1.6 billion pixels** (e.g., French_Guiana at 250 m resolution). Loading such rasters entirely would crash the kernel. The extraction script implements three layers of memory safety:

1. **Boundary pre-filter** — discard coordinates outside the raster bounding box before any pixel I/O.
2. **`rasterio.sample()`** — reads only requested pixels via internal windowed I/O; memory usage is O(batch_size), not O(raster).
3. **Checkpoint pattern** — saves one parquet per country in `_sg_cache/`; the script resumes automatically from the last completed country.

### 4.2 Merge Logic

```
WoSIS (all depths)  →  filter upper_depth_cm ≤ 10  →  deduplicate by (lat, lon, country)
                                                                     ↓
SoilGrids parquet  ←──────────────────────────── left join on (country, lat, lon)
                                                                     ↓
                                         combined_soilhive_dataset.parquet
```

The left join ensures all WoSIS surface stations are retained even when SoilGrids data is absent (out-of-bounds coordinates or missing tile).

---

## 5. Output Files

| File | Description | Size |
|------|-------------|------|
| `data/combined_soilhive_dataset.parquet` | Final consolidated dataset | ~3 MB |
| `data/soilgrids_surface_all_countries.parquet` | SoilGrids extraction (all countries) | ~4 MB |
| `data/_sg_cache/{country}.parquet` | Per-country checkpoints | ~50–200 KB each |
| `notebook/nb08_consolidation_overview.png` | Visualisation figure | — |
| `reports/nb08_inventory.csv` | Country inventory with file status | — |

---

## 6. Key Observations

- **Variable sparsity in WoSIS** is the main data quality challenge. Properties like `BD` (7.5%), `N` (9.6%), and `P` (7.8%) will require imputation or should be excluded from models requiring complete cases.
- **SoilGrids provides dense coverage** (73–93%) as it is a model-based product with global spatial continuity. It can serve as a reliable substitute for sparse WoSIS measurements in modelling.
- **Country imbalance**: Switzerland (10,429), Mexico (7,446), and Belgium (6,962) account for ~59% of all stations. Models trained on this dataset should account for this geographic imbalance.
- **Paired properties** available for cross-validation: both WoSIS and SoilGrids measure pH, clay, sand, silt, CEC, N, BD — enabling direct comparison and bias correction between observed and modelled values.

---

## 7. Recommended Next Steps

1. **Cross-validation analysis** — compare WoSIS vs SoilGrids values for shared properties (pH, clay, sand, silt) to assess SoilGrids accuracy by region.
2. **Imputation strategy** — for sparse WoSIS properties (BD, N, P, CEC), use IDW spatial imputation or SoilGrids equivalents as predictors.
3. **Geographic bias correction** — apply country-level weighting or stratified sampling to reduce the dominance of Switzerland/Mexico/Belgium.
4. **Depth harmonisation** — WoSIS filter is `upper_depth ≤ 10 cm`; SoilGrids layer is `0–5 cm`. For strict comparisons, consider tightening the WoSIS filter to `upper_depth ≤ 5 cm`.
5. **Join with yield data** — merge `combined_soilhive_dataset.parquet` with GYGA or FAOSTAT yield records at station or H3 hexagon level for soil–yield modelling.

---

*Report generated from notebook `08_data_consolidation.ipynb` — SoilHive Project*
