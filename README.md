# SoilHive

A soil data collection and analysis pipeline that aggregates open-source soil measurement databases into a unified dataset for exploratory analysis and machine learning research.

## Overview

SoilHive consolidates soil property observations from multiple global databases into a single structured dataset. The combined dataset contains over 1 million georeferenced measurements covering 20 soil properties across 31,000+ locations worldwide, spanning measurements from 1928 to 2017.

## Data Sources

| Source | Description |
|---|---|
| WoSIS | World Soil Information Service — primary source of physicochemical measurements |
| CAROB | Harmonized crop and soil research data |
| Global Soil Nematode DB | Nematode abundance by soil horizon |

## Dataset Schema

The combined output (`data/combined_output_data_points.csv`) contains 14 columns:

| Column | Type | Description |
|---|---|---|
| `id` | int | Record identifier |
| `lat` / `lon` | float | Geographic coordinates |
| `property` | str | Soil property name |
| `original_name` | str | Property name as recorded in the source database |
| `upper_depth_cm` | float | Top of the sampling horizon (cm) |
| `lower_depth_cm` | float | Bottom of the sampling horizon (cm) |
| `value` | float | Measured value |
| `unit` | str | Unit of measurement |
| `sampling_date` | float | Year of soil sampling |
| `license` | str | Data license (e.g., CC BY 3.0) |
| `h3_index` | str | Uber H3 spatial index at resolution 3 |
| `publication_date` | str | Date the record was published |
| `data_source` | str | Source database name |

## Soil Properties Covered

`sand`, `clay`, `silt`, `pH`, `N`, `occ` (organic carbon), `CaCO3`, `CEC`, `BD` (bulk density), `TC` (total carbon), `CF` (coarse fragments), `EC` (electrical conductivity), `P`, `K`, `Ca`, `Mg`, `Na`, `WR_volumetric`, `WR_gravimetric`, `nematode`

## Dataset Statistics

- **Total observations:** 1,032,331
- **Unique locations:** 31,124
- **H3 spatial cells:** 613
- **Soil properties:** 20
- **Depth range:** 0 to 800 cm
- **Temporal range:** 1928 to 2017
- **Sampling date coverage:** ~48% of records have a sampling date

## Notebooks

### `extractcsv.ipynb`

Ingestion pipeline. Scans the `data/` directory recursively for all CSV files, loads and concatenates them into a single dataframe, and writes the result to `data/combined_output_data_points.csv`.

### `visualisation.ipynb`

Exploratory data analysis. Covers:

- Dataset structure and missing value audit
- Observation counts by source and property
- Value distributions for key properties (histograms,  etc)
- Vertical variation — how properties change with depth across five horizon classes (0-30, 30-60, 60-100, 100-200, >200 cm)
- Source comparison — which properties each database provides
- Correlation matrix between co-located soil properties

## Project Structure

```
SoilHive/
├── data/
│   ├── combined_output_data_points.csv   # Merged output (generated)
│   └── ...                               # Raw source CSV files
├── notebook/
│   ├── extractcsv.ipynb                  # Data ingestion pipeline
│   └── visualisation.ipynb               # Exploratory data analysis
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
```

Install with:

```bash
pip install pandas numpy matplotlib seaborn scipy
```

## Usage

1. Place raw source CSV files in the `data/` directory.
2. Run `extractcsv.ipynb` to produce the combined dataset.
3. Run `visualisation.ipynb` for exploratory analysis.

## Notes on Data Quality

- **Sampling date** is missing for approximately 52% of records, primarily from the CAROB source.
- **Unit** is missing for ~26% of records (nematode counts have no standard unit).
- Outliers are present in all properties; the visualisation notebook clips to the 1st–99th percentile range for display.
- The dataset has a temporal bias toward the 1970s–1980s; records from after 2010 are sparse.

## License

Data licenses vary by source. Each record includes a `license` field. Licenses present in this dataset include CC BY 3.0 and related Creative Commons variants. Consult the original source databases before any redistribution or commercial use.
