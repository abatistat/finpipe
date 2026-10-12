import random
from datetime import date

import pandas as pd
from faker import Faker

from db import get_engine

SEMILLA = 42
random.seed(SEMILLA)
Faker.seed(SEMILLA)
fake = Faker("es_ES")

PAISES = ["Panamá", "Costa Rica", "Colombia", "México", "Estados Unidos"]
SEGMENTOS = ["Retail", "Mayorista", "Corporativo"]
CATALOGO = {
    "Hardware": ["Laptop", "Monitor", "Teclado", "Router", "Impresora", "Disco SSD"],
    "Software": ["Licencia ERP", "Antivirus", "Suite ofimática", "Licencia BI"],
    "Servicios": ["Soporte mensual", "Instalación", "Capacitación", "Consultoría"],
}


def limpiar_tablas(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "TRUNCATE clientes, productos, facturas, lineas_factura, pagos "
            "RESTART IDENTITY CASCADE"
        )


def generar_clientes(n=200):
    filas = []
    for _ in range(n):
        filas.append({
            "nombre": fake.company(),
            "pais": random.choice(PAISES),
            "segmento": random.choice(SEGMENTOS),
            "dias_credito": random.choice([0, 15, 30, 45, 60]),
            "fecha_alta": fake.date_between(date(2022, 1, 1), date(2024, 12, 31)),
        })
    return pd.DataFrame(filas)


def generar_productos():
    filas = []
    for categoria, nombres in CATALOGO.items():
        for nombre in nombres:
            precio = round(random.uniform(20, 2000), 2)
            costo = round(precio * random.uniform(0.40, 0.75), 2)
            filas.append({
                "nombre": nombre,
                "categoria": categoria,
                "precio_lista": precio,
                "costo_unitario": costo,
            })
    return pd.DataFrame(filas)


if __name__ == "__main__":
    engine = get_engine()
    limpiar_tablas(engine)

    clientes = generar_clientes()
    clientes.to_sql("clientes", engine, if_exists="append", index=False)
    print(f"clientes: {len(clientes)} filas")

    productos = generar_productos()
    productos.to_sql("productos", engine, if_exists="append", index=False)
    print(f"productos: {len(productos)} filas")
