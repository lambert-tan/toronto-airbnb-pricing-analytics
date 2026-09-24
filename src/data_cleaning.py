import pandas as pd
import numpy as np

KEEP = [
    "price", "latitude", "longitude", "room_type", "bedrooms",
    "bathrooms_text", "accommodates", "amenities", "host_since",
    "host_is_superhost", "instant_bookable", "neighbourhood_cleansed",
    "has_availability", "number_of_reviews", "availability_365"
]

def _bath_count(text):
    if pd.isna(text):
        return np.nan
    text = str(text).lower().strip()
    if "half" in text:
        return 0.5
    try:
        return float(text.split()[0])
    except (ValueError, IndexError):
        return np.nan

def clean_listings(raw):
    """Clean the raw Inside Airbnb listing snapshot for analysis."""
    df = raw[KEEP].copy()

    df["price"] = pd.to_numeric(
        df["price"].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce",
    )
    df = df[df["price"].between(15, 900)].copy()
    df = df[df["bedrooms"].notna()].copy()

    df["is_shared_bath"] = (
        df["bathrooms_text"].astype(str).str.lower().str.contains("shared").astype(int)
    )
    df["bathrooms"] = df["bathrooms_text"].apply(_bath_count)
    df = df[df["bathrooms"].le(10) & df["bathrooms"].gt(0)].copy()
    df = df.drop(columns="bathrooms_text")

    df = df[df["has_availability"].notna()].copy()
    df = df[df["host_since"].notna()].copy()

    inactive = (
        df["availability_365"].fillna(0).eq(0)
        & df["number_of_reviews"].fillna(0).eq(0)
    )
    df = df[~inactive].copy()

    df = df[df["room_type"].isin(["Entire home/apt", "Private room"])].copy()
    df["host_is_superhost"] = df["host_is_superhost"].fillna("f")

    return df.reset_index(drop=True)
