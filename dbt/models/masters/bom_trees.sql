with
--- final
final as (
  select
    *
  from {{ source("masters", "bom_trees") }}
)

select * from final
