-- One row per currency per month: average, lowest, highest rate
-- and volatility (how much the rate moved during the month).

with daily as (

    select * from {{ ref('fct_exchange_rates_daily') }}

)

select
    date_trunc('month', rate_date)::date       as month,
    currency_code,
    count(*)                                   as published_days,
    round(avg(mid_rate_per_unit_mad), 6)       as avg_mid_rate_mad,
    min(mid_rate_per_unit_mad)                 as min_mid_rate_mad,
    max(mid_rate_per_unit_mad)                 as max_mid_rate_mad,
    round(stddev(daily_change_pct), 4)         as volatility_pct,
    round(avg(spread_pct), 2)                  as avg_spread_pct
from daily
group by 1, 2
