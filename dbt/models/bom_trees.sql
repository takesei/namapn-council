{{ config(materialized='view') }}

select
    *
from
    master_data.bom_trees
