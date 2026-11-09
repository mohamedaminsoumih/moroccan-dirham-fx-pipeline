-- Transfer rates (CoursVirement): one row per currency per day.
-- Extracts the JSON fields into typed columns.

with source as (

    select *
    from {{ source('bam', 'bam_rates') }}
    where endpoint = 'CoursVirement'

),

typed as (

    select
        rate_date,
        payload ->> 'libDevise'                    as currency_code,
        (payload ->> 'uniteDevise')::int           as currency_unit,
        (payload ->> 'moyen')::numeric(12, 4)      as mid_rate_mad,
        (payload ->> 'date')::timestamp            as published_at,
        extracted_at,
        loaded_at
    from source

)

select
    *,
    -- Some currencies are quoted per 100 units (e.g. JPY): bring all to 1 unit
    round(mid_rate_mad / currency_unit, 6) as mid_rate_per_unit_mad
from typed
