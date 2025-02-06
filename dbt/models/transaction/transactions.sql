with
--- load
type as (
  select
      *
  from {{ source("transaction", "transaction_types_master") }}
),
tran as (
  select
      *
  from {{ source("transaction", "transactions_raw") }}
),
time as(
  select 
    *
  from {{ ref("times") }}
),

-- final
final as (
  select
    ti.time_id,
    t.company_code,
    t.customer_code,
    t.item_code,
    ty.transaction_type_name as transaction_type,
    t.storage_code,
    t.price,
    t.version
  from tran as t
  left join type as ty on t.transaction_type_code = ty.transaction_type_code
  left join time as ti on t.month_code = ti.month and t.year_code = ti.year and t.date_code = ti.date
)

select * from final
