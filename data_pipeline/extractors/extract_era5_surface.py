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
zarr_file = f"{home_dir}/data/processed/era5_surf/era5_surf_2025.zarr"
Valid_Station_csv = f"{home_dir}/data/processed/Valid_Stations.csv"
store_folder = f"{home_dir}/data/intermediate/era5_surf/"
final_folder = f"{home_dir}/data/processed/era5_surf/"

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
    "ssrd",
    "e",
    "tp"
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

    times = mean_ds.valid_time.values.flatten()
    
    for i, t in enumerate(times):

        rows.append({
            "Station_Id": station.Station_Id,
            "time": pd.to_datetime(t),
            "e": float(
                mean_ds["e"].values.flatten()[i]
            ),
            "ssrd": float(
                mean_ds["ssrd"].values.flatten()[i]
            ),
            "tp": float(
                mean_ds["tp"].values.flatten()[i]
            )
        })

    extracted_df = pd.DataFrame(rows)

    extracted_df.to_parquet(
        f"{final_folder}/2025_era5_surf_{station.Station_Id}.parquet"
    )