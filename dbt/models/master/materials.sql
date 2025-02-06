with
--- load
mat as (
  select
    *
  from {{ source("master", "materials_master") }}
),
type as (
  select
    *
  from {{ source("master", "item_types_master") }}
),

--- final
final as (
  select
    m.material_code,
    m.material_name,
    m.item_code,
    t.item_type_name as item_type,
    m.material_volume
  from mat as m
  left join type as t on m.item_type_code = t.item_type_code
)

select * from final
