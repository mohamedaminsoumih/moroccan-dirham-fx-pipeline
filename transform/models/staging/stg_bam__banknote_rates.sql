-- Banknote rates (CoursBBE): cash buy and sell prices at bank counters.
-- One row per currency per day.

with source as (

    select *
    from {{ source('bam', 'bam_rates') }}
    where endpoint = 'CoursBBE'

),

typed as (

    select
        rate_date,
        payload ->> 'libDevise'                         as currency_code,
        (payload ->> 'uniteDevise')::int                as currency_unit,
        (payload ->> 'achatClientele')::numeric(12, 4)  as buy_rate_mad,
        (payload ->> 'venteClientele')::numeric(12, 4)  as sell_rate_mad,
        (payload ->> 'date')::timestamp                 as published_at,
        extracted_at,
        loaded_at
    from source

),

-- The API sometimes returns the same currency twice for one day:
-- keep one row, the latest published
deduplicated as (

    select distinct on (rate_date, currency_code) *
    from typed
    order by rate_date, currency_code, published_at desc

)

select
    *,
    round(buy_rate_mad / currency_unit, 6)   as buy_rate_per_unit_mad,
    round(sell_rate_mad / currency_unit, 6)  as sell_rate_per_unit_mad,
    -- Bank margin: how much more you pay when buying vs selling (in %)
    round((sell_rate_mad - buy_rate_mad) / buy_rate_mad * 100, 2)
        as spread_pct
from deduplicated
