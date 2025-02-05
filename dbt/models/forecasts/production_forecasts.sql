with
--- final
final as (
  select * from {{ source("forecasts", "production_forecasts") }}
)

select * from final
