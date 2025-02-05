with
--- final
final as (
  select * from {{ source("forecast", "resource_forecasts") }}
)

select * from final
