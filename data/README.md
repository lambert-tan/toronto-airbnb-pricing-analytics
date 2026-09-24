# Data

Source: **Inside Airbnb — Toronto detailed listings, November 2025**.

The original snapshot used in this project contained **21,468 rows and 79 columns**. After cleaning and filtering, the final analytical sample contained **15,332 listings**.

Large CSV files are intentionally excluded from GitHub.

To reproduce the project:

1. Download the Toronto detailed listings snapshot from Inside Airbnb.
2. Create `data/raw/`.
3. Save the file as `data/raw/toronto_listings_detail_nov.csv`.
4. Run `notebooks/airbnb_pricing_analysis.ipynb`.

The notebook rebuilds the cleaned and engineered datasets from the raw snapshot.
