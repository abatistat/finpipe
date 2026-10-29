-- One row per product; money stored as exact decimals
with source as (

    select * from {{ source('erp', 'productos') }}

),

cleaned as (

    select
        producto_id,
        trim(nombre)                            as nombre,
        trim(categoria)                         as categoria,
        cast(precio_lista as decimal(18, 2))    as precio_lista,
        cast(costo_unitario as decimal(18, 2))  as costo_unitario,
        actualizado_en,
        _loaded_at
    from source

)

select * from cleaned
