-- One row per currency per day: transfer rate + banknote rates,
-- plus the change compared with the previous published day.

with transfer as (

    select * from {{ ref('stg_bam__transfer_rates') }}

),

banknote as (

    select * from {{ ref('stg_bam__banknote_rates') }}

),

joined as (

    select
        t.rate_date,
        t.currency_code,
        t.mid_rate_per_unit_mad,
        b.buy_rate_per_unit_mad,
        b.sell_rate_per_unit_mad,
        b.spread_pct
    from transfer as t
    left join banknote as b
        on  b.rate_date = t.rate_date
        and b.currency_code = t.currency_code

),

with_previous as (

    select
        *,
        lag(mid_rate_per_unit_mad) over (
            partition by currency_code
            order by rate_date
        ) as previous_mid_rate
    from joined

)

select
    rate_date,
    currency_code,
    mid_rate_per_unit_mad,
    buy_rate_per_unit_mad,
    sell_rate_per_unit_mad,
    spread_pct,
    round(
        (mid_rate_per_unit_mad - previous_mid_rate) / previous_mid_rate * 100,
        4
    ) as daily_change_pct
from with_previous
