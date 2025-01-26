{{ config(materialized='view') }}

select
    *
from
    master_data_ordinary.production_plan
