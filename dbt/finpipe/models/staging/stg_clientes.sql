-- One row per customer
with source as (

    select * from {{ source('erp', 'clientes') }}

),

cleaned as (

    select
        cliente_id,
        trim(nombre)              as nombre,
        trim(pais)                as pais,
        trim(segmento)            as segmento,
        dias_credito,
        cast(fecha_alta as date)  as fecha_alta,
        actualizado_en,
        _loaded_at
    from source

)

select * from cleaned
