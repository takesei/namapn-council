with
--- final
final as (
  select * from {{ source("forecasts", "sales_forecasts") }}
)

select * from final
