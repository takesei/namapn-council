{{ config(materialized='view') }}

with
  locations_final as (
    select
      location_code
    from
      master_data_ordinary.locations
  ),

  plants_final as (
    select
      locations_final.*,
      plants.plant_code,
      plants.plant_name
    from
      master_data_ordinary.plants as plants
    inner join
      locations_final
    on
      plants.location_code = locations_final.location_code
  ),

  final as (
    select
      lines.line_code,
      lines.month,
      lines.line_name,
      lines.production_cost,
      plants_final.plant_code
    from
      master_data_ordinary.lines as lines
    inner join
      plants_final
    on
      lines.plant_code = plants_final.plant_code
  )


select * from final
