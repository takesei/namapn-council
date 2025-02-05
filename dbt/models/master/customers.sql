with
--- final
final as (
  select
    *
  from {{ source("master", "customers") }}
)

select * from final
