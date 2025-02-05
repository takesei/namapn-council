with
--- load
year as (
  select
    *
  from
    {{ source("masters", "years") }}
),
month as (
  select
    *
  from
    {{ source("masters", "months") }}
),
date as (
  select
    *
  from
    {{ source("masters", "dates") }}
),

---final
final as (
  select
    concat(
      y.year_code,
      '-',
      m.month_code,
      '-',
      d.date_code
    ) as time_id,
    y.year_code as year,
    y.year_name,
    m.month_code as month,
    m.month_name,
    d.date_code as date,
    d.date_name,
    d.version
  from date as d
  left join month as m on d.month_code = m.month_code and d.version = m.version
  left join year as y on m.year_code = y.year_code and m.version = y.version
)

select * from final
