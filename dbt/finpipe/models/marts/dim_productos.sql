-- Product dimension: one row per product
select
    producto_id,
    nombre,
    categoria,
    precio_lista,
    costo_unitario
from {{ ref('stg_productos') }}
