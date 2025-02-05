with
--- load
mat as (
  select
    *
  from {{ source("masters", "materials") }}
),
type as (
  select
    *
  from {{ source("masters", "item_types") }}
),

--- final
final as (
  select
    m.material_code,
    m.material_name,
    m.item_code,
    m.materials_volume,
    m.is_active,
    m.version,
    t.item_type_name as item_type
  from mat as m
  left join type as t on m.item_type_code = t.item_type_code
)

select * from final
