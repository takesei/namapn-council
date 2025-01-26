{{ config(materialized='view') }}

select
    customer_code,
    customer_name,
from master_data_ordinary.customers
