with
--- final
final as (
  select * from {{ source("forecasts", "routing_forecasts") }}
)

select * from final
