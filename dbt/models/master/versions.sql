with
--- final
final as (
  select
    *
  from {{ source("master", "versions") }}
)

select * from final
