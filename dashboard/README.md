# Tableau Dashboard

**[View the interactive Tableau Public dashboard](https://public.tableau.com/views/Toronto_Airbnb_Pricing_Analytics/Dashboard01MarketPulse)**

This folder documents the Tableau layer of the Toronto Airbnb Pricing Analytics project. The published workbook contains two connected dashboards built from the same 15,332-listing analytical sample.

- **Market Pulse** — descriptive market view of listing concentration, room type, nightly rate, and distance from downtown.
- **What Drives Nightly Price?** — conditional associations from the final log-price OLS model.

The two dashboards are connected with in-dashboard navigation.

## How the layers differ

- **Tableau / Market Pulse:** descriptive patterns in the November 2025 Toronto market.
- **Python / OLS:** conditional associations with nightly price after controlling for the other included model variables.
- **Streamlit:** model-implied pricing scenarios for user-selected listing characteristics.

Descriptive differences should not be interpreted as regression effects, and regression estimates are associations rather than causal effects.

## Dashboard 1 — Market Pulse

The market dashboard summarizes **15,332 Toronto Airbnb listings** from November 2025.

### KPIs

| KPI | Value |
|---|---:|
| Active listings | 15,332 |
| Median nightly rate | $125 |
| Median distance to downtown | 5.3 km |
| Entire-home share | 66.8% |

### Views

**Toronto listing map**  
Each point represents one listing. Colour distinguishes entire homes/apartments from private rooms. Tooltips provide neighbourhood, room type, nightly price, bedrooms, bathrooms, downtown distance, host status, and booking setting.

**Price by property type**  
Median nightly rate is **$167 for entire homes/apartments** and **$65 for private rooms**.

**Price by distance**  
Median nightly rates decline across the descriptive distance bands:

| Distance from downtown | Median nightly rate |
|---|---:|
| 0–2 km | $183 |
| 2–5 km | $140 |
| 5–10 km | $115 |
| 10+ km | $81 |

These are raw market summaries, not the model's estimated distance coefficient.

### Filters

The published dashboard supports filtering by room type, bedrooms, distance band, host status, and booking setting.

## Dashboard 2 — What Drives Nightly Price?

The second dashboard presents selected business-facing coefficients from the final multivariate log-price OLS model.

| Driver | Estimated price difference |
|---|---:|
| Entire home vs. private room | +43.8% |
| Instant booking | +2.4% |
| Each additional amenity | +0.4% |
| Distance from downtown | -2.7% per km |
| Shared bathroom | -21.0% |

The model uses **15,332 listings** and achieves **test R² = 0.619** (0.6185 unrounded). HC3 robust standard errors are used for inference.

Property characteristics show the largest estimated price differences. Entire-home listings are associated with a 43.8% premium relative to private rooms, while shared bathrooms are associated with a 21.0% discount. Each additional kilometre from downtown is associated with a 2.7% decrease in nightly price, holding the other modeled characteristics constant.

## Tableau data

The market dashboard uses a cleaned 19-field Tableau dataset with listing-level geography and selected analytical fields:

`price`, `latitude`, `longitude`, `neighbourhood`, `room_type`, `accommodates`, `bedrooms`, `bathrooms`, `shared_bathroom`, `entire_home`, `distance_to_downtown_km`, `amenity_count`, `instant_bookable`, `superhost`, `host_experience_years`, `distance_band`, `bathroom_type`, `booking_setting`, and `host_status`.

The processed listing-level CSV is excluded from GitHub through `.gitignore`. The regression-facing values are reproducible from the Python modeling workflow and the files under `outputs/model_results/`.

## Model-effects export

The Tableau model-effects view uses five selected coefficients from the fitted model. The export helper is implemented in `src/modeling.py`, and the notebook calls it after fitting the final model.

The complete fitted coefficient table remains available in:

`outputs/model_results/final_coefficients.csv`

Model performance and diagnostic statistics are stored in:

`outputs/model_results/model_metrics.json`

## Interpretation

The Tableau workbook is intended as a portfolio-facing analytical product rather than a causal pricing tool. The first dashboard shows what is observed in the market; the second shows conditional model estimates. Keeping those two views separate avoids treating descriptive price gaps as if they were regression results.

## Source

Inside Airbnb · Toronto detailed listings · November 2025
