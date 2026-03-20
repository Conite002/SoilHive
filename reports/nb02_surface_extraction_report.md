# NB02 — Surface Extraction Report

**Date**: 2026-03-19
**Notebook**: `notebook/NB02_surface_extraction.ipynb`
**Status**: COMPLETED — no errors

---

## 1. Execution Pipeline Overview

```
806,504 raw surface rows (77 ZIPs loaded)
        │
        ▼  Exact-duplicate removal
367,243 rows  (−439,261 rows, −54.5%)
        │
        ▼  Temporal selection (most recent per station × property × depth)
320,858 rows  (−46,385 older-year records set aside)
        │
        ▼  Depth-weighted mean aggregation
239,336 station × property aggregates
        │
        ▼  Pivot to wide format
 53,708 unique stations × 29 columns
```

---

## 2. Input Summary

| Metric | Value |
|--------|-------|
| Total ZIPs in inventory | 118 |
| Valid ZIPs with CSV processed | **77** |
| Skipped — raster only (no CSV) | 41 |
| Skipped — corrupt (BadZipFile) | 12 |
| Raw surface rows loaded | 806,504 |

---

## 3. Deduplication

### 3.1 Exact-Duplicate Removal

Duplicates are **internal to each data source** (e.g. WoSIS), not caused by cross-ZIP downloads.
A duplicate is defined as a row with identical: `lat`, `lon`, `iso3`, `property`, `upper_depth_cm`, `lower_depth_cm`, `sampling_date`, `value`.

| | Rows |
|--|------|
| Before | 806,504 |
| Removed | **439,261 (54.5%)** |
| After | 367,243 |

> All years are preserved in `wosis_surface_long.parquet` for temporal analysis.

### 3.2 Temporal Selection

A station may have measurements from multiple years.
**Rule**: keep the most recent observation per `(lat, lon, iso3, property, upper_depth_cm, lower_depth_cm)`.
Older records are set aside, not deleted — they remain in the long parquet.

| | Rows |
|--|------|
| Before | 367,243 |
| Older records set aside | **46,385** |
| Retained (most recent) | 320,858 |

### 3.3 Depth-Weighted Mean Aggregation

Multiple surface depth intervals at the same station (e.g. 0–5 cm + 5–10 cm) are collapsed into a single representative surface value using thickness-weighted averaging.

| | Value |
|--|-------|
| Input rows | 320,858 |
| Station × property aggregates | 239,336 |
| Unique stations (wide table) | **53,708** |

---

## 4. Station Recovery Rate

| | Stations |
|--|----------|
| Expected (unique countries, from NB01) | 56,991 |
| Output (wide table) | 53,708 |
| Recovery rate | **94.2%** ✓ (threshold: 80%) |

The 5.8% gap is explained by stations that have records only at depth > 10 cm (no surface observation) and are therefore correctly excluded from the surface-representative table. They remain in the raw ZIPs and in `wosis_surface_long.parquet`.

---

## 5. Property Completeness

Percentage of the 53,708 stations with at least one surface observation per property:

| Property | Coverage | Notes |
|----------|----------|-------|
| pH | **78.8%** | Best covered — core property |
| occ | **58.0%** | Organic carbon — well covered |
| clay | **54.8%** | Well covered |
| silt | **53.5%** | Well covered |
| EC | 40.3% | Moderate |
| N | 31.7% | Moderate |
| CEC | 22.9% | Moderate |
| sand | 20.1% | Moderate |
| P | 18.4% | Sparse |
| CF | 17.4% | Sparse |
| CaCO3 | 11.9% | Sparse |
| WR_gravimetric | 9.0% | Sparse |
| TC | 6.5% | Sparse |
| Al, Cu, Fe, Mn | 2.7% | Australia only — micro-elements |
| Ca, K, Mg | 2.8% | Very sparse |
| BD | 1.1% | Very sparse — raster fallback critical |
| nematode | 1.4% | Non-soil-chemistry property |
| WR_volumetric | 0.8% | Very sparse |
| Na | 0.1% | Essentially absent |

**Implication for NB05 (Integration)**: Properties with coverage < 10% (BD, TC, WR_vol, Na, nematode) will rely almost entirely on raster fallback (OpenLandMap / HoliSoils) for the unified dataset.

---

## 6. Stations per Country

| ISO3 | Country | Stations | Share |
|------|---------|----------|-------|
| AUS | Australia | 36,580 | 68.1% |
| DEU | Germany | 4,260 | 7.9% |
| FRA | France | 3,122 | 5.8% |
| BFA | Burkina Faso | 2,109 | 3.9% |
| AGO | Angola | 1,762 | 3.3% |
| CMR | Cameroon | 1,387 | 2.6% |
| BWA | Botswana | 1,368 | 2.5% |
| NLD | Netherlands | 1,300 | 2.4% |
| BEN | Benin | 725 | 1.4% |
| GRC | Greece | 330 | 0.6% |
| EST | Estonia | 223 | 0.4% |
| MAR | Morocco | 114 | 0.2% |
| ALB | Albania | 83 | 0.2% |
| CAF | Central African Rep. | 80 | 0.1% |
| HRV | Croatia | 79 | 0.1% |
| TUN | Tunisia | 41 | <0.1% |
| MDA | Moldova | 35 | <0.1% |
| BDI | Burundi | 28 | <0.1% |
| MNE | Montenegro | 25 | <0.1% |
| GEO | Georgia | 18 | <0.1% |
| PNG | Papua New Guinea | 16 | <0.1% |
| TCD | Chad | 13 | <0.1% |
| DZA | Algeria | 10 | <0.1% |

> **Geographic imbalance**: Australia alone accounts for 68.1% of all stations. This must be considered when interpreting global statistics.

---

## 7. Surface Coverage by Country

Countries where ≥ 2% of stations had NO surface record (upper_depth > 10 cm for all measurements):

| Country | Total stations | With surface | Gap |
|---------|---------------|--------------|-----|
| Australia | 39,727 | 36,580 | **−8.0%** |
| Netherlands | 1,354 | 1,300 | −4.0% |
| Angola | 1,800 | 1,762 | −2.1% |
| Cameroon | 1,394 | 1,387 | −0.5% |

All other countries: 97–100% surface coverage.

---

## 8. Output Artifacts

| File | Rows | Size | Description |
|------|------|------|-------------|
| `wosis_surface_long.parquet` | 367,243 | 2.86 MB | Post-dedup, all years, long format |
| `wosis_surface_wide.parquet` | 53,708 | 2.16 MB | Most-recent, depth-aggregated, wide format |
| `wosis_surface_flags.parquet` | 239,336 | 2.00 MB | Depth method + source flag per station × property |
| `logs/nb02_surface_extraction.log` | — | — | Full execution trace |

---

## 9. Known Limitations

1. **Temporal rule is arbitrary at the station level**: "most recent" is the best general choice but may miss improvement in older, higher-quality measurements. This is flagged in the flags parquet.
2. **Australia dominates**: 68% of stations from one country. Country-level statistics must always be stratified.
3. **12 corrupt ZIPs excluded**: these represent data that cannot be recovered without re-downloading from SoilHive.
4. **4 extra properties (Al, Cu, Fe, Mn)**: present only in the Australia ZIP. Coverage < 3% globally — raster fallback will be needed for all other countries.

---

## 10. Next Step

→ **NB03 — Coordinate Validation & QC**
Validate all 53,708 station coordinates: range checks, country boundary containment, null-island detection, duplicate coordinate flagging.
