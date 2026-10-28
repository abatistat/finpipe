"""Full load: copy every ERP table from Postgres into DuckDB (raw schema)."""

from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

from generator.db import get_engine

TABLES = ["clientes", "productos", "facturas", "lineas_factura", "pagos"]
DUCKDB_PATH = Path(__file__).resolve().parent.parent / "data" / "finpipe.duckdb"


def main() -> None:
    engine = get_engine()
    loaded_at = datetime.now(timezone.utc)
    DUCKDB_PATH.parent.mkdir(exist_ok=True)

    with duckdb.connect(str(DUCKDB_PATH)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        for table in TABLES:
            df = pd.read_sql_table(table, engine)
            df["_loaded_at"] = loaded_at
            con.register("incoming", df)
            con.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM incoming")
            con.unregister("incoming")
            print(f"raw.{table}: {len(df):,} rows")


if __name__ == "__main__":
    main()
