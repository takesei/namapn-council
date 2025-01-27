{{ config(materialized='view') }}

select
    finished_goods_code,
    finished_goods_name,
    finished_goods_volume,
    item_type_code
from master_data.finished_goods
