# Toronto Airbnb Pricing Analytics

### What actually drives Airbnb prices in Toronto?

I analyzed **15,332 Toronto Airbnb listings** to examine how property characteristics, location, and booking features are associated with nightly prices. The analysis combines data cleaning, feature engineering, an interpretable log-price regression, model diagnostics, and a small Streamlit application for exploring pricing scenarios.

**[▶ Open the Live Pricing App](https://toronto-airbnb-pricing-analytics-jthhn2unchpj3ewyfbnyfq.streamlit.app/)**

> **Project note:** This repository is my independently rebuilt and extended portfolio version of a graduate analytics team project that I led. I rewrote the analysis as a reproducible Python workflow, reproduced the statistical model, and developed the interactive application presented here.

## Question

Airbnb prices vary considerably even among listings in the same city. Location is an obvious explanation, but it does not tell the whole story. I wanted to separate the association of location from differences in room type, capacity, bathrooms, amenities, and booking settings.

The analysis therefore focuses on one question:

**After accounting for observable listing characteristics, which factors are most strongly associated with nightly price in Toronto?**

The objective is explanatory rather than causal. I use an interpretable model so that the estimated relationships can be checked, discussed, and translated into practical pricing decisions.

## Data and sample

The project uses the **November 2025 Toronto detailed listings file from Inside Airbnb**.

- Raw snapshot: **21,468 listings × 79 fields**
- Final analytical sample: **15,332 listings**
- Outcome: nightly price in CAD
- Unit of analysis: one Airbnb listing

The raw file is not committed to this repository. Reproduction instructions are in [data/README.md](data/README.md).

The cleaning decisions are deliberately visible in the code. Prices outside the working range of $15–$900 are removed to limit the influence of implausible or highly atypical observations. The analysis is restricted to entire homes/apartments and private rooms so that the comparison is made across the two main listing formats rather than mixing them with structurally different hotel and shared-room products.

## Analysis

The workflow is:

`raw listing data → cleaning → exploratory analysis → feature engineering → log-price OLS → testing-down → diagnostics → holdout evaluation → interpretation`

Several raw fields were converted into variables with a clearer pricing interpretation. These include amenity count, host experience, distance to Union Station, entire-home status, shared-bathroom status, Superhost status, and instant booking.

I use **Union Station as a fixed downtown reference point** and calculate straight-line distance with the Haversine formula. It is not intended to represent travel time; it provides a consistent measure of centrality across listings.

Nightly price is strongly right-skewed, so the regression is estimated on `log(price)`. This also makes the coefficients easier to discuss in approximate percentage terms. I use OLS because the main goal is to understand the direction and magnitude of the relationships rather than maximize predictive accuracy with a less interpretable model.

The final specification retains eight predictors. A **70/30 train/test split** provides a simple check on out-of-sample performance. The Breusch–Pagan test indicates heteroskedasticity, so inference is reported using **HC3 robust standard errors**.

## Results

| Variable | Estimated association with nightly price |
|---|---:|
| Entire home vs. private room | **+43.8%** |
| Shared bathroom | **−21.0%** |
| Distance from downtown | **−2.7% per km** |
| Instant booking | **+2.4%** |
| Each additional amenity | **+0.4%** |

The model explains approximately **61.8% of the variation in log nightly price** on the test sample. Train and test R² are very similar, which suggests that the fitted relationship is not being driven by a large train/test performance gap.

The largest differences are associated with the listing itself. Entire-home status and bathroom arrangement have substantially larger estimated effects than instant booking or an additional amenity. Distance from downtown remains important, but its role is more incremental: each additional kilometre is associated with roughly a 2.7% lower nightly price, holding the included listing characteristics constant.

Superhost status and host experience were considered during model development but did not remain in the final testing-down specification. In this sample, they did not add enough explanatory value once property and listing characteristics were taken into account.

These estimates are **conditional associations, not causal effects**. For example, the 43.8% entire-home estimate should not be read as the price increase a host would obtain by converting a private room into an entire home.

## Practical implications

For pricing, I would begin with listings that are structurally comparable: room type, bathroom arrangement, capacity, bedrooms, and bathrooms. Location can then be used to adjust that benchmark rather than serving as the benchmark by itself.

Amenities and instant booking appear to be smaller pricing signals. They may still matter operationally, but the model does not support treating them as substitutes for the basic property characteristics that explain much larger price differences.

The results also suggest separating **reputation** from **price formation**. Superhost status may matter for trust, conversion, or occupancy even though it did not remain a meaningful nightly-price predictor in this specification. Those outcomes are outside the scope of the current dataset.

## Explore the analysis

This project has three complementary layers:

| Layer | Purpose |
|---|---|
| **Tableau / Power BI** | Explore the Toronto market, property mix, location, and pricing patterns |
| **Python / statistical model** | Estimate conditional associations with nightly price |
| **Streamlit** | Explore a user-defined pricing scenario |

The Tableau and Power BI dashboards use the same analytical dataset and are designed around two views: **Toronto Market Overview** and **Pricing Drivers**. Their design specifications, calculated fields, and DAX measures are documented in [dashboard/README.md](dashboard/README.md).

> Tableau Public and Power BI links will be added after the interactive reports are published. I do not include placeholder public links.

## Interactive pricing scenario

**[Launch the Streamlit app](https://toronto-airbnb-pricing-analytics-jthhn2unchpj3ewyfbnyfq.streamlit.app/)**

The app applies the final fitted coefficients to user-selected listing characteristics. I treat the output as a **model-implied pricing scenario**, not a forecast of the expected market price.

Because the model is estimated in log dollars, directly exponentiating the fitted log value introduces a retransformation issue if the objective is the conditional mean price in dollars. A production forecasting application would estimate and apply a retransformation adjustment (for example, a smearing factor) using the training residuals. I leave that adjustment out here rather than imply a level of forecasting precision that this cross-sectional explanatory model was not designed to provide.

Run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Repository structure

```text
.
├── app.py
├── data/
│   └── README.md
├── dashboard/
│   └── README.md
├── notebooks/
│   └── airbnb_pricing_analysis.ipynb
├── outputs/
│   └── model_results/
├── reports/
│   └── business_memo.md
├── src/
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── modeling.py
│   └── visualization.py
├── requirements.txt
└── README.md
```

## Reproduce the analysis

1. Download the November 2025 Toronto detailed listings file from Inside Airbnb.
2. Save it as `data/raw/toronto_listings_detail_nov.csv`.
3. Install the dependencies.
4. Run the notebook from top to bottom.

```bash
pip install -r requirements.txt
jupyter notebook notebooks/airbnb_pricing_analysis.ipynb
```

## Limitations and next steps

This is a **cross-sectional observational analysis**, so it cannot establish that changing a listing characteristic will cause the estimated change in price. The snapshot also does not directly model occupancy, booking conversion, seasonality, event demand, travel time, or live competitor inventory. In addition, accommodates, bedrooms, and bathrooms are related measures of listing size, so their individual coefficients should not be interpreted in isolation.

A useful next step would be to combine repeated listing snapshots with availability or booking-demand information. That would make it possible to distinguish persistent property differences from time-varying market conditions and move the project closer to a dynamic pricing problem.

## Author

**Lambert Tan**  
Master of Management in Analytics · Smith School of Business, Queen's University
