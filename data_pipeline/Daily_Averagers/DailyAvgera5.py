import duckdb

duckdb.sql("""

CREATE TABLE master AS
SELECT *
FROM 'data/processed/era5/*.parquet'

""")

duckdb.sql("""

COPY (

    SELECT
        Station_Id,
        DATE(time) as date,

        AVG(t2m) as t2m,
        AVG(u10) as u10,
        AVG(v10) as v10,
        AVG(sp) as sp,
        AVG(blh) as blh,
        AVG(tcc) as tcc,
        AVG(d2m) as d2m,
        AVG(skt) as skt

    FROM master

    GROUP BY
        Station_Id,
        DATE(time)

)

TO 'data/processed/daily/era5_data.parquet'
(FORMAT PARQUET)

""")

duckdb.sql("""

CREATE TABLE master_surf AS
SELECT *
FROM 'data/processed/era5_surf/*.parquet'

""")

duckdb.sql("""

COPY (

    SELECT
        Station_Id,
        DATE(time) as date,

        AVG(ssrd) as ssrd,
        AVG(e) as e,
        AVG(tp) as tp

    FROM master_surf

    GROUP BY
        Station_Id,
        DATE(time)

)

TO 'data/processed/daily/era5_surf_data.parquet'
(FORMAT PARQUET)

""")