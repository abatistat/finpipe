-- One row per invoice line; money stored as exact decimals
with source as (

    select * from {{ source('erp', 'lineas_factura') }}

),

cleaned as (

    select
        linea_id,
        factura_id,
        producto_id,
        cantidad,
        cast(precio_unitario as decimal(18, 2))  as precio_unitario,
        cast(descuento_pct as decimal(9, 4))     as descuento_pct,
        actualizado_en,
        _loaded_at
    from source

)

select * from cleaned
