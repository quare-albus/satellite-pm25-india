import pandas as pd
import requests
import time
from rich.progress import track

# ----------------------------------------
# LOAD CSV
# ----------------------------------------

df = pd.read_csv(
    "data/processed/Valid_Stations.csv"
)

# ----------------------------------------
# STORE RESULTS
# ----------------------------------------

rows = []

# ----------------------------------------
# LOOP THROUGH STATIONS
# ----------------------------------------

for row in track(
    df.itertuples(),
    total=len(df),
    description="Getting elevations"
):

    try:

        station_id = row.Station_id
        lat = row.latitude
        lon = row.longitude

        # --------------------------------
        # API URL
        # --------------------------------

        url = (
            "https://api.opentopodata.org/v1/"
            f"aster30m?locations={lat},{lon}"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        elevation = (
            data["results"][0]["elevation"]
        )

        rows.append({

            "Station_Id": station_id,

            "Latitude": lat,

            "Longitude": lon,

            "Elevation": elevation
        })

        # avoid hammering API
        time.sleep(0.2)

    except Exception as e:

        print(
            f"Failed on "
            f"{row.Station_id}"
        )

        print(e)

# ----------------------------------------
# SAVE OUTPUT
# ----------------------------------------

elevation_df = pd.DataFrame(rows)

elevation_df.to_csv(
    "data/processed/station_elevations.csv",
    index=False
)

print(
    "Elevation extraction complete!"
)