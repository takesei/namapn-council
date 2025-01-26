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
      storages.storage_code,
      storages.month,
      storages.storage_name,
      storages.storage_unit_cost,
      plants_final.plant_code
    from
      master_data_ordinary.storages as storages
    inner join
      plants_final
    on
      storages.plant_code = plants_final.plant_code
  )


select * from final
