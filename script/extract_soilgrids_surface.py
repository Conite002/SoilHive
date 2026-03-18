"""
extract_soilgrids_surface.py
Memory-efficient SoilGrids surface (0-5cm) extraction at WoSIS station points.

Key design:
  - rasterio.sample() → windowed reads, never loads the full raster
  - Boundary filter   → skip coords outside raster extent before sampling
  - Batch processing  → limits peak memory when coordinate arrays are large
  - Checkpointing     → one parquet per country; safe to interrupt and resume

Usage:
    python extract_soilgrids_surface.py [--data-dir PATH] [--batch-size N] [--reset]
"""
import os, glob, gc, argparse
import numpy as np
import pandas as pd
import rasterio
from rasterio.crs import CRS

DATA_DIR   = "/home/agbelgaid/Documents/WORKSPACE/DataCollection/SoilHive/data"
CACHE_DIR  = os.path.join(DATA_DIR, "_sg_cache")
SURFACE    = "0-5cm"
BATCH_SIZE = 5_000   # points per batch

SG_DIVISORS = {
    "bdod":     100,   # cg/cm³  → g/cm³
    "cec":       10,   # mmol/kg → cmolc/kg
    "cfvo":      10,   # cm³/dm³ → %
    "clay":      10,   # g/kg    → %
    "nitrogen": 100,   # cg/kg   → g/kg
    "ocd":       10,
    "phh2o":     10,   # pH×10   → pH
    "sand":      10,
    "silt":      10,
    "soc":       10,
    "wv0010":    10,
    "wv0033":    10,
    "wv1500":    10,
}


# ── Core extraction ──────────────────────────────────────────────────────────

def sample_raster_at_points(tif_path: str,
                             lats: np.ndarray,
                             lons: np.ndarray,
                             batch_size: int = BATCH_SIZE) -> np.ndarray:
    """
    Sample raster values at (lat, lon) coordinates WITHOUT loading the full raster.

    Strategy:
      1. Open the raster and read metadata only (no pixel data loaded).
      2. Pre-filter coordinates outside the raster bounding box.
      3. Process valid coords in batches using rasterio.sample() which uses
         internal windowed reads — memory usage stays O(batch_size), not O(raster).
      4. Convert NoData / masked → NaN.

    Parameters
    ----------
    tif_path   : Path to GeoTIFF file.
    lats, lons : 1-D arrays of coordinates (EPSG:4326).
    batch_size : Number of points sampled per rasterio call.

    Returns
    -------
    np.ndarray of float64 (NaN where NoData or out-of-bounds).
    """
    result = np.full(len(lats), np.nan, dtype=np.float64)

    if not os.path.exists(tif_path):
        return result

    try:
        with rasterio.open(tif_path) as src:
            nodata  = src.nodata
            left, bottom, right, top = src.bounds

            # ── 1. Boundary filter (vectorised, no pixel I/O) ─────────────
            in_bounds = (
                (lons >= left)  & (lons <= right) &
                (lats >= bottom) & (lats <= top)
            )
            valid_idx = np.where(in_bounds)[0]

            if valid_idx.size == 0:
                return result          # no points inside raster extent

            valid_lats = lats[valid_idx]
            valid_lons = lons[valid_idx]

            # rasterio.sample expects (x, y) = (lon, lat)
            coords = list(zip(valid_lons.tolist(), valid_lats.tolist()))

            # ── 2. Batched sampling (windowed reads, low memory) ──────────
            sampled = np.full(len(valid_idx), np.nan, dtype=np.float64)
            for start in range(0, len(coords), batch_size):
                batch_coords = coords[start : start + batch_size]
                # src.sample() returns an iterator of 1-element masked arrays
                for j, pixel in enumerate(src.sample(batch_coords,
                                                      indexes=1,
                                                      masked=True)):
                    val = pixel[0]
                    if np.ma.is_masked(val):
                        continue
                    fval = float(val)
                    if nodata is not None and fval == nodata:
                        continue
                    sampled[start + j] = fval

            result[valid_idx] = sampled

    except Exception as e:
        print(f"    [WARN] {os.path.basename(tif_path)}: {e}")

    return result


# ── Per-country processing ───────────────────────────────────────────────────

def process_country(country: str,
                    data_dir: str,
                    cache_dir: str,
                    batch_size: int = BATCH_SIZE) -> tuple[bool, str]:
    base      = os.path.join(data_dir, country)
    sg_folder = os.path.join(base, "SoilGrids_250m")
    csv_path  = os.path.join(base, "output_data_points.csv")

    if not os.path.exists(csv_path):
        return False, "missing output_data_points.csv"
    if not os.path.isdir(sg_folder):
        return False, "missing SoilGrids_250m folder"

    tifs = sorted(glob.glob(os.path.join(sg_folder, f"*_{SURFACE}_mean.tif")))
    if not tifs:
        return False, f"no *_{SURFACE}_mean.tif"

    # Load only lat/lon columns
    df       = pd.read_csv(csv_path, usecols=["lat", "lon"])
    stations = df[["lat", "lon"]].drop_duplicates().reset_index(drop=True)
    lats     = stations["lat"].values.astype(np.float64)
    lons     = stations["lon"].values.astype(np.float64)
    del df

    rec = {"country": country, "lat": lats, "lon": lons}

    for tif in tifs:
        prop    = os.path.basename(tif).replace(f"_{SURFACE}_mean.tif", "")
        divisor = SG_DIVISORS.get(prop, 1)

        vals = sample_raster_at_points(tif, lats, lons, batch_size)
        good = ~np.isnan(vals)
        if good.any():
            vals[good] = np.round(vals[good] / divisor, 4)
        rec[f"sg_{prop}"] = vals
        del vals
        gc.collect()

    frame = pd.DataFrame(rec)
    out   = os.path.join(cache_dir, f"{country}.parquet")
    frame.to_parquet(out, index=False)

    sg_cols = [c for c in frame.columns if c.startswith("sg_")]
    n_ok    = frame[sg_cols].notna().any(axis=1).sum()
    msg     = f"{len(stations)} stations, {len(tifs)} SG props, {n_ok}/{len(stations)} with data"

    del frame, rec, stations, lats, lons
    gc.collect()
    return True, msg


# ── Main ─────────────────────────────────────────────────────────────────────

def get_countries(data_dir):
    return sorted([
        d for d in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, d))
        and not d.startswith(("Y", "Z", "_"))
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir",   default=DATA_DIR)
    parser.add_argument("--cache-dir",  default=CACHE_DIR)
    parser.add_argument("--batch-size", default=BATCH_SIZE, type=int)
    parser.add_argument("--reset",      action="store_true",
                        help="Clear cache and restart from scratch")
    args = parser.parse_args()

    os.makedirs(args.cache_dir, exist_ok=True)

    if args.reset:
        for f in glob.glob(os.path.join(args.cache_dir, "*.parquet")):
            os.remove(f)
        print("Cache cleared.")

    countries = get_countries(args.data_dir)
    print(f"Countries found : {len(countries)}")
    print(f"Batch size      : {args.batch_size:,} points")
    print()

    done, skipped, failed = 0, 0, 0
    for i, c in enumerate(countries, 1):
        cache = os.path.join(args.cache_dir, f"{c}.parquet")
        if os.path.exists(cache):
            print(f"  [{i:2d}/{len(countries)}] {c}: cached ✓")
            skipped += 1
            continue
        print(f"  [{i:2d}/{len(countries)}] {c}: ", end="", flush=True)
        ok, msg = process_country(c, args.data_dir, args.cache_dir, args.batch_size)
        if ok:
            print(f"OK — {msg}")
            done += 1
        else:
            print(f"SKIP — {msg}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Done: {done}  Cached: {skipped}  Failed: {failed}")

    # Merge all checkpoints
    files = sorted(glob.glob(os.path.join(args.cache_dir, "*.parquet")))
    if not files:
        print("No data to merge.")
        return

    merged  = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    out     = os.path.join(args.data_dir, "soilgrids_surface_all_countries.parquet")
    merged.to_parquet(out, index=False)

    print(f"\nFinal dataset : {out}")
    print(f"Shape         : {merged.shape}")
    sg_cols = [c for c in merged.columns if c.startswith("sg_")]
    print(f"\nSoilGrids surface (0-5cm) coverage:")
    for col in sg_cols:
        n   = merged[col].notna().sum()
        pct = n / len(merged) * 100
        print(f"  {col:25s}: {n:6,}/{len(merged):,} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
