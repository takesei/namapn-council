with
--- load
fg as (
  select
    *
  from {{ source("masters", "finished_goods") }}
),
type as (
  select
    *
  from {{ source("masters", "item_types") }}
),

--- final
final as (
  select
    f.finished_goods_code,
    f.finished_goods_name,
    f.item_code,
    f.item_type_code,
    f.finished_goods_volume,
    f.is_active,
    f.version,
    t.item_type_name as item_type
  from fg as f
  left join type as t on f.item_type_code = t.item_type_code
)

select * from final
