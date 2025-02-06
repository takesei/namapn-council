with
--- load
locs as (
  select
    *
  from {{ source("master", "locations_master") }}
),
plants as (
  select
    *
  from {{ source("master", "plants_master") }}
),
stores as (
  select
    *
  from {{ source("master", "storages_master") }}
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
    s.storage_code,
    s.storage_name,
    s.item_code,
    s.target_quantity,
    s.storage_unit_cost,
    l.longuitude,
    l.latitude,
    s.version
  from stores as s
  left join plants as p on s.plant_code = p.plant_code
  left join locs as l on p.location_code = l.location_code
  left join time as t on s.month_code = t.month and s.year_code = t.year and s.date_code = t.date
)


select * from final
