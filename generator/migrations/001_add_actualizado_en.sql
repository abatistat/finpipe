-- 001: add actualizado_en to every ERP table to support incremental extraction.
-- Safe to run on a database that already has data, and safe to run twice.

-- Trigger function: stamp the current time on every UPDATE.
CREATE OR REPLACE FUNCTION set_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- clientes
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now();
CREATE INDEX IF NOT EXISTS ix_clientes_actualizado_en ON clientes (actualizado_en);
CREATE OR REPLACE TRIGGER trg_clientes_actualizado_en
    BEFORE UPDATE ON clientes FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();

-- productos
ALTER TABLE productos ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now();
CREATE INDEX IF NOT EXISTS ix_productos_actualizado_en ON productos (actualizado_en);
CREATE OR REPLACE TRIGGER trg_productos_actualizado_en
    BEFORE UPDATE ON productos FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();

-- facturas
ALTER TABLE facturas ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now();
CREATE INDEX IF NOT EXISTS ix_facturas_actualizado_en ON facturas (actualizado_en);
CREATE OR REPLACE TRIGGER trg_facturas_actualizado_en
    BEFORE UPDATE ON facturas FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();

-- lineas_factura
ALTER TABLE lineas_factura ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now();
CREATE INDEX IF NOT EXISTS ix_lineas_factura_actualizado_en ON lineas_factura (actualizado_en);
CREATE OR REPLACE TRIGGER trg_lineas_factura_actualizado_en
    BEFORE UPDATE ON lineas_factura FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();

-- pagos
ALTER TABLE pagos ADD COLUMN IF NOT EXISTS actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now();
CREATE INDEX IF NOT EXISTS ix_pagos_actualizado_en ON pagos (actualizado_en);
CREATE OR REPLACE TRIGGER trg_pagos_actualizado_en
    BEFORE UPDATE ON pagos FOR EACH ROW EXECUTE FUNCTION set_actualizado_en();
