with
--- final
final as (
  select * from {{ source("forecasts", "resource_forecasts") }}
)

select * from final
