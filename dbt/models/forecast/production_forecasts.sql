with
--- final
final as (
  select * from {{ source("forecast", "production_forecasts") }}
)

select * from final
