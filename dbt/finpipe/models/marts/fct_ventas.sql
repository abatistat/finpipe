-- Sales fact: one row per invoice line, with amounts and margin
-- descuento_pct comes as a percentage (0, 5, 10), so it is divided by 100
with lineas as (

    select * from {{ ref('stg_lineas_factura') }}

),

facturas as (

    select * from {{ ref('stg_facturas') }}

),

productos as (

    select * from {{ ref('stg_productos') }}

),

joined as (

    select
        l.linea_id,
        l.factura_id,
        f.cliente_id,
        l.producto_id,
        f.fecha_emision,
        f.moneda,
        f.estado,
        f.es_anulada,
        l.cantidad,
        l.precio_unitario,
        l.descuento_pct,
        p.costo_unitario,
        cast(l.cantidad * l.precio_unitario as decimal(18, 2))
            as importe_bruto,
        cast(l.cantidad * l.precio_unitario * (1 - l.descuento_pct / 100) as decimal(18, 2))
            as importe_neto,
        cast(l.cantidad * p.costo_unitario as decimal(18, 2))
            as costo_total
    from lineas l
    inner join facturas f on l.factura_id = f.factura_id
    inner join productos p on l.producto_id = p.producto_id

)

select
    *,
    importe_bruto - importe_neto  as importe_descuento,
    importe_neto - costo_total    as margen_bruto
from joined
