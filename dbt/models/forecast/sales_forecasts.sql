with
--- load
forecast as (
  select * from {{ source("forecast", "sales_forecasts_raw") }}
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
    f.company_code,
    f.customer_code,
    f.item_code,
    f.quantity
  from forecast as f
  left join time as t on f.year_code = t.year and f.month_code = t.month and f.date_code = t.date
)

select * from final
