{{ config(materialized='view') }}

select
    *
from
    master_data.sales_plan
