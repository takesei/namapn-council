with
--- load
fg as (
  select
    *
  from {{ source("master", "finished_goods_master") }}
),
type as (
  select
    *
  from {{ source("master", "item_types_master") }}
),

--- final
final as (
  select
    f.finished_goods_code,
    f.finished_goods_name,
    f.item_code,
    t.item_type_name as item_type,
    f.finished_goods_volume
  from fg as f
  left join type as t on f.item_type_code = t.item_type_code
)

select * from final
