import duckdb

# connect to local duckdb database
con = duckdb.connect("pm25_pipeline.duckdb")

# --------------------------------------------------
# LOAD PARQUET FILES
# --------------------------------------------------

con.execute("""

CREATE OR REPLACE TABLE era5 AS
SELECT *
FROM 'data/processed/daily/era5_data.parquet'

""")

con.execute("""

CREATE OR REPLACE TABLE pop_density AS
SELECT *
FROM 'data/processed/pd/pd.parquet'

""")


con.execute("""

CREATE OR REPLACE TABLE era5_surf AS
SELECT *
FROM 'data/processed/daily/era5_surf_data.parquet'

""")

con.execute("""

CREATE OR REPLACE TABLE station_loc AS
SELECT *
FROM 'data/processed/Valid_Stations.csv'

""")

con.execute("""

CREATE OR REPLACE TABLE aod AS
SELECT *
FROM 'data/processed/daily/aod_data.parquet'

""")

con.execute("""

CREATE OR REPLACE TABLE cpcb AS
SELECT *
FROM 'data/processed/cpcb_data.parquet'

""")

con.execute("""

CREATE OR REPLACE TABLE topo AS
SELECT *
FROM 'data/processed/station_elevations.csv'

""")

# --------------------------------------------------
# MERGE EVERYTHING
# --------------------------------------------------

con.execute("""

CREATE OR REPLACE TABLE master_dataset AS

SELECT

    e.Station_Id,
    e.date,

    e.t2m,
    e.u10,
    e.v10,
    e.sp,
    e.blh,
    e.tcc,
    e.d2m,
    e.skt,

    a.AOD,

    c.pm25,

    b.ssrd,
    b.e,
    b.tp,
            
    l.latitude,
    l.longitude,
    
    t.Elevation,
            
    pd.Population_Density

FROM era5 e

INNER JOIN aod a 
ON
    e.Station_Id = a.Station_Id
    AND e.date = a.date

INNER JOIN cpcb c
ON
    e.Station_Id = c.Station_Id
    AND e.date = c.time
            
INNER JOIN era5_surf b
ON 
    e.Station_ID = b.Station_Id
    AND e.date = b.date
            
LEFT JOIN station_loc l
ON 
    e.Station_ID = l.Station_ID
            
LEFT JOIN topo t
ON 
    e.Station_ID = t.Station_ID
            
LEFT JOIN pop_density pd
ON 
    e.Station_ID = pd.Station_ID

""")

# --------------------------------------------------
# EXPORT FINAL PARQUET
# --------------------------------------------------

con.execute("""

COPY master_dataset
TO 'data/processed/final/master_dataset.parquet'
(FORMAT PARQUET)

""")

print("Master dataset created successfully!")