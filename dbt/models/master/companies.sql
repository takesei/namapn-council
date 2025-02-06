with
--- final
final as (
  select
    *
  from {{ source("master", "companies_master") }}
)

select * from final
