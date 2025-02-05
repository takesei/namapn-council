with
--- load
type as (
  select
      *
  from {{ source("transactions", "transaction_types") }}
),
tran as (
  select
      *
  from {{ source("transactions", "transactions") }}
),
time as(
  select 
    *
  from {{ ref("times") }}
),

-- final
final as (
  select
    t.company_code,
    t.customer_code,
    ti.time_id,
    t.item_code,
    ty.transaction_type_name as transaction_type,
    t.storage_code
  from tran as t
  left join type as ty on t.transaction_type = ty.transaction_type_code
  left join time as ti on t.month = ti.month and 2025 = ti.year and 1 = ti.date
)

select * from final
