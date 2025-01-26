{{ config(materialized='view') }}

with
  items_types_final as (
    select
      item_type_code,
      item_type_name
    from
      master_data_ordinary.item_types
  ),

  materials_final as (
    select
      material_code,
      material_name,
      item_type_code
    from
      master_data_ordinary.materials
  ),

  finished_goods_final as (
    select
      finished_goods_code,
      finished_goods_name,
      item_type_code
    from
      master_data_ordinary.finished_goods
  ),

  union_fg_mat as (
    select
      materials_final.item_type_code as item_code,
      materials_final.material_code as resource_code,
      materials_final.material_name as item_name
    from
      materials_final

    union all

    select
      finished_goods_final.item_type_code as item_code,
      item_type_code as resource_code,
      finished_goods_name as item_name
    from
      finished_goods_final
  ),

  final as (
    select
      union_fg_mat.*,
      items_types_final.item_type_code
    from
      union_fg_mat
    inner join
      items_types_final
    on
      union_fg_mat.item_code = items_types_final.item_type_code
  )


select * from final