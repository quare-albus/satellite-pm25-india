import pandas as pd
import glob
import os

home_dir = os.getenv("HOME_FOLDER")
aod_file_path = f"{home_dir}/data/processed/aod/aod_data.csv"

os.makedirs(
    "data/processed/daily",
    exist_ok=True
)



df = pd.read_csv(aod_file_path)

df["date"]=pd.to_datetime(
    df["date"]
)

df["date"] = df["date"].dt.date

daily = (
    df.groupby(
        ["Station_Id", "date"],
        as_index=False
    )
    .mean(numeric_only=True)
)

output = os.path.basename(aod_file_path)

daily.to_parquet(
    f"data/processed/daily/aod_data.parquet"
)

daily.to_csv(
    f"data/processed/daily/aod_data.csv"
)