-- One row per payment; money stored as exact decimals
with source as (

    select * from {{ source('erp', 'pagos') }}

),

cleaned as (

    select
        pago_id,
        factura_id,
        cast(fecha_pago as date)       as fecha_pago,
        cast(monto as decimal(18, 2))  as monto,
        lower(trim(metodo))            as metodo,
        actualizado_en,
        _loaded_at
    from source

)

select * from cleaned
