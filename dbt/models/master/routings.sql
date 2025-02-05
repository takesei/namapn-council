with
--- final
final as (
  select
    *
  from {{ source("master", "routings") }}
)

select * from final
