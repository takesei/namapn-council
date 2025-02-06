with
--- final
final as (
  select
    *
  from {{ source("master", "customers_master") }}
)

select * from final
