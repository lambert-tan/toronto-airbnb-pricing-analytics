-- 02_quality_checks.sql
-- Checks on the tables built by 01. One row per check: (check_name, observed, expected, passed).
-- scripts/run_sql_pipeline.py exits non-zero if any check fails.
--
-- The last two checks compare with the sample sizes reported in the README
-- (21,468 raw listings; 15,332 in the final analytical sample). They only run
-- with --check-known-totals, i.e. on the real Inside Airbnb file.
--
-- name: quality_checks

WITH checks AS (
    SELECT 'price_within_15_900' AS check_name,
           COUNT(*) FILTER (WHERE price < 15 OR price > 900) AS observed, 0 AS expected
    FROM listings_clean

    UNION ALL
    SELECT 'bathrooms_within_0_10',
           COUNT(*) FILTER (WHERE NOT (bathrooms > 0 AND bathrooms <= 10)), 0
    FROM listings_clean

    UNION ALL
    SELECT 'only_two_room_types',
           COUNT(*) FILTER (WHERE room_type NOT IN ('Entire home/apt', 'Private room')), 0
    FROM listings_clean

    UNION ALL
    SELECT 'listing_id_unique_in_raw',
           COUNT(listing_id) - COUNT(DISTINCT listing_id), 0
    FROM listings_staged

    UNION ALL
    SELECT 'no_inactive_listings',
           COUNT(*) FILTER (WHERE COALESCE(availability_365, 0) = 0
                              AND COALESCE(number_of_reviews, 0) = 0), 0
    FROM listings_clean

    UNION ALL
    SELECT 'no_missing_model_inputs',
           COUNT(*) FILTER (WHERE price IS NULL OR bedrooms IS NULL OR bathrooms IS NULL
                              OR accommodates IS NULL OR amenity_count IS NULL
                              OR host_experience_years IS NULL OR distance_to_downtown_km IS NULL), 0
    FROM listing_features

    UNION ALL
    SELECT 'binary_flags_are_0_or_1',
           COUNT(*) FILTER (WHERE is_shared_bath NOT IN (0, 1) OR host_is_superhost NOT IN (0, 1)
                              OR instant_bookable NOT IN (0, 1) OR is_entire_home NOT IN (0, 1)), 0
    FROM listing_features

    UNION ALL
    -- Toronto listings should sit within ~100 km of Union Station; more means bad coordinates.
    SELECT 'distance_plausible_0_100km',
           COUNT(*) FILTER (WHERE distance_to_downtown_km < 0 OR distance_to_downtown_km > 100), 0
    FROM listing_features

    UNION ALL
    SELECT 'host_experience_not_negative',
           COUNT(*) FILTER (WHERE host_experience_years < 0), 0
    FROM listing_features

    UNION ALL
    SELECT 'known_raw_rows_21468',
           (SELECT COUNT(*) FROM listings_staged),
           CASE WHEN getvariable('check_known_totals') THEN 21468
                ELSE (SELECT COUNT(*) FROM listings_staged) END

    UNION ALL
    SELECT 'known_final_rows_15332',
           (SELECT COUNT(*) FROM listing_features),
           CASE WHEN getvariable('check_known_totals') THEN 15332
                ELSE (SELECT COUNT(*) FROM listing_features) END
)
SELECT check_name, observed, expected, observed = expected AS passed
FROM checks;
