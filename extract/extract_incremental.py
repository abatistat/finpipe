"""Incremental load: copy only new or changed ERP rows into DuckDB (raw schema).

First run for a table (no watermark yet): full copy.
Next runs: only rows with actualizado_en after the stored watermark,
merged into raw by primary key (delete + insert) inside a transaction.
"""

from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd
from sqlalchemy import text

from generator.db import get_engine

PRIMARY_KEYS = {
    "clientes": "cliente_id",
    "productos": "producto_id",
    "facturas": "factura_id",
    "lineas_factura": "linea_id",
    "pagos": "pago_id",
}
DUCKDB_PATH = Path(__file__).resolve().parent.parent / "data" / "finpipe.duckdb"


def get_watermark(con: duckdb.DuckDBPyConnection, table: str) -> str | None:
    """Return the last loaded actualizado_en for a table, or None on the first run."""
    row = con.execute(
        "SELECT CAST(last_loaded_at AS VARCHAR) FROM raw._watermarks WHERE table_name = ?",
        [table],
    ).fetchone()
    return row[0] if row else None


def main() -> None:
    engine = get_engine()
    loaded_at = datetime.now(timezone.utc)
    DUCKDB_PATH.parent.mkdir(exist_ok=True)

    with duckdb.connect(str(DUCKDB_PATH)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        con.execute(
            "CREATE TABLE IF NOT EXISTS raw._watermarks ("
            "table_name VARCHAR PRIMARY KEY, last_loaded_at TIMESTAMPTZ NOT NULL)"
        )

        for table, pk in PRIMARY_KEYS.items():
            watermark = get_watermark(con, table)

            if watermark is None:
                df = pd.read_sql_table(table, engine)
            else:
                query = text(
                    f"SELECT * FROM {table} WHERE actualizado_en > CAST(:wm AS timestamptz)"
                )
                df = pd.read_sql(query, engine, params={"wm": watermark})

            if df.empty:
                print(f"raw.{table}: 0 new or changed rows")
                continue

            df["_loaded_at"] = loaded_at
            con.register("incoming", df)
            con.begin()
            if watermark is None:
                con.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM incoming")
            else:
                con.execute(f"DELETE FROM raw.{table} WHERE {pk} IN (SELECT {pk} FROM incoming)")
                con.execute(f"INSERT INTO raw.{table} BY NAME SELECT * FROM incoming")
            con.execute(
                "INSERT OR REPLACE INTO raw._watermarks "
                f"SELECT '{table}', max(actualizado_en) FROM raw.{table}"
            )
            con.commit()
            con.unregister("incoming")

            mode = "full" if watermark is None else "incremental"
            print(f"raw.{table}: {len(df):,} rows ({mode})")


if __name__ == "__main__":
    main()
