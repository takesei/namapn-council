{{ config(materialized='view') }}
with
  year_final as (
    select
      *
    from
      master_data_ordinary.years
  ),

  month_final as (
    select
      year_final.*,
      months.month_code,
      months.month_name
    from
      master_data_ordinary.months as months
    inner join
      year_final
    on
      months.year_code = year_final.year_code
  ),

  final as (
    select
      concat(
        month_final.year_code,
        month_final.month_code,
        dates.date_code
      ) as time_id,
      month_final.*,
      dates.date_code,
      dates.date_name
    from
      master_data_ordinary.dates as dates
    inner join
      month_final
    on
      dates.month_code = month_final.month_code
  )

select * from final
