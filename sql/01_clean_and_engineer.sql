-- 01_clean_and_engineer.sql
-- SQL (DuckDB) version of src/data_cleaning.py + src/feature_engineering.py.
--
-- Reads the raw Inside Airbnb snapshot and builds
--   listings_clean    cleaned listings (same rules and order as clean_listings)
--   listing_features  the 11 modelling columns (same as engineer_features), plus
--                     listing_id and neighbourhood_cleansed for exploration queries
-- and returns the cleaning funnel (rows remaining after each rule).
--
-- The runner sets the variable raw_file (default data/raw/toronto_listings_detail_nov.csv).
--
-- The funnel query at the end is saved by the runner as cleaning_funnel.csv.

CREATE OR REPLACE MACRO snapshot_date() AS DATE '2025-11-11';

-- Straight-line distance in km (same formula as _haversine in feature_engineering.py).
CREATE OR REPLACE MACRO haversine_km(lat1, lon1, lat2, lon2) AS
    2 * 6371.0 * asin(sqrt(
        pow(sin((radians(lat2) - radians(lat1)) / 2), 2)
        + cos(radians(lat1)) * cos(radians(lat2))
          * pow(sin((radians(lon2) - radians(lon1)) / 2), 2)));

-- All columns are read as text and cast explicitly below, like pd.to_numeric(errors='coerce').
-- nullstr lists the strings pandas treats as missing by default.
CREATE OR REPLACE TEMP VIEW raw_listings AS
SELECT * FROM read_csv(getvariable('raw_file'), header = true, all_varchar = true,
    strict_mode = false,
    nullstr = ['', 'NA', 'N/A', 'n/a', 'NaN', 'nan', 'NULL', 'null', 'None', '<NA>', '#N/A']);

-- One pass: typed fields, parsed price / bathrooms, and one boolean flag per cleaning rule.
CREATE OR REPLACE TABLE listings_staged AS
WITH typed AS (
    SELECT
        id                                                              AS listing_id,
        TRY_CAST(REPLACE(REPLACE(price, '$', ''), ',', '') AS DOUBLE)   AS price,
        TRY_CAST(latitude  AS DOUBLE)                                   AS latitude,
        TRY_CAST(longitude AS DOUBLE)                                   AS longitude,
        room_type,
        TRY_CAST(bedrooms AS DOUBLE)                                    AS bedrooms,
        bathrooms_text,
        TRY_CAST(accommodates AS BIGINT)                                AS accommodates,
        amenities,
        host_since,
        host_is_superhost,
        instant_bookable,
        neighbourhood_cleansed,
        has_availability,
        TRY_CAST(number_of_reviews AS BIGINT)                           AS number_of_reviews,
        TRY_CAST(availability_365  AS BIGINT)                           AS availability_365
    FROM raw_listings
),
parsed AS (
    SELECT
        *,
        -- "1.5 baths" -> 1.5, "Half-bath" / "Shared half-bath" -> 0.5, otherwise NULL
        CASE
            WHEN bathrooms_text IS NULL THEN NULL
            WHEN lower(trim(bathrooms_text)) LIKE '%half%' THEN 0.5
            ELSE TRY_CAST(regexp_split_to_array(lower(trim(bathrooms_text)), '\s+')[1] AS DOUBLE)
        END AS bathrooms,
        CAST(COALESCE(lower(bathrooms_text) LIKE '%shared%', FALSE) AS TINYINT) AS is_shared_bath
    FROM typed
)
SELECT
    *,
    -- one flag per rule in clean_listings(), in the same order
    COALESCE(price BETWEEN 15 AND 900, FALSE)                                  AS ok_price,
    bedrooms IS NOT NULL                                                       AS ok_bedrooms,
    COALESCE(bathrooms > 0 AND bathrooms <= 10, FALSE)                         AS ok_bathrooms,
    has_availability IS NOT NULL                                               AS ok_availability,
    host_since IS NOT NULL                                                     AS ok_host_since,
    NOT (COALESCE(availability_365, 0) = 0 AND COALESCE(number_of_reviews, 0) = 0)
                                                                               AS ok_active,
    COALESCE(room_type IN ('Entire home/apt', 'Private room'), FALSE)          AS ok_room_type
FROM parsed;

CREATE OR REPLACE TABLE listings_clean AS
SELECT
    listing_id, price, latitude, longitude, room_type, bedrooms, bathrooms, is_shared_bath,
    accommodates, amenities, host_since,
    COALESCE(host_is_superhost, 'f') AS host_is_superhost,
    instant_bookable, neighbourhood_cleansed, has_availability, number_of_reviews, availability_365
FROM listings_staged
WHERE ok_price AND ok_bedrooms AND ok_bathrooms AND ok_availability
  AND ok_host_since AND ok_active AND ok_room_type;

CREATE OR REPLACE TABLE listing_features AS
WITH f AS (
    SELECT
        listing_id,
        neighbourhood_cleansed,
        price,
        bedrooms,
        bathrooms,
        is_shared_bath,
        accommodates,
        CAST(host_is_superhost = 't' AS TINYINT)                         AS host_is_superhost,
        CAST(COALESCE(instant_bookable = 't', FALSE) AS TINYINT)         AS instant_bookable,
        -- json_array_length of the amenities list; unparseable or missing -> 0
        COALESCE(json_array_length(TRY_CAST(amenities AS JSON)), 0)      AS amenity_count,
        (snapshot_date() - TRY_CAST(host_since AS DATE)) / 365.25        AS host_experience_years,
        haversine_km(latitude, longitude, 43.6455, -79.3807)             AS distance_to_downtown_km,
        CAST(room_type = 'Entire home/apt' AS TINYINT)                   AS is_entire_home
    FROM listings_clean
)
SELECT * FROM f
WHERE price IS NOT NULL AND bedrooms IS NOT NULL AND bathrooms IS NOT NULL
  AND is_shared_bath IS NOT NULL AND accommodates IS NOT NULL
  AND host_is_superhost IS NOT NULL AND instant_bookable IS NOT NULL
  AND amenity_count IS NOT NULL AND host_experience_years IS NOT NULL
  AND distance_to_downtown_km IS NOT NULL AND is_entire_home IS NOT NULL;

-- name: cleaning_funnel
-- Rows remaining after each rule, in the order clean_listings() applies them.
WITH steps AS (
    SELECT 1 AS step_no, 'raw listings' AS step, COUNT(*) AS rows_remaining
    FROM listings_staged
    UNION ALL SELECT 2, 'price parsed and between $15 and $900',
        COUNT(*) FILTER (WHERE ok_price) FROM listings_staged
    UNION ALL SELECT 3, '+ bedrooms present',
        COUNT(*) FILTER (WHERE ok_price AND ok_bedrooms) FROM listings_staged
    UNION ALL SELECT 4, '+ bathrooms parsed, 0 < bathrooms <= 10',
        COUNT(*) FILTER (WHERE ok_price AND ok_bedrooms AND ok_bathrooms) FROM listings_staged
    UNION ALL SELECT 5, '+ has_availability present',
        COUNT(*) FILTER (WHERE ok_price AND ok_bedrooms AND ok_bathrooms AND ok_availability) FROM listings_staged
    UNION ALL SELECT 6, '+ host_since present',
        COUNT(*) FILTER (WHERE ok_price AND ok_bedrooms AND ok_bathrooms AND ok_availability
                           AND ok_host_since) FROM listings_staged
    UNION ALL SELECT 7, '+ not inactive (no availability and no reviews)',
        COUNT(*) FILTER (WHERE ok_price AND ok_bedrooms AND ok_bathrooms AND ok_availability
                           AND ok_host_since AND ok_active) FROM listings_staged
    UNION ALL SELECT 8, '+ entire home/apt or private room (= listings_clean)',
        COUNT(*) FROM listings_clean
    UNION ALL SELECT 9, 'listing_features (no missing model inputs)',
        COUNT(*) FROM listing_features
)
SELECT
    step_no, step, rows_remaining,
    COALESCE(LAG(rows_remaining) OVER (ORDER BY step_no) - rows_remaining, 0) AS rows_removed,
    ROUND(100.0 * rows_remaining / FIRST_VALUE(rows_remaining) OVER (ORDER BY step_no), 1)
                                                                              AS pct_of_raw
FROM steps
ORDER BY step_no;
