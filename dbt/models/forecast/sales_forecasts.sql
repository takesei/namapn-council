with
--- final
final as (
  select * from {{ source("forecast", "sales_forecasts") }}
)

select * from final
