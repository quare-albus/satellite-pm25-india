import h5py
import pandas as pd 
import xarray as xr
import os
import cfgrib
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import zarr
from rich.progress import track

home_dir = os.getenv("HOME_FOLDER")
zarr_file = f"{home_dir}/data/processed/era5/era5_2025.zarr"
Valid_Station_csv = f"{home_dir}/data/processed/Valid_Stations.csv"
store_folder = f"{home_dir}/data/intermediate/era5/"
final_folder = f"{home_dir}/data/processed/era5/"

Valid_Station_df = pd.read_csv(Valid_Station_csv).reset_index()
ds = xr.open_zarr(zarr_file)  # Open the Zarr file and access the 'time' variable



# -----------------------------
# PRECOMPUTE STATION INDICES
# -----------------------------
lats = ds.latitude.values
lons = ds.longitude.values

station_lookup = []

for station in Valid_Station_df.itertuples():

    lat_start_idx = np.abs(
        lats - station.Latitude_Start
    ).argmin()

    lon_start_idx = np.abs(
        lons - station.Longitude_Start
    ).argmin()

    lat_end_idx = np.abs(
        lats - station.Latitude_End
    ).argmin()

    lon_end_idx = np.abs(
        lons - station.Longitude_End
    ).argmin()

    station_lookup.append({
        "Station_Id": station.Station_id,
        "lat_start_idx": min(lat_start_idx, lat_end_idx),
        "lon_start_idx": min(lon_start_idx, lon_end_idx),
        "lat_end_idx": max(lat_start_idx, lat_end_idx),
        "lon_end_idx": max(lon_start_idx, lon_end_idx)
    })


station_idx_df = pd.DataFrame(station_lookup)

station_idx_df.to_parquet(
    f"{store_folder}/station_indices.parquet"
)


# ------------------------------------------------------------------------------
#                                EXTRACTION                                 
# ------------------------------------------------------------------------------
vars_to_extract = [
    "t2m",
    "u10",
    "v10",
    "sp",
    "blh",
    "tcc",
    "d2m",
    "skt"
]



for station in track(
    (station_idx_df.itertuples()), 
    description="ERA5 Extraction in progress...",
    total=len(station_idx_df)):

    rows = []

    subset = ds[vars_to_extract].isel(

        latitude=slice(
            station.lat_start_idx,
            station.lat_end_idx + 1
        ),

        longitude=slice(
            station.lon_start_idx,
            station.lon_end_idx + 1
        )
    )

    mean_ds = subset.mean(
        dim=["latitude", "longitude"]
    ).compute()

    times = ds.time.values

    for i, t in enumerate(times):

        rows.append({
            "Station_Id": station.Station_Id,
            "time": pd.to_datetime(t),
            "t2m": float(
                mean_ds["t2m"].values[i]
            ),
            "u10": float(
                mean_ds["u10"].values[i]
            ),
            "v10": float(
                mean_ds["v10"].values[i]
            ),
            "sp": float(
                mean_ds["sp"].values[i]
            ),
            "blh": float(
                mean_ds["blh"].values[i]
            ),
            "tcc": float(
                mean_ds["tcc"].values[i]
            ),
            "d2m": float(
                mean_ds["d2m"].values[i]
            ),
            "skt": float(
                mean_ds["skt"].values[i]
            )
        })

    extracted_df = pd.DataFrame(rows)

    extracted_df.to_parquet(
        f"{final_folder}/2025_era5_{station.Station_Id}.parquet"
    )