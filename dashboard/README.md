# BI Dashboards

This folder contains the design specification for the Tableau layer of the Toronto Airbnb Pricing Analytics project.

The statistical model and the dashboards answer different questions:

- **Python / OLS:** Which listing characteristics are associated with nightly price after controlling for other included characteristics?
- **Tableau:** What does the Toronto Airbnb market look like across listing types, price ranges, and distance from downtown?
- **Streamlit:** What model-implied nightly price is produced for a user-defined listing scenario?

## Dashboard 1 — Toronto Market Overview

The first dashboard should help a user explore the market before looking at the regression model.

### KPI cards
- Listings in current filter
- Median nightly price
- Median distance to downtown
- Share of entire-home listings

### Recommended views
1. **Toronto listing map** — latitude/longitude, coloured by nightly price or room type.
2. **Median price by room type** — compare entire homes and private rooms.
3. **Price by distance band** — 0–2 km, 2–5 km, 5–10 km, and 10+ km from the downtown reference point.
4. **Price by capacity / bedrooms** — show how price changes with listing size.

### Filters
- Room type
- Price range
- Bedrooms
- Bathrooms
- Superhost
- Instant bookable
- Distance band

## Dashboard 2 — Pricing Drivers

This dashboard connects descriptive market patterns with the final regression results.

### Model results
| Driver | Estimated association |
|---|---:|
| Entire home vs. private room | +43.8% |
| Shared bathroom | -21.0% |
| Distance from downtown | -2.7% per km |
| Instant booking | +2.4% |
| Each additional amenity | +0.4% |

### Recommended views
1. **Coefficient impact chart** — horizontal bars for the five interpretable effects above.
2. **Price vs. distance** — scatter plot or binned view showing the raw relationship between nightly price and downtown distance.
3. **Room type × bathroom arrangement** — compare median prices across structurally different listings.
4. **Model context panel** — 15,332 listings; test R² ≈ 0.618; log-price OLS; HC3 robust inference.

The dashboard should clearly distinguish **descriptive charts** from **regression estimates**. Raw differences in a chart are not the same as conditional model effects.

## Tableau implementation

Recommended workbook structure:

```text
Toronto Airbnb Pricing.twbx
├── Market Overview
├── Pricing Drivers
├── Map
├── Room Type Comparison
├── Distance Analysis
└── Model Effects
```

Suggested calculated field for distance band:

```text
IF [Distance To Downtown Km] < 2 THEN "0–2 km"
ELSEIF [Distance To Downtown Km] < 5 THEN "2–5 km"
ELSEIF [Distance To Downtown Km] < 10 THEN "5–10 km"
ELSE "10+ km"
END
```

Once published to Tableau Public, add the public dashboard URL to the main project README.

## Publishing

The finished portfolio version should include:

- a Tableau Public link to the interactive dashboard;
- screenshots of the Market Overview and Pricing Drivers views; and
- the Tableau workbook (`.twbx`) when it is suitable for public sharing.

The screenshots are important because they allow someone reviewing the GitHub repository to understand the dashboard without opening Tableau.

## Data fields

The dashboard layer should use the cleaned / engineered project data rather than the raw 79-column source file. At minimum, retain fields needed for:

- price
- latitude / longitude
- room type
- accommodates
- bedrooms
- bathrooms
- shared bathroom
- entire home
- distance to downtown
- amenity count
- instant bookable
- Superhost

Do not publish host-identifying fields that are unnecessary for the analysis.
