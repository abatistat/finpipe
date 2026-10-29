-- One row per invoice, cleaned from the raw ERP copy
with source as (

    select * from {{ source('erp', 'facturas') }}

),

cleaned as (

    select
        factura_id,
        cliente_id,
        cast(fecha_emision as date)      as fecha_emision,
        cast(fecha_vencimiento as date)  as fecha_vencimiento,
        upper(trim(moneda))              as moneda,
        lower(trim(estado))              as estado,
        lower(trim(estado)) = 'anulada'  as es_anulada,
        actualizado_en,
        _loaded_at
    from source

)

select * from cleaned
