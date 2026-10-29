# FinPipe dbt project

Transforms the raw ERP copy in `data/finpipe.duckdb` (schema `raw`) into analysis-ready models.

## Layers

- **staging** (`models/staging`, views): one model per raw table. Light cleaning only: dates cast to `DATE`, text trimmed, codes lowercased, money cast from `DOUBLE` to `DECIMAL(18,2)` so amounts stay exact to the cent.
- **marts** (`models/marts`, tables): business-ready models. Coming next.

## Run it

From this folder, with the project virtualenv active:

    dbt debug   # check the connection
    dbt run     # build all models

`profiles.yml` lives in this folder and points to the local DuckDB file, so no extra setup is needed.
