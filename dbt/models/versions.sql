{{ config(materialized='view') }}

select
    versions_code,
    versions_name,
    is_active,
from master_data.versions
