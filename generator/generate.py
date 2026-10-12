import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

from db import get_engine

SEMILLA = 42
random.seed(SEMILLA)
Faker.seed(SEMILLA)
fake = Faker("es_ES")

FECHA_CORTE = date(2026, 9, 30)
INICIO_FACTURAS = date(2024, 1, 1)
N_FACTURAS = 3000

PAISES = ["Panamá", "Costa Rica", "Colombia", "México", "Estados Unidos"]
SEGMENTOS = ["Retail", "Mayorista", "Corporativo"]
METODOS_PAGO = ["Transferencia", "ACH", "Cheque", "Tarjeta"]
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


def cargar(df, tabla, engine):
    df.to_sql(tabla, engine, if_exists="append", index=False, method="multi", chunksize=1000)
    print(f"{tabla}: {len(df)} filas")


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


def asignar_estado(vencimiento):
    if random.random() < 0.03:
        return "anulada"
    dias_vencida = (FECHA_CORTE - vencimiento).days
    if dias_vencida > 60:
        prob_pagada = 0.95
    elif dias_vencida > 0:
        prob_pagada = 0.85
    else:
        prob_pagada = 0.35
    return "pagada" if random.random() < prob_pagada else "abierta"


def generar_facturas(clientes, n=N_FACTURAS):
    clientes_lista = clientes.to_dict("records")
    filas = []
    for _ in range(n):
        cliente = random.choice(clientes_lista)
        inicio = max(cliente["fecha_alta"], INICIO_FACTURAS)
        emision = fake.date_between(inicio, FECHA_CORTE)
        vencimiento = emision + timedelta(days=int(cliente["dias_credito"]))
        filas.append({
            "cliente_id": int(cliente["cliente_id"]),
            "fecha_emision": emision,
            "fecha_vencimiento": vencimiento,
            "moneda": "USD",
            "estado": asignar_estado(vencimiento),
        })
    return pd.DataFrame(filas)


def generar_lineas(facturas, productos):
    productos_lista = productos.to_dict("records")
    filas = []
    totales = {}
    for factura_id in facturas["factura_id"]:
        total = 0
        for _ in range(random.randint(1, 5)):
            producto = random.choice(productos_lista)
            if producto["categoria"] == "Servicios":
                cantidad = random.randint(1, 3)
            else:
                cantidad = random.randint(1, 20)
            precio = round(float(producto["precio_lista"]) * random.uniform(0.95, 1.05), 2)
            descuento = random.choice([0, 0, 0, 5, 10])
            filas.append({
                "factura_id": int(factura_id),
                "producto_id": int(producto["producto_id"]),
                "cantidad": cantidad,
                "precio_unitario": precio,
                "descuento_pct": descuento,
            })
            total += cantidad * precio * (1 - descuento / 100)
        totales[factura_id] = round(total, 2)
    return pd.DataFrame(filas), totales


def generar_pagos(facturas, totales):
    filas = []
    for f in facturas.itertuples():
        total = totales[f.factura_id]
        if f.estado == "pagada":
            if random.random() < 0.8:
                montos = [total]
            else:
                primero = round(total * random.uniform(0.3, 0.7), 2)
                montos = [primero, round(total - primero, 2)]
        elif f.estado == "abierta" and random.random() < 0.3:
            montos = [round(total * random.uniform(0.3, 0.7), 2)]
        else:
            continue
        for monto in montos:
            atraso = random.randint(-10, 45)
            fecha = f.fecha_vencimiento + timedelta(days=atraso)
            fecha = min(max(fecha, f.fecha_emision), FECHA_CORTE)
            filas.append({
                "factura_id": int(f.factura_id),
                "fecha_pago": fecha,
                "monto": monto,
                "metodo": random.choice(METODOS_PAGO),
            })
    return pd.DataFrame(filas)


if __name__ == "__main__":
    engine = get_engine()
    limpiar_tablas(engine)

    cargar(generar_clientes(), "clientes", engine)
    cargar(generar_productos(), "productos", engine)

    clientes = pd.read_sql(
        "SELECT cliente_id, dias_credito, fecha_alta FROM clientes ORDER BY cliente_id", engine
    )
    productos = pd.read_sql(
        "SELECT producto_id, categoria, precio_lista FROM productos ORDER BY producto_id", engine
    )
    cargar(generar_facturas(clientes), "facturas", engine)

    facturas = pd.read_sql(
        "SELECT factura_id, fecha_emision, fecha_vencimiento, estado "
        "FROM facturas ORDER BY factura_id", engine
    )
    lineas, totales = generar_lineas(facturas, productos)
    cargar(lineas, "lineas_factura", engine)
    cargar(generar_pagos(facturas, totales), "pagos", engine)
