# Toronto Airbnb Pricing Analytics

Entire homes in the November 2025 Toronto sample listed for a median of **CAD 167 per night**, compared with **CAD 65** for private rooms. The groups also differ in size, location and amenities. For a host pricing a two-bedroom apartment, the practical question is which nearby listings make credible comparisons.

I led the original graduate team project and rebuilt the Python analysis and interactive application for this portfolio. [Market dashboard](https://public.tableau.com/views/Toronto_Airbnb_Pricing_Analytics/Dashboard01MarketPulse) · [Pricing app](https://toronto-airbnb-pricing-analytics-jthhn2unchpj3ewyfbnyfq.streamlit.app/)

## Sample and method

The Inside Airbnb snapshot contains 21,468 listings. Cleaning and restricting the analysis to entire homes and private rooms with nightly prices between CAD 15 and 900 leaves **15,332 listings**. DuckDB tracks how many records each filter removes. The Python model relates log nightly price to room type, guest capacity, bedrooms, bathrooms, shared-bathroom status, distance to Union Station, amenity count and instant booking.

The model uses a 70/30 train/test split. Test R² was **0.619** for log price, close to the training value of 0.618. A Breusch–Pagan test indicated unequal residual variance, so the reported inference uses HC3 robust standard errors. [Notebook](notebooks/airbnb_pricing_analysis.ipynb) · [Model metrics](outputs/model_results/model_metrics.json)

## Pricing implications

| Listing characteristic | Estimated difference in nightly price, other inputs held constant |
|---|---:|
| Entire home compared with a private room | +43.8% |
| Shared bathroom | −21.0% |
| One kilometre farther from Union Station | −2.7% |
| Instant booking enabled | +2.4% |
| One additional listed amenity | +0.4% |

For a two-bedroom apartment with a private bathroom, I would start with nearby entire homes of similar size. If few qualify, I would widen the search area before adding private rooms. The fitted location gradient gives a way to compare properties farther apart. The 43.8% room-type estimate comes from a log-price regression, so it cannot be subtracted from the raw median gap to assign the remainder to location or size. To recommend a rate that maximizes revenue, I would also need booked nights and realized prices. [Coefficient estimates](outputs/model_results/model_effects.csv) · [Host pricing memo](reports/business_memo.md)

## SQL layer (DuckDB)

| Step | Purpose |
|---|---|
| [Clean listings and build features](sql/01_clean_and_engineer.sql) | Parse prices and bathrooms, apply sample filters, and calculate amenities and distance to Union Station. |
| [Check data quality](sql/02_quality_checks.sql) | Check ranges, categories, model inputs and optional reference counts. |
| [Compare market segments](sql/03_market_exploration.sql) | Compare unadjusted prices by neighbourhood, distance, room type and amenities. |

## Reproduce the analysis

Place the November 2025 snapshot at the path in the [data instructions](data/README.md). From the repository root, run:

```bash
pip install -r requirements.txt
python scripts/run_sql_pipeline.py --check-known-totals
jupyter notebook notebooks/airbnb_pricing_analysis.ipynb
```

The SQL runner writes tables to `outputs/sql_results/`. Run `pytest tests/ -q` for SQL/Python comparisons on synthetic listings. Run `streamlit run app.py` to explore a listing using the saved coefficients. The app converts fitted log price back to dollars for scenario comparisons.

