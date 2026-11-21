"""Parity tests for the DuckDB SQL pipeline.

The raw Inside Airbnb file is not committed, so these tests build a synthetic snapshot with
deliberately awkward values, then check that sql/01_clean_and_engineer.sql returns the same
tables as the Python code in src/ (clean_listings and engineer_features).

Run:  pytest tests/ -q        (or: python tests/test_sql_pipeline.py)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
RUNNER = REPO / "scripts" / "run_sql_pipeline.py"

from src import data_cleaning as dc  # noqa: E402
from src.feature_engineering import engineer_features  # noqa: E402

FEATURE_COLS = [
    "price", "bedrooms", "bathrooms", "is_shared_bath", "accommodates", "host_is_superhost",
    "instant_bookable", "amenity_count", "host_experience_years", "distance_to_downtown_km",
    "is_entire_home",
]


def make_raw_listings(seed: int = 11, n: int = 6000) -> pd.DataFrame:
    """Synthetic snapshot with the awkward values the cleaning rules are written for."""
    rng = np.random.default_rng(seed)

    def pick(options, probs=None):
        return list(rng.choice(np.array(options, dtype=object), n, p=probs))

    # prices: formatted strings, boundaries, unparseable and missing values
    base = np.round(rng.lognormal(4.9, 0.6, n), 2)
    price = [f"${v:,.2f}" for v in base]
    for i in rng.choice(n, 60, replace=False):
        price[i] = str(rng.choice(["$15.00", "$900.00", "$14.99", "$900.01", "$1,234.00", "abc", None, "$0.00"]))
        if price[i] == "None":
            price[i] = None

    bath = pick(["1 bath", "1.5 baths", "2 baths", "1 shared bath", "2.5 baths", "Half-bath",
                 "Shared half-bath", "Private half-bath", "0 baths", "11 baths", "3 shared baths",
                 "Bath", "", None], [.28, .1, .1, .12, .03, .03, .03, .02, .02, .01, .02, .01, .01, .22])
    amen_pool = ['["Wifi", "Kitchen", "TV"]', '["Wifi"]', "[]", '["Wifi", "Hair dryer, ionic", "Crib \\"pack\\""]',
                 '["Wi\\u2019fi", "Pool"]', "not json", None, '[' + ", ".join(f'"a{k}"' for k in range(60)) + ']']
    hs = pd.to_datetime("2009-06-01") + pd.to_timedelta(rng.integers(0, 5600, n), unit="D")
    host_since = [d.strftime("%Y-%m-%d") for d in hs]
    for i in rng.choice(n, 40, replace=False):
        host_since[i] = None
    for i in rng.choice(n, 12, replace=False):
        host_since[i] = "N/A"           # pandas treats this as missing
    for i in rng.choice(n, 8, replace=False):
        host_since[i] = "2015-13-45"    # not a date: cleaning keeps it, feature step must drop it

    avail = list(rng.integers(0, 366, n).astype(object))
    reviews = list(rng.integers(0, 300, n).astype(object))
    for i in rng.choice(n, 500, replace=False):      # inactive listings
        avail[i], reviews[i] = 0, 0
    for i in rng.choice(n, 40, replace=False):
        avail[i], reviews[i] = None, None
    for i in rng.choice(n, 30, replace=False):
        reviews[i] = None

    lat = list(np.round(43.58 + rng.random(n) * 0.2, 6))
    lon = list(np.round(-79.55 + rng.random(n) * 0.33, 6))
    for i in rng.choice(n, 10, replace=False):
        lat[i] = None
    accommodates = list(rng.integers(1, 12, n).astype(object))
    for i in rng.choice(n, 15, replace=False):
        accommodates[i] = None
    bedrooms = list(rng.choice([0, 1, 1, 2, 2, 3, 4, 6], n).astype(object))
    for i in rng.choice(n, 150, replace=False):
        bedrooms[i] = None

    return pd.DataFrame({
        "id": 1_000_000 + np.arange(n),
        "name": pick(["Cozy loft", 'The "Annex" stay', "Room, near TTC"]),
        "description": pick(["plain", "line1\nline2", 'quote " inside, and comma']),
        "price": price,
        "latitude": lat, "longitude": lon,
        "room_type": pick(["Entire home/apt", "Private room", "Shared room", "Hotel room"], [.6, .32, .04, .04]),
        "bedrooms": bedrooms,
        "bathrooms_text": bath,
        "accommodates": accommodates,
        "amenities": pick(amen_pool),
        "host_since": host_since,
        "host_is_superhost": pick(["t", "f", None], [.25, .7, .05]),
        "instant_bookable": pick(["t", "f", None], [.4, .58, .02]),
        "neighbourhood_cleansed": pick(["Waterfront", "Annex", "Kensington-Chinatown", "Scarborough Village"]),
        "has_availability": pick(["t", "f", None], [.85, .13, .02]),
        "number_of_reviews": reviews,
        "availability_365": avail,
    })


def run_sql(raw_csv: Path, out_dir: Path, steps=("01", "02", "03")) -> pd.DataFrame:
    feats_csv = out_dir / "features_from_sql.csv"
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--raw-file", str(raw_csv), "--out-dir", str(out_dir / "results"),
         "--steps", *steps, "--export-features", str(feats_csv)],
        capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, f"runner failed:\nSTDOUT\n{proc.stdout[-3000:]}\nSTDERR\n{proc.stderr[-3000:]}"
    return pd.read_csv(feats_csv)


def reference(raw_csv: Path):
    """clean_listings + engineer_features from src/, applied to the same CSV the SQL reads."""
    raw = pd.read_csv(raw_csv)
    original_keep = list(dc.KEEP)
    dc.KEEP = original_keep + ["id"]          # carry the id so rows can be matched; logic unchanged
    try:
        clean = dc.clean_listings(raw)
    finally:
        dc.KEEP = original_keep
    feats = engineer_features(clean.drop(columns="id"))
    return clean, feats


def assert_same(a: pd.Series, b: pd.Series, label: str):
    if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
        same = np.isclose(a.astype(float), b.astype(float), rtol=1e-9, atol=1e-9, equal_nan=True)
    else:
        same = (a.astype(str) == b.astype(str)) | (a.isna() & b.isna())
    assert np.asarray(same).all(), f"{label}: {int((~np.asarray(same)).sum())} differing values"


# ------------------------------------------------------------------------------- tests
def test_clean_listings_match_python(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    make_raw_listings().to_csv(raw_csv, index=False)
    ref_clean, _ = reference(raw_csv)
    run_sql(raw_csv, tmp_path)
    import duckdb
    con = duckdb.connect()
    con.execute("SET VARIABLE raw_file = ?", [str(raw_csv)])
    con.execute("SET VARIABLE check_known_totals = false")
    for f in ("01_clean_and_engineer.sql",):
        for st in con.extract_statements((REPO / "sql" / f).read_text()):
            con.execute(st.query)
    got = con.execute("SELECT * FROM listings_clean").df()

    ref = ref_clean.sort_values("id").reset_index(drop=True)
    got = got.sort_values("listing_id").reset_index(drop=True)
    assert len(ref) > 2000
    assert list(ref["id"]) == list(got["listing_id"].astype("int64")), "different cleaned cohorts"
    for col in [c for c in ref.columns if c != "id"]:
        assert_same(ref[col], got[col], f"listings_clean.{col}")


def test_features_match_python(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    make_raw_listings().to_csv(raw_csv, index=False)
    _, ref = reference(raw_csv)
    got = run_sql(raw_csv, tmp_path)

    assert len(ref) == len(got) and len(ref) > 2000, (len(ref), len(got))
    ref = ref.sort_values(["distance_to_downtown_km", "price"]).reset_index(drop=True)
    got = got.sort_values(["distance_to_downtown_km", "price"]).reset_index(drop=True)
    for col in FEATURE_COLS:
        assert_same(ref[col], got[col], f"listing_features.{col}")


def test_edge_cases_are_present(tmp_path):
    """Guard: the parity tests only mean something if the edge cases they target occur."""
    raw_csv = tmp_path / "raw.csv"
    make_raw_listings().to_csv(raw_csv, index=False)
    raw = pd.read_csv(raw_csv)
    clean, feats = reference(raw_csv)
    assert raw["price"].isna().sum() > 0 and (raw["price"] == "abc").sum() > 0
    assert (clean["is_shared_bath"] == 1).sum() > 100
    assert (clean["bathrooms"] == 0.5).sum() > 20
    assert (feats["amenity_count"] == 0).sum() > 100 and feats["amenity_count"].max() >= 60
    assert len(clean) > len(feats) > 0            # malformed host_since dates and missing coordinates
    assert clean["host_is_superhost"].isin(["t", "f"]).all()
    assert len(raw) > len(clean) * 1.3


def test_quality_checks_and_funnel(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    make_raw_listings().to_csv(raw_csv, index=False)
    run_sql(raw_csv, tmp_path)
    checks = pd.read_csv(tmp_path / "results" / "quality_checks.csv")
    assert checks["passed"].all() and len(checks) == 11
    funnel = pd.read_csv(tmp_path / "results" / "cleaning_funnel.csv")
    assert funnel["rows_remaining"].is_monotonic_decreasing
    assert funnel.iloc[0]["rows_remaining"] == 6000
    _, feats = reference(raw_csv)
    assert funnel.iloc[-1]["rows_remaining"] == len(feats)


def test_known_totals_check_fails_on_wrong_data(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    make_raw_listings().to_csv(raw_csv, index=False)
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--raw-file", str(raw_csv), "--out-dir", str(tmp_path / "r"),
         "--steps", "01", "02", "--check-known-totals"], capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 1 and "known_raw_rows_21468" in proc.stdout


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
