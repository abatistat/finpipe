-- Customer dimension: one row per customer
select
    cliente_id,
    nombre,
    pais,
    segmento,
    dias_credito,
    fecha_alta
from {{ ref('stg_clientes') }}
