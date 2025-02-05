with
--- final
final as (
  select
    *
  from {{ source("master", "companies") }}
)

select * from final
