with
--- final
final as (
  select
    *
  from {{ source("master", "bom_trees") }}
)

select * from final
