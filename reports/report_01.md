# SoilHive - Surface Soil Dataset Construction Report

## 1. Overview

This notebook presents the construction of a machine learning-ready soil dataset from heterogeneous geospatial soil observations.
The pipeline is designed to transform raw multi-depth soil profiles into a consistent surface representation suitable for agronomic modeling and fertilizer recommendation systems.

The methodology follows a structured sequence:

1. Data loading
2. Cleaning and standardization
3. Surface layer extraction (0-30 cm)
4. Depth-weighted aggregation
5. Temporal filtering
6. Spatial aggregation
7. Transformation to wide format
8. Uncertainty estimation
9. Country attribution
10. Country-based partitioning


---

## 2. Dataset description

The dataset consists of geospatial soil observations with the following components:

* **Spatial variables**: latitude, longitude
* **Depth variables**: upper and lower depth (cm)
* **Soil properties**: pH, nitrogen, carbon, texture, etc.
* **Temporal variable**: sampling year
* **Source information**: dataset origin

Each location may contain multiple observations across:

- **Different depths**: ranging from 0 to 150 cm  
- **Different years**: spanning from 1920 to 2015  
- **Different data sources**:

| Source                          | Number of Observations | Percentage (%) |
|--------------------------------|-----------------------|----------------|
| WoSIS                          | 1,872,802             | 92.9%          |
| iSDA Field Data                | 122,572               | 6.1%           |
| Global Soil Nematode DB        | 25,158                | 1.2%           |
| CAROB                          | -                     | -              |

This results in a **multi-layer, heterogeneous dataset** requiring structured transformation.

### Focus on observed soil samples

This study focuses exclusively on **observed soil samples collected in situ**, rather than predicted or interpolated datasets such as SoilGrids.

The objective is to rely on **real measurements of soil properties**, ensuring:

* direct representation of actual soil conditions
* preservation of natural spatial variability
* avoidance of model-induced bias

Predicted datasets (e.g., SoilGrids) are generated through interpolation or machine learning models and may introduce:

* smoothing effects
* assumptions about spatial continuity
* uncertainties in poorly sampled regions

In contrast, this work prioritizes **measured soil data**, even if it leads to lower spatial coverage, in order to maintain **data authenticity and scientific reliability** for downstream agronomic modeling.

---

## 3. Data cleaning and standardization

Initial preprocessing ensures data consistency by:

* Removing rows with missing spatial coordinates or values
* Enforcing valid depth intervals (`upper < lower`)
* Converting sampling year into a proper datetime format

This step is critical to avoid:

* invalid depth calculations
* incorrect temporal interpretation
* propagation of corrupted values

---

## 4. Surface layer extraction 
![alt text](image.png)
Soil layers are not directly comparable due to varying depth intervals.
To ensure agronomic relevance, only layers overlapping the **0-30 cm range** are retained.

A weighting function is applied to quantify the proportion of each layer contributing to the surface.

This allows:

* partial inclusion of relevant layers
* exclusion of deeper, irrelevant layers

---

## 5. Depth-weighted aggregation

Instead of selecting arbitrary layers, a **weighted aggregation** is performed.

Each soil measurement is weighted based on its overlap with the surface layer.

This ensures:

* accurate representation of surface conditions
* avoidance of bias from thick or deep layers
* preservation of physical meaning

---

## 6. Temporal filtering (2000 - 2015)

The dataset spans several decades, introducing temporal heterogeneity.

Older observations may not reflect current soil conditions, especially for dynamic properties.

A temporal filtering step is applied to:

* remove outdated measurements
* improve alignment with modern agronomic data

---

## 7. Spatial aggregation

Multiple observations may exist at the same geographic location.

These are aggregated to produce stable estimates using:

* mean (central tendency)
* standard deviation (variability)
* observation count (robustness)

This reduces noise and improves statistical reliability.

---

## 8. Transformation to Wide Format

The dataset is transformed from long format to wide format:

* Each row represents a unique spatial location
* Each column represents a soil property

This structure is required for:

* machine learning models
* statistical analysis
* feature engineering

---

## 9. Uncertainty Estimation

To capture data reliability, two additional metrics are included:

* **Standard deviation (std)**: variability of measurements
* **Number of observations (n_obs)**: data density

These features allow:

* identification of uncertain regions
* robustness-aware modeling
* improved generalization

---

## 10. Country attribution

Each observation is assigned to a country using spatial joins.

This enables:

* geographic analysis
* country-specific modeling
* structured data partitioning

---

## 11. Country-based partitioning

Due to uneven data distribution, only the most represented countries are retained:

* Australia
* France
* Netherlands
* Germany

This ensures:

* sufficient data per region
* reduced sparsity
* more reliable analysis

---

## 12. Feature engineering and cleaning

Cleaning is performed independently per country to avoid global bias.

This includes:

* removing features with excessive missing values
* adaptive thresholding based on dataset size
* imputing remaining missing values using median

This step ensures:

* consistent feature quality
* balanced representation
* ML-ready dataset

---

## 13. Key Insights

* The dataset is highly heterogeneous across depth, time, and space
* Surface extraction is essential for agronomic relevance
* Depth-weighted aggregation significantly improves data quality
* Uncertainty features provide critical information for modeling
* Country-aware processing avoids structural bias

---

## 14. Limitations

* Temporal coverage is uneven across regions
* Some properties are sparsely observed
* Spatial distribution is imbalanced (dominance of certain countries like Australia)

---

## 15. Conclusion

The pipeline successfully converts raw soil profile data into a consistent, surface-focused dataset suitable for machine learning applications. By integrating depth-aware aggregation, uncertainty estimation, and geographic structuring, the resulting dataset provides a robust foundation for fertilizer recommendation and yield prediction models.

---
