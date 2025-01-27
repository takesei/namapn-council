{{ config(materialized='view') }}

select
    *
from
    master_data.transactions
