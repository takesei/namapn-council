{{ config(materialized='view') }}

select
    material_code,
    material_name,
    materials_volume,
    item_type_code
from master_data.materials
