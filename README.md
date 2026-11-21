# 🏙️ Toronto Airbnb Pricing Analytics

A Toronto host has a two-bedroom apartment with a private bathroom. Which nearby listings would I use to benchmark its nightly rate? In the November 2025 sample, entire homes listed for a median of **CAD 167** and private rooms for **CAD 65**. Taking a neighbourhood average across both groups could give the host a poor starting price.

I led the original graduate team project and rebuilt the Python analysis and Streamlit app for this portfolio. I use three views of the same pricing question:

| If you want to… | Open | What to look for |
|---|---|---|
| Find comparable listings | [Tableau market dashboard](https://public.tableau.com/views/Toronto_Airbnb_Pricing_Analytics/Dashboard01MarketPulse) | Compare asking prices within a room type and distance band. |
| Explore a specific property | [Streamlit pricing app](https://toronto-airbnb-pricing-analytics-jthhn2unchpj3ewyfbnyfq.streamlit.app/) | Change the guest capacity, bathroom setup or distance and see how the fitted estimate moves. |
| Assess the pricing recommendation | [Host memo](reports/business_memo.md) · [Regression notebook](notebooks/airbnb_pricing_analysis.ipynb) | Follow the reasoning from observable listing differences to a benchmark a host could use. |

## Building the comparison set with SQL and Python

The Inside Airbnb snapshot contains 21,468 listings. Cleaning and restricting the analysis to entire homes and private rooms with nightly prices between CAD 15 and 900 leaves **15,332 listings**. DuckDB tracks how many records each filter removes. The Python model relates log nightly price to room type, guest capacity, bedrooms, bathrooms, shared-bathroom status, distance to Union Station, amenity count and instant booking.

The cleaning rules shape the question the model can answer. For example, a listing with zero available days and no reviews is excluded as potentially inactive. A calendar with no available nights alone is ambiguous: it could belong to a fully booked property or to one the host has taken off the market. The price limits also place luxury properties above CAD 900 outside this benchmark. [Python cleaning rules](src/data_cleaning.py)

The model uses a 70/30 train/test split. Test R² was **0.619** for log price, close to the training value of 0.618. A Breusch–Pagan test indicated unequal residual variance, so the reported inference uses HC3 robust standard errors. [Notebook](notebooks/airbnb_pricing_analysis.ipynb) · [Model metrics](outputs/model_results/model_metrics.json)

## What the regression adds to the dashboard

| Listing characteristic | Estimated difference in nightly price, other inputs held constant |
|---|---:|
| Entire home compared with a private room | +43.8% |
| Shared bathroom | −21.0% |
| One kilometre farther from Union Station | −2.7% |
| Instant booking enabled | +2.4% |
| One additional listed amenity | +0.4% |

For a two-bedroom apartment with a private bathroom, I would start with nearby entire homes of similar size. If few qualify, I would widen the search area before adding private rooms. The fitted location gradient gives a way to compare properties farther apart. The 43.8% room-type estimate comes from a log-price regression, so it cannot be subtracted from the raw median gap to assign the remainder to location or size. To recommend a rate that maximizes revenue, I would also need booked nights and realized prices. [Coefficient estimates](outputs/model_results/model_effects.csv) · [Host pricing memo](reports/business_memo.md)

## Applying the distance estimate to a CAD 200 comparable

Consider an entire two-bedroom apartment with a private bathroom. Suppose the closest comparable is an otherwise similar apartment five kilometres nearer Union Station. Using the fitted distance coefficient, the estimated asking-price ratio is `exp(5 × −0.02748) = 0.872`. If the comparable lists at CAD 200, the distance adjustment alone gives about **CAD 174**. Both prices in this example are illustrative. A lakefront location, a subway connection or a large event could make the comparison inappropriate even when the arithmetic is correct.

The model also associates an additional bedroom with a 9.8% higher asking price **at the same guest capacity**. Adding a bedroom while holding capacity fixed describes a different comparison from accommodating two extra guests. I would match both attributes when choosing comparable properties. For a specific listing, the held-out error matters too: mean absolute error was 0.321 in log-price units. The precision of the reported coefficient does not carry over to a dollar quote for an individual host. [Full coefficient table](outputs/model_results/final_coefficients.csv) · [Model implementation](src/modeling.py)

## What a revenue decision would require

A host earns revenue on booked nights. To evaluate a price change, I would collect quoted rates, nights genuinely offered, nights booked and realized revenue for comparable dates. Revenue per available night would be the primary outcome, with occupancy and realized nightly rate explaining the trade-off. Repeated observations across weekdays, weekends and events would make it possible to test whether a suggested rate holds up as demand changes. The current dashboard and regression establish a market benchmark for that test.

## SQL layer (DuckDB)

| Step | Purpose |
|---|---|
| [Clean listings and build features](sql/01_clean_and_engineer.sql) | Parse prices and bathrooms, apply sample filters, and calculate amenities and distance to Union Station. |
| [Check data quality](sql/02_quality_checks.sql) | Check ranges, categories, model inputs and optional reference counts. |
| [Compare market segments](sql/03_market_exploration.sql) | Compare unadjusted prices by neighbourhood, distance, room type and amenities. |

## Reproduce the analysis

The notebook fits and evaluates the regression. DuckDB provides a second implementation of the cleaning and feature calculations and produces descriptive market tables. Both start from the same raw snapshot. Place the November 2025 snapshot at the path in the [data instructions](data/README.md). From the repository root, run:

```bash
pip install -r requirements.txt
python scripts/run_sql_pipeline.py --check-known-totals
jupyter notebook notebooks/airbnb_pricing_analysis.ipynb
```

The SQL runner writes tables to `outputs/sql_results/`. Run `pytest tests/ -q` for SQL/Python comparisons on synthetic listings. Run `streamlit run app.py` to explore a listing using the saved coefficients. The app converts fitted log price back to dollars for scenario comparisons.

