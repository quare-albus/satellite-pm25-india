import h5py
import pandas as pd 
import xarray as xr
import os
import cfgrib
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from rich.progress import track

home_dir = os.getenv("HOME_FOLDER")
Valid_Station_csv = f"{home_dir}/data/processed/Valid_Stations.csv"
Valid_Station_df = pd.read_csv(Valid_Station_csv).reset_index()
Stations_df = pd.read_csv(f"{home_dir}/config/Station_Locations.csv").reset_index()

def Cleaner_Extractor(file_path):
    cpcb = pd.read_csv(file_path).reset_index()
    cpcb = cpcb.dropna(subset=["PM2.5 (µg/m³)"])  
    cpcb = cpcb.rename(columns={"PM2.5 (µg/m³)": "PM2.5",
                                "index": "time"})
    cpcb = cpcb.rename(columns={"time": "Index",
                                "Timestamp": "time"})
    return cpcb[["time", "PM2.5"]]

folder_path = Path("data/raw/PM_CPCB/")

all_CPCB_dfs = []
skipped = 0
Valid_Station = []

# Loop through all files ending in .csv
for file in folder_path.glob("*.csv"):
    print(f"Processing: {file.name}")
    df = Cleaner_Extractor(file)
    
    #extract station name from file name and add as a column
    station_name = file.stem.split("_")[1]  # Assuming the station name is the second part of the file name before an underscore
    try : 
        Station = Stations_df[Stations_df['Station_Name'] == station_name]
        Station_id = Station['Station_id'].values[0]
        Valid_Station.append(Station.head(1))
    except IndexError:
        print(f"Station ID not found for {station_name}")
        skipped += 1 
        continue
    df["Station_Id"] = Station_id


    df = df.dropna().reset_index()

    df["time"] = pd.to_datetime(df["time"]).dt.date # the exact time is of no use, only the dat as the project focuses on the daily average of PM2.5

    df = df.groupby("time").mean().reset_index()

    #feature engineering 
    df["pm25_lag_1"] = df["PM2.5"].shift(1)
    df["pm25_lag_3"] = df["PM2.5"].shift(3)
    df["pm25_lag_7"] = df["PM2.5"].shift(7)
    df["pm25"] = df["PM2.5"]


    df = df.dropna().reset_index(drop=True)  # Drop rows with NaN values after creating lag features

    
    all_CPCB_dfs.append(df)

master_CPCB = pd.concat(all_CPCB_dfs, ignore_index=True).reset_index()
master_CPCB = master_CPCB.rename({
    "time" : "date"
})
master_CPCB.to_csv("data/processed/cpcb_data.csv", index=False)
master_CPCB.to_parquet("data/processed/cpcb_data.parquet", index=False)      
print(f"Total files processed: {len(all_CPCB_dfs)}")
print(f"Total files skipped due to missing Station ID: {skipped}")
