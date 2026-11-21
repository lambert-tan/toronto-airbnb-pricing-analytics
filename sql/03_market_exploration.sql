-- 03_market_exploration.sql
-- Descriptive cuts of the cleaned Toronto listings. Each query is tagged with "-- name:";
-- the runner saves it to outputs/sql_results/<name>.csv.
--
-- These are raw (unadjusted) price comparisons. They complement the regression in the
-- notebook, which estimates the same differences holding other listing traits constant.

-- name: price_rule_impact
-- How many listings the $15-$900 working range removes, and from which side.
SELECT
    CASE WHEN price IS NULL  THEN 'price missing or unparseable'
         WHEN price < 15     THEN 'below $15 (removed)'
         WHEN price > 900    THEN 'above $900 (removed)'
         ELSE                     'kept' END                      AS price_group,
    COUNT(*)                                                      AS listings,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)            AS pct_of_raw,
    ROUND(MIN(price), 2)                                          AS min_price,
    ROUND(MAX(price), 2)                                          AS max_price
FROM listings_staged
GROUP BY 1
ORDER BY listings DESC;

-- name: price_by_room_type_and_size
-- Median and interquartile price by room type and number of bedrooms (4+ pooled).
SELECT
    CASE WHEN is_entire_home = 1 THEN 'Entire home/apt' ELSE 'Private room' END AS room_type,
    CASE WHEN bedrooms >= 4 THEN '4+' ELSE CAST(CAST(bedrooms AS INTEGER) AS VARCHAR) END
                                                              AS bedrooms,
    COUNT(*)                                                  AS listings,
    ROUND(quantile_cont(price, 0.25), 0)                      AS p25_price,
    ROUND(quantile_cont(price, 0.50), 0)                      AS median_price,
    ROUND(quantile_cont(price, 0.75), 0)                      AS p75_price,
    ROUND(AVG(price), 0)                                      AS mean_price
FROM listing_features
GROUP BY ALL
HAVING COUNT(*) >= 30
ORDER BY 1, 2;

-- name: neighbourhood_price_ranking
-- Neighbourhoods with at least 100 listings, ranked by median nightly price, with the premium
-- over the city-wide median. Mix of room types differs by area, so read with the next query.
WITH city AS (SELECT quantile_cont(price, 0.5) AS city_median FROM listing_features)
SELECT
    f.neighbourhood_cleansed                                  AS neighbourhood,
    COUNT(*)                                                  AS listings,
    ROUND(AVG(f.is_entire_home), 3)                           AS share_entire_home,
    ROUND(quantile_cont(f.price, 0.5), 0)                     AS median_price,
    ROUND(quantile_cont(f.price, 0.5) / ANY_VALUE(c.city_median) - 1, 3) AS premium_vs_city_median,
    ROUND(quantile_cont(f.distance_to_downtown_km, 0.5), 1)   AS median_km_to_union,
    RANK() OVER (ORDER BY quantile_cont(f.price, 0.5) DESC)   AS price_rank
FROM listing_features f CROSS JOIN city c
GROUP BY f.neighbourhood_cleansed
HAVING COUNT(*) >= 100
ORDER BY price_rank
LIMIT 20;

-- name: distance_band_pricing
-- Median price by distance band from Union Station, separately for each room type.
SELECT
    CASE WHEN distance_to_downtown_km < 2  THEN '1) under 2 km'
         WHEN distance_to_downtown_km < 5  THEN '2) 2-5 km'
         WHEN distance_to_downtown_km < 10 THEN '3) 5-10 km'
         WHEN distance_to_downtown_km < 20 THEN '4) 10-20 km'
         ELSE                                   '5) 20+ km' END         AS distance_band,
    CASE WHEN is_entire_home = 1 THEN 'Entire home/apt' ELSE 'Private room' END AS room_type,
    COUNT(*)                                                            AS listings,
    ROUND(quantile_cont(price, 0.5), 0)                                 AS median_price
FROM listing_features
GROUP BY ALL
HAVING COUNT(*) >= 30
ORDER BY 1, 2;

-- name: shared_bath_gap
-- Median price with a private vs shared bathroom, within each room type.
SELECT
    CASE WHEN is_entire_home = 1 THEN 'Entire home/apt' ELSE 'Private room' END AS room_type,
    COUNT(*) FILTER (WHERE is_shared_bath = 0)                                  AS private_bath_listings,
    COUNT(*) FILTER (WHERE is_shared_bath = 1)                                  AS shared_bath_listings,
    ROUND(quantile_cont(price, 0.5) FILTER (WHERE is_shared_bath = 0), 0)       AS median_private_bath,
    ROUND(quantile_cont(price, 0.5) FILTER (WHERE is_shared_bath = 1), 0)       AS median_shared_bath,
    ROUND(quantile_cont(price, 0.5) FILTER (WHERE is_shared_bath = 1)
          / quantile_cont(price, 0.5) FILTER (WHERE is_shared_bath = 0) - 1, 3) AS shared_vs_private
FROM listing_features
GROUP BY ALL;

-- name: amenity_quartile_pricing
-- Listings split into amenity-count quartiles within their room type (NTILE window),
-- then median price per quartile.
WITH q AS (
    SELECT *, NTILE(4) OVER (PARTITION BY is_entire_home ORDER BY amenity_count) AS amenity_quartile
    FROM listing_features
)
SELECT
    CASE WHEN is_entire_home = 1 THEN 'Entire home/apt' ELSE 'Private room' END AS room_type,
    amenity_quartile,
    COUNT(*)                                  AS listings,
    MIN(amenity_count)                        AS min_amenities,
    MAX(amenity_count)                        AS max_amenities,
    ROUND(quantile_cont(price, 0.5), 0)       AS median_price
FROM q
GROUP BY ALL
ORDER BY 1, 2;

-- name: host_traits_by_room_type
-- Median price by Superhost and instant-booking status within each room type.
SELECT
    CASE WHEN is_entire_home = 1 THEN 'Entire home/apt' ELSE 'Private room' END AS room_type,
    CASE WHEN host_is_superhost = 1 THEN 'Superhost' ELSE 'Not Superhost' END    AS host_status,
    CASE WHEN instant_bookable = 1 THEN 'Instant book' ELSE 'Request to book' END AS booking_mode,
    COUNT(*)                                  AS listings,
    ROUND(quantile_cont(price, 0.5), 0)       AS median_price
FROM listing_features
GROUP BY ALL
HAVING COUNT(*) >= 30
ORDER BY 1, 2, 3;
