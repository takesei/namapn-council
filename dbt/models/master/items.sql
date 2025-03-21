with
--- load
fg as (
  select * from {{ ref("finished_goods") }}
),
mat as (
  select * from {{ ref("materials") }}
),

--- logic
uitem as (
  select
    item_type,
    finished_goods_code as resource_code
  from
    fg

  union all

  select
    item_type,
    material_code as resource_code
  from
    mat
),

--- final
final as (
  select
    row_number() over() as item_id,
    *
  from uitem
)

select * from final
