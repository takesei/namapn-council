with
--- load
forecast as (
  select * from {{ source("forecast", "routing_forecasts_raw") }}
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
    f.routings_code,
    f.routings_name,
    f.from_plants_code,
    f.to_plants_code,
    f.item_code,
    f.quantity,
    f.cost,
    f.unit_cost
  from forecast as f
  left join time as t on f.year_code = t.year and f.month_code = t.month and f.date_code = t.date
)

select * from final
