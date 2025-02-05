with
--- final
final as (
  select
    *
  from {{ source("masters", "customers") }}
)

select * from final
