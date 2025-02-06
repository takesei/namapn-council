with
--- final
final as (
  select
    *
  from {{ source("master", "bom_trees_master") }}
)

select * from final
