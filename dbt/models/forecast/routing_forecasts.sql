with
--- final
final as (
  select * from {{ source("forecast", "routing_forecasts") }}
)

select * from final
