{{ config(materialized='view') }}

select
    routings_code,
    item_code,
    month,
    routings_name,
    quantity,
    cost,
from
    master_data.routing_forecasts
