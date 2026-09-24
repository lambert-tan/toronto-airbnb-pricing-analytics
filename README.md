# Toronto Airbnb Pricing Analytics

### What actually drives Airbnb prices in Toronto?

An end-to-end analysis of **15,332 Toronto Airbnb listings**, moving from raw data and feature engineering to statistical modelling, business recommendations, and an interactive pricing estimator.

> **Project note:** This repository is my independently rebuilt and extended portfolio version of a graduate analytics team project that I led. I redesigned the workflow into a reproducible pipeline, reproduced the modelling process, and expanded the work into a business-facing analytics product.

## Business question

Airbnb hosts often rely on neighbourhood averages or reputation signals when setting a nightly rate. This project asks a more practical question:

**After controlling for listing characteristics, which factors are most strongly associated with nightly price in Toronto?**

The aim is not to build a black-box prediction model. I wanted a model that was statistically defensible, easy to explain, and useful for pricing decisions.

## Data

- **Source:** Inside Airbnb, Toronto, November 2025
- **Raw snapshot:** 21,468 listings and 79 fields
- **Final analysis sample:** 15,332 listings
- **Target:** nightly listing price

The large raw CSV is not stored in this repository. See `data/README.md` for the data setup.

## Workflow

`Raw data → data audit → cleaning → EDA → feature engineering → train/test split → log-price OLS → testing-down → diagnostics → HC3 robust inference → business recommendations → pricing estimator`

## Feature engineering

The analysis turns raw listing fields into variables that are easier to interpret in a pricing context:

- amenity count
- host experience
- straight-line distance to Union Station
- entire-home indicator
- shared-bathroom indicator
- Superhost indicator
- instant-booking indicator

## Modelling approach

Nightly price is right-skewed, so the dependent variable is transformed to `log(price)`. I use an interpretable OLS specification and a testing-down approach rather than optimizing only for predictive accuracy.

The final model retains eight predictors. I evaluate it using a 70/30 train/test split. A Breusch–Pagan test indicates heteroskedasticity, so HC3 robust standard errors are used for inference.

## What I found

| Driver | Estimated association with nightly price |
|---|---:|
| Entire home vs. private room | **+43.8%** |
| Shared bathroom | **−21.0%** |
| Distance from downtown | **−2.7% per km** |
| Instant booking | **+2.4%** |
| Each additional amenity | **+0.4%** |

The final model explains about **61.8% of log-price variation**, with similar train and test performance.

Superhost status and host experience did not remain meaningful pricing drivers in the final testing-down specification.

## Business interpretation

The results suggest a simple three-layer way to think about pricing:

1. **Start with the property itself.** Room type, bathroom setup and size create the largest differences.
2. **Use location as an adjustment.** Downtown proximity matters, but it should refine a comparable-property benchmark rather than define it.
3. **Fine-tune with operational features.** Instant booking and amenities offer smaller, more actionable adjustments.

## Interactive app

The Streamlit app turns the final model into a simple scenario tool. A user can change property characteristics and see the model-implied nightly price.

```bash
pip install -r requirements.txt
streamlit run app.py
```

The estimator is intended for scenario exploration, not as a production pricing engine.

## Repository structure

```text
.
├── app.py
├── data/
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

## Run the analysis

1. Download the November 2025 Toronto detailed listings file from Inside Airbnb.
2. Save it as `data/raw/toronto_listings_detail_nov.csv`.
3. Install the dependencies.
4. Run the notebook from top to bottom.

```bash
pip install -r requirements.txt
jupyter notebook notebooks/airbnb_pricing_analysis.ipynb
```

## Skills demonstrated

**Python · pandas · NumPy · statsmodels · scikit-learn · data cleaning · EDA · feature engineering · regression · robust inference · model validation · Streamlit · business storytelling**

## Limitations

This is a cross-sectional observational analysis, not a causal pricing experiment. It does not directly model seasonality, occupancy, booking conversion, guest demand, events, transit travel time, or live competitor inventory. Listing-size variables are also correlated, so their individual coefficients should not be interpreted in isolation.

## Author

**Lambert Tan**  
Master of Management in Analytics · Smith School of Business, Queen's University
