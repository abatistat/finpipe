CREATE TABLE clientes (
    cliente_id     SERIAL PRIMARY KEY,
    nombre         TEXT NOT NULL,
    pais           TEXT NOT NULL,
    segmento       TEXT NOT NULL,
    dias_credito   INTEGER NOT NULL DEFAULT 30,
    fecha_alta     DATE NOT NULL
);

CREATE TABLE productos (
    producto_id    SERIAL PRIMARY KEY,
    nombre         TEXT NOT NULL,
    categoria      TEXT NOT NULL,
    precio_lista   NUMERIC(12,2) NOT NULL,
    costo_unitario NUMERIC(12,2) NOT NULL
);

CREATE TABLE facturas (
    factura_id        SERIAL PRIMARY KEY,
    cliente_id        INTEGER NOT NULL REFERENCES clientes(cliente_id),
    fecha_emision     DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    moneda            CHAR(3) NOT NULL DEFAULT 'USD',
    estado            TEXT NOT NULL CHECK (estado IN ('abierta', 'pagada', 'anulada'))
);

CREATE TABLE lineas_factura (
    linea_id        SERIAL PRIMARY KEY,
    factura_id      INTEGER NOT NULL REFERENCES facturas(factura_id),
    producto_id     INTEGER NOT NULL REFERENCES productos(producto_id),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12,2) NOT NULL,
    descuento_pct   NUMERIC(5,2) NOT NULL DEFAULT 0
);

CREATE TABLE pagos (
    pago_id     SERIAL PRIMARY KEY,
    factura_id  INTEGER NOT NULL REFERENCES facturas(factura_id),
    fecha_pago  DATE NOT NULL,
    monto       NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    metodo      TEXT NOT NULL
);
