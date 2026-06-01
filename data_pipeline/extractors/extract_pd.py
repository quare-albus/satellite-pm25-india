import rasterio
import pandas as pd

pop = rasterio.open("data/raw/pop_density/ind_pd_2020_1km.tif")

stations = pd.read_csv("data/processed/Valid_Stations.csv")

population = []

for row in stations.itertuples():

    value = list(
        pop.sample(
            [(row.longitude, row.latitude)]
        )
    )[0][0]

    population.append(value)

stations["Population_Density"] = population

stations.to_parquet(
    "data/processed/pd/pd.parquet",
    index=False
)