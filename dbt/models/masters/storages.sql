with
--- load
locs as (
  select
    *
  from {{ source("masters", "locations") }}
),
plants as (
  select
    *
  from {{ source("masters", "plants") }}
),
stores as (
  select
    *
  from {{ source("masters", "storages") }}
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
    s.version,
    p.is_active,
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
    l.latitude
  from stores as s
  left join plants as p on s.plant_code = p.plant_code
  left join locs as l on p.location_code = l.location_code
  left join time as t on s.month = t.month and 2025 = t.year and 1 = t.date
)


select * from final
