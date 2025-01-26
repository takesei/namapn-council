{{ config(materialized='view') }}

select
    company_code,
    company_name,
from master_data.companies
