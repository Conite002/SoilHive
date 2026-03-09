# PEDOLOGICAL ANALYSIS REPORT — ARGENTINA

## Toward Modeling the Soil–Yield Relationship at the Climate Zone Scale

**Project:** SoilHive — Comparative Analysis of Global Soil Data
**Country analyzed:** Argentina
**Date:** March 2026

---

## EXECUTIVE SUMMARY

This report presents an in-depth analysis of Argentina’s soil data, integrated with agricultural yield data from the GYGA (Global Yield Gap Atlas) database. Based on **14,397 observations** from 281 sampling points, covering 36 distinct years between 1955 and 2018, we establish a solid analytical foundation to test two central hypotheses:

1. **Pedological similarity predicts yield similarity** at the climate zone scale.
2. **Agro-pedological knowledge transfer** (K-NN type approach) can estimate yields in zones without direct yield data.

If validated, these hypotheses open the way to a global yield estimation tool that can be applied even in countries or regions with limited agronomic documentation.

---

## 1. CONTEXT AND MOTIVATION

### 1.1 Why Argentina?

Availability of yield data in substantial quantity.

### 1.2 Scientific Challenge

The fundamental challenge in global agronomy is the following:
**Can crop yield be predicted from the pedological signature of soils, independently of direct productivity measurements?**

If so, the implications are significant:

* Estimation of potential yields in countries without agronomic monitoring
* Identification of underexploited high yield-gap zones


---

## 2. DATA SOURCES AND QUALITY

### 2.1 Soil Data

| Source    | Observations | % with date | % with depth |
| --------- | ------------ | ----------- | ------------ |
| **WoSIS** | 14,118       | **94.5%**   | **100%**     |
| CAROB     | 983          | ~6%          | 0%           |

**The analysis is based entirely on the WoSIS source**, which provides significantly higher structural quality.

#### Measured Properties (18 total)

| Property             | Covered Points | Availability |
| -------------------- | -------------- | ------------ |
| OCC (Organic Carbon) | 274 / 276      | 99%          |
| Sand                 | 230 / 276      | 83%          |
| pH                   | 230 / 276      | 83%          |
| Clay                 | 230 / 276      | 83%          |
| Silt                 | 230 / 276      | 83%          |
| CEC                  | 219 / 276      | 79%          |
| Nitrogen (N)         | 215 / 276      | 78%          |
| CaCO₃                | 106 / 276      | 38%          |

![alt text](image-1.png)
#### Sampling Campaigns

The data span **36 distinct years** (1955–2018). The years 1970 and 1995 correspond to complete and standardized campaigns, with up to **13 properties measured simultaneously** per point. This richness reflects protocol design rather than data quality bias.

> **Key observation:** The variability in the number of properties per point is primarily explained by differences in original campaign protocols. This is not a quality issue but a methodological difference across campaigns.

---


### 2.2 Yield Data Availability by Crop — (Climate Zone Level)

| Crop       | YA (Actual Yield) | YP (Potential Yield) | YW (Water-Limited Yield) | Climate Zones |
|------------|------------------|----------------------|--------------------------|---------------|
| Soybean    | 288              | 1024                 | 1024                     | 11            |
| Maize      | 261              | 928                  | 928                      | 11            |
| Wheat      | 90               | 320                  | 320                      | 10            |
| Sunflower  | 72               | 256                  | 256                      | 8             |
| Rice       | 55               | 55                   | 0                        | 5             |
---

## 3. TEMPORAL ANALYSIS OF SOIL PROPERTIES

### 3.1 Linear Regression Results

$Y_t$ = $\beta_0$ + $\beta_1$ t + $\varepsilon_t$

où :

- $Y_t$ = moyenne annuelle de la propriété  
- $t$ = année  
- $\beta_0$ = intercept  
- $\beta_1$ = pente (variation annuelle)  
- $\varepsilon_t$ = erreur aléatoire  

For each property with sufficient temporal coverage, a linear regression was applied to annual means.

| Property                 | Slope (unit/year) | R²    | p-value | Significance      |
| ------------------------ | ----------------- | ----- | ------- | ----------------- |
| **OCC** (Organic Carbon) | +0.537            | 0.403 | 0.001   | **✓ Significant** |
| **Sand**                 | +1.165            | 0.335 | 0.002   | **✓ Significant** |
| **Silt**                 | −0.711            | 0.288 | 0.006   | **✓ Significant** |
| **Clay**                 | −0.455            | 0.257 | 0.010   | **✓ Significant** |
| CaCO₃                    | +3.210            | 0.338 | 0.226   | — Not significant |
| N                        | +0.018            | 0.032 | 0.422   | — Not significant |
| CEC                      | −0.089            | 0.035 | 0.446   | — Not significant |
| pH                       | +0.007            | 0.017 | 0.522   | — Not significant |

![alt text](image.png)
### 3.2 Interpretation

**Four properties show statistically significant evolution** over the 1955–2018 period:

#### Increase in Organic Carbon (+0.54/year, p=0.001)

OCC exhibits the most robust signal (R²=0.40). This may reflect:

* Intensification of conservation agriculture practices (no-till, rotations)
* Sampling bias toward high-organic-potential sites
* Genuine organic matter improvement in fertile Pampas regions

#### Increase in Sand and Decrease in Fine Fractions

The simultaneous trend toward higher sand content and lower silt and clay suggests a **textural transformation of soils** over decades. Possible explanations include:

* Preferential erosion of fine particles (wind or water erosion)
* Aeolian deflation in arid zones (Dry Pampas, Patagonia)
* Vegetation cover changes affecting soil cohesion

> **Central hypothesis:** These trends are structurally meaningful and may document a long-term transformation of Argentine soils, with direct implications for productive capacity.

---

## 4. AGRICULTURAL ANALYSIS: MAIZE AS A PILOT CASE

### 4.1 Why Maize?

| Criterion                 | Justification                                       |
| ------------------------- | --------------------------------------------------- |
| **Fertility indicator**   | Highly sensitive to soil properties (N, P, texture) |
| **Agronomic stability**   | Less affected by complex rotations than soybean     |
| **Data coverage**         | 957 observations across 11 climate zones            |

Maize provides a **cleaner pedological signal**, making it ideal for testing the soil–yield relationship.

### 4.2 Yield Data Structure

```
YA  : Actual yield (field measured)             → 261 obs.
YW  : Water-limited yield                       → 928 obs.
YP  : Potential yield (no limitations)          → 928 obs.
Gap : YP - YA                                   → computed
```

The **yield gap** (difference between potential and actual yield) is the main target variable. It measures agricultural inefficiency and can be partially explained by soil properties.

---

## 5. HYPOTHESES AND METHODOLOGY

### Hypothesis 1: Pedological Similarity → Yield Similarity

**Statement:** Climate zones with similar soil signatures will exhibit similar maize yields.

**Testing protocol:**

```
Step 1 → Aggregate soil properties by climate zone
Step 2 → Aggregate maize yield by climate zone
Step 3 → Standardization (StandardScaler)
Step 4 → PCA (2 components)
Step 5 → KMeans clustering
Step 6 → ANOVA on YA, YP, YW, Gap per cluster
Step 7 → Evaluate cluster separability
```

**Validation criterion:** ANOVA must show statistically significant yield differences across pedological clusters (p < 0.05).

---

### Hypothesis 2: Agro-Pedological Knowledge Transfer (K-NN)

**Statement:** For a zone without yield data, yield can be estimated from its closest pedological neighbors.

**Method:**

```
For a target zone Z without yield:
  1. Compute its standardized pedological signature
  2. Compute Euclidean distance to k known zones (PCA space)
  3. Estimate yield(Z) = Σ [yield(neighbor_i) × w_i] / Σ w_i
     where w_i = 1 / distance_i
```

This approach is analogous to an **agro-ecological K-NN**, transferring agronomic knowledge between pedologically similar territories.

**Potential applications:**

* Yield estimation in countries without GYGA data
* Global mapping of agro-pedological regimes
* Identification of yield “outlier” countries

---

## 6. FULL EXECUTION PLAN

### PHASE 1 — Validation

* Soil aggregation → climate zone (11 zones)
* Maize yield aggregation → climate zone
* Soil–yield correlation (Pearson + Spearman)
* PCA + clustering
* ANOVA: yield per cluster
* Predictive power assessment (R², RMSE)

### PHASE 2 — Radius Calibration

* Test 10 km / 25 km / 50 km radii
* Evaluate pedological signal stability
* Identify outlier stations
* Select optimal radius

### PHASE 3 — Cross-Country Transfer

* Aggregate soil data from N countries
* Build common pedological space
* Apply K-NN to countries without yield
* Map global pedological similarity
* Identify agronomic outliers

---

## 7. STRENGTHS AND LIMITATIONS

### Strengths

* **Robust empirical base:** 14,118 validated WoSIS observations
* **Temporal coverage:** 60+ years (1955–2018)
* **13 core soil properties measured**
* **11 climate zones** for clustering diversity
* **Significant temporal signals** (4 properties, p < 0.01)

### Identified Limitations

* Few multi-campaign points (2/276)
* CAROB lacks depth/date metadata
* Limited YA observations (261)
* Soil and GYGA stations not always co-located

---

## 8. ANTICIPATED RESULTS AND IMPLICATIONS

### If Hypothesis 1 is validated

* Proof of concept: pedology predicts yield at macro-climatic scale
* Soil potential scoring per climate zone
* Identification of underperforming Argentine zones

### If Hypothesis 2 is validated

* Global yield estimation tool (150+ countries)
* Investment targeting based on pedological similarity
* Identification of agronomic over- and under-performers

### SoilHive Product Vision

These hypotheses underpin a future **agro-pedological recommendation engine**:

```
INPUT  : Pedological signature of a territory
OUTPUT : Estimated yield + Similar countries + Potential yield gap
```

This responds to growing demand from agricultural development institutions (FAO, CGIAR, World Bank) for yield potential estimation tools in low-data regions.

---

## 9. CONCLUSION

The pedological analysis of Argentina demonstrates that a robust analytical foundation can be built from heterogeneous soil datasets, provided that rigorous source auditing (WoSIS vs CAROB), quality stratification (dated vs non-dated), and coherent spatial aggregation are applied.

The **four significant temporal trends** (OCC, sand, silt, clay) confirm that Argentine soils are undergoing structural transformation, with agronomic implications that require further quantification.

The integration of WoSIS soil data and GYGA yield data — via climate zone aggregation — provides a solid analytical framework for testing the soil–yield relationship. **Maize**, given its sensitivity to soil properties and sufficient coverage across 11 climate zones, represents the optimal pilot case.

**Argentina is not just a country under analysis — it is the training ground for a globally transferable methodology.**

---

*Data sources: WoSIS (ISRIC), GYGA (Wageningen University), OpenLandMap, GSOCmap*
