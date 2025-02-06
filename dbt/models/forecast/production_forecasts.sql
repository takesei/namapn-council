with
--- load
forecast as (
  select * from {{ source("forecast", "production_forecasts") }}
),
time as(
  select 
    *
  from {{ ref("times") }}
),

---final
final as (
  select
    f.version,
    t.time_id,
    f.line_code,
    f.item_code,
    f.quantity
  from forecast as f
  left join time as t on f.year_code = t.year and f.month_code = t.month and f.date_code = t.date
)

select * from final
