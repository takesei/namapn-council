with
--- final
final as (
  select
    *
  from {{ source("master", "versions_master") }}
)

select * from final
