{{ config(materialized='view') }}

select
    *
from
    master_data.production_plan
