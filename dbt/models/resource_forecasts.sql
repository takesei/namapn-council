{{ config(materialized='view') }}

select
    *
from
    master_data.resource_forecast
