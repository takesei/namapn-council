{{ config(materialized='view') }}

select
    *
from
    master_data_ordinary.resource_forecast
