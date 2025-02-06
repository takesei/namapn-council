with
--- final
final as (
  select
    *
  from {{ source("master", "routings_master") }}
)

select * from final
