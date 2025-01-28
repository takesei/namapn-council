{{ config(materialized='view') }}

select
    *
from
    master_data.routing
