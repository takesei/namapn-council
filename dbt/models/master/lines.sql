with
--- load
locs as (
  select
    *
  from {{ source("master", "locations") }}
),
plants as (
  select
    *
  from {{ source("master", "plants") }}
),
lines as (
  select
    *
  from {{ source("master", "lines") }}
),
time as(
  select 
    *
  from {{ ref("times") }}
),

--- final
final as (
  select
    t.time_id,
    l.location_code,
    l.location_name,
    p.plant_code,
    p.plant_name,
    s.line_code,
    s.line_name,
    s.capacity,
    s.production_cost
  from lines as s
  left join plants as p on s.plant_code = p.plant_code
  left join locs as l on p.location_code = l.location_code
  left join time as t on s.month_code = t.month and s.year_code = t.year and s.date_code = t.date
)


select * from final
