with
--- final
final as (
  select
    *
  from {{ source("masters", "routings") }}
)

select * from final
