import h5py
import pandas as pd 
from tqdm import dask
import xarray as xr
import os
import cfgrib
from pathlib import Path
from tqdm.auto import tqdm
from rich.progress import track 
import numpy as np
from dotenv import load_dotenv

np.seterr(all="ignore")

load_dotenv()  # This loads the variables from .env into os.environ

home_dir = os.getenv("HOME_FOLDER")

Valid_Station_df = pd.read_csv(f"{home_dir}/data/processed/Valid_Stations.csv").reset_index()

folder = f"{home_dir}/data/raw/3RIMG_L2G_AOD"

# -----------------------------
# PRECOMPUTE STATION INDICES
# -----------------------------

# Open ONE sample file to get grid
sample_ds = xr.open_dataset(
    f"{home_dir}/data/raw/3RIMG_L2G_AOD/2025/01APR/3RIMG_01APR2025_0545_L2G_AOD_V02R00.h5"
)

station_lookup = []

for station in Valid_Station_df.itertuples():

    lat_start_idx = np.abs(
        sample_ds.latitude.values - station.Latitude_Start
    ).argmin()

    lon_start_idx = np.abs(
        sample_ds.longitude.values - station.Longitude_Start
    ).argmin()

    lat_end_idx = np.abs(
        sample_ds.latitude.values - station.Latitude_End
    ).argmin()

    lon_end_idx = np.abs(
        sample_ds.longitude.values - station.Longitude_End
    ).argmin()

    station_lookup.append({
        "Station_Id": station.Station_id,
        "lat_start_idx": int(lat_start_idx),
        "lon_start_idx": int(lon_start_idx),
        "lat_end_idx": int(lat_end_idx),
        "lon_end_idx": int(lon_end_idx)
    })

rows = []

# -----------------------------
# EXTRACTION
# -----------------------------

all_files = []


for root, dirs, files in os.walk(folder):
    
    for file in (files):

        full_path = os.path.join(root, file)
        all_files.append(full_path)

print(f"total files: {len(all_files)}")

total = 0 
for full_path in track(
    all_files,
    description="INSAT Extraction in progress..."):

    try:

        ds = xr.open_dataset(
            full_path
        )

        print(ds)
        aod_arr = ds["AOD"].values

        # extract timestamp
        timestamp = pd.to_datetime(
            ds["time"].values[0]
        )

        for station in station_lookup:
            total += 1 
            lat_start = station["lat_start_idx"]
            lat_end = station["lat_end_idx"]

            lon_start = station["lon_start_idx"]
            lon_end = station["lon_end_idx"]

            try:
                
                box = aod_arr[
                    0,
                    lat_end :lat_start + 1,
                    lon_start :lon_end + 1
                ]
                
                aod = np.nanmean(box)


                rows.append({
                    "Station_Id": station["Station_Id"],
                    "date": timestamp,
                    "AOD" : aod
                })


            except Exception as e:
                print(f"Error occurred while processing station {station['Station_Id']}: {e}")
                continue
        
    except Exception as e:
        print(f"Failed on {file}: {e}")

print(f"{total}")

# -----------------------------
# FINAL DATAFRAME
# -----------------------------

master_AOD = pd.DataFrame(rows)

# optional
master_AOD = master_AOD.dropna()

# save fast format
master_AOD.to_parquet(f"{home_dir}/data/processed/aod/aod_data.parquet")
master_AOD.to_csv(f"{home_dir}/data/processed/aod/aod_data.csv", index=False)
print(master_AOD.describe())
