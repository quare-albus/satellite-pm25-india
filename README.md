# PM2.5 India Estimation using INSAT, ERA5 and CPCB Data

## Overview

This project develops an end-to-end geospatial machine learning pipeline for estimating PM2.5 concentrations across India using satellite observations, meteorological reanalysis data, and ground-based monitoring stations.

The workflow combines INSAT Aerosol Optical Depth (AOD), ERA5 atmospheric variables, and CPCB PM2.5 observations to train machine learning models capable of learning spatial and atmospheric patterns associated with air pollution.

The project emphasizes:

- Scientific data engineering
- Geospatial feature extraction
- Atmospheric feature engineering
- Scalable data processing
- Leakage-aware model development
- Reproducible machine learning workflows

---

## Problem Statement

Ground-based PM2.5 monitoring stations provide accurate measurements but have limited spatial coverage.

Satellite observations provide broad spatial coverage but do not directly measure surface PM2.5.

This project attempts to learn the relationship between:

```text
Satellite Aerosols (AOD)
+
Meteorology (ERA5)
+
Spatial Characteristics
↓
Surface PM2.5
```

using CPCB monitoring stations as ground truth.

---

## Data Sources

### CPCB

Source:

https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-data-repository

Used for:

- PM2.5 measurements
- Ground-truth labels

---

### INSAT AOD

Used for:

- Aerosol Optical Depth
- Satellite-derived aerosol loading

---

### ERA5 Reanalysis

Source:

https://cds.climate.copernicus.eu/

Variables used include:

- 2m Temperature (t2m)
- Surface Pressure (sp)
- Boundary Layer Height (blh)
- 10m U Wind (u10)
- 10m V Wind (v10)
- Total Precipitation (tp)

Derived features:

- Wind Speed
- Pollution Trap Index
- Ventilation Coefficient
- Seasonal Encodings

---

### Elevation

Source:

- OpenTopoData
- Copernicus DEM

Used as a spatial terrain feature.

---

### Population Density

Source:

- WorldPop

Used as a proxy for:

- Urbanization
- Human activity
- Emissions intensity

---

## Project Architecture

```text
ERA5 GRIB Files
        │
        ▼
      Zarr
        │
        ▼
 Feature Extraction
        │
        ▼
    Parquet Files
        │
        ▼
      DuckDB
        │
        ▼
Feature Engineering
        │
        ▼
    XGBoost Model
        │
        ▼
 PM2.5 Estimation
```

---

## Repository Structure

```text
pm25-india/

├── data/
│   ├── duckdb/
│   ├── parquet/
│   └── station_data/
│
├── data_pipeline/
│
├── feature_engineering/
│
├── modeling/
│
├── notebooks/
│
├── docs/
│
├── results/
│
├── README.md
│
├── requirements.txt
│
└── VERSION_1.md
```

---

## Data Engineering Pipeline

### ERA5 Processing

- Download ERA5 datasets
- Convert GRIB files to NetCDF/Zarr
- Chunk atmospheric variables
- Extract station-centered spatial windows

### INSAT Processing

- Read INSAT products
- Extract AOD values
- Match satellite observations to station locations

### Feature Store

Features stored using:

- Zarr
- Parquet
- DuckDB

to enable scalable processing.

---

## Feature Engineering

### Atmospheric Features

- AOD
- Temperature
- Pressure
- Boundary Layer Height
- Wind Speed
- Precipitation

### Derived Features

#### Wind Speed

```text
sqrt(u10² + v10²)
```

#### Pollution Trap Index

```text
AOD / BLH
```

#### Ventilation Coefficient

```text
BLH × Wind Speed
```

### Spatial Features

- Latitude
- Longitude
- Elevation
- Population Density

### Temporal Features

- Month Encoding
- Seasonal Cycles
- Winter Indicators

---

## Machine Learning

### Model

```text
XGBoost Regressor
```

Chosen because:

- Strong performance on tabular data
- Handles nonlinear interactions
- Robust to feature scaling
- Interpretable feature importance

---

## Validation Strategy

The project investigates:

### Temporal Forecasting

Using:

- Lag PM Features
- Rolling PM Features

Resulted in significantly higher performance.

### Spatial Inference

Using:

- Atmospheric variables
- Spatial covariates

without PM lag information.

This better represents estimation at unmonitored locations.

---

## Results

### Version 1

Model:

```text
XGBoost
```

Features:

- INSAT AOD
- ERA5 Variables
- Latitude
- Longitude
- Elevation
- Population Density

Performance:

R² ≈ 0.45
MAE ≈ 21 µg/m³


without autoregressive PM features.

Key findings:

- Spatial features were highly informative.
- Population density improved predictive performance.
- Atmospheric variables contributed meaningful signal.
- Lag PM features dominated forecasting performance.
- Spatial estimation is substantially harder than station forecasting.

---

## Feature Importance Insights

Most influential features included:

- Latitude
- Population Density
- Longitude
- Elevation
- Temperature
- Boundary Layer Height
- Wind Speed
- AOD

This suggests the model learns both:

- Spatial pollution structure
- Atmospheric transport behavior

---

## Limitations

Current model does not include:

- Nighttime Lights (VIIRS)
- Land Cover
- Fire Counts
- Emissions Inventories
- Road Density
- Industrial Activity Indicators

Validation is station-based and future work will explore more rigorous spatial validation strategies.

---

## Future Work

Potential improvements include:

### Spatial Features

- VIIRS Nighttime Lights
- ESA WorldCover
- Road Density
- NDVI

### Emissions Features

- FIRMS Fire Data
- EDGAR Emissions
- CAMS Emissions

### Modeling

- Spatial Cross Validation
- Time-Series Validation
- Uncertainty Estimation
- Ensemble Models

### Mapping

- India-wide PM2.5 Prediction Maps
- Daily Spatial Forecasting
- Uncertainty Maps

---

## Technologies Used

- Python
- Pandas
- NumPy
- Xarray
- DuckDB
- Zarr
- Rasterio
- Scikit-Learn
- XGBoost
- Matplotlib

---

## Author

Independent atmospheric machine learning and geospatial data engineering project developed as part of exploration into satellite-based air quality estimation and environmental data science.