with
--- final
final as (
  select
    *
  from {{ source("masters", "companies") }}
)

select * from final
