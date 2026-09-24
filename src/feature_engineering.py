import ast
import numpy as np
import pandas as pd

UNION_LAT, UNION_LON = 43.6455, -79.3807
SNAPSHOT_DATE = pd.Timestamp("2025-11-11")

def _amenity_count(value):
    try:
        return len(ast.literal_eval(value)) if isinstance(value, str) else len(value)
    except (ValueError, SyntaxError, TypeError):
        return 0

def _haversine(lat, lon):
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(
        np.radians, [lat, lon, UNION_LAT, UNION_LON]
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )
    return 2 * radius_km * np.arcsin(np.sqrt(a))

def engineer_features(df):
    """Create interpretable pricing features used by the final model."""
    out = df.copy()

    out["amenity_count"] = out["amenities"].apply(_amenity_count)

    host_since = pd.to_datetime(out["host_since"], errors="coerce")
    out["host_experience_years"] = (
        SNAPSHOT_DATE - host_since
    ).dt.days / 365.25

    out["distance_to_downtown_km"] = _haversine(
        out["latitude"].to_numpy(), out["longitude"].to_numpy()
    )
    out["host_is_superhost"] = (out["host_is_superhost"] == "t").astype(int)
    out["instant_bookable"] = (out["instant_bookable"] == "t").astype(int)
    out["is_entire_home"] = (out["room_type"] == "Entire home/apt").astype(int)

    cols = [
        "price", "bedrooms", "bathrooms", "is_shared_bath", "accommodates",
        "host_is_superhost", "instant_bookable", "amenity_count",
        "host_experience_years", "distance_to_downtown_km", "is_entire_home"
    ]
    return out[cols].dropna().reset_index(drop=True)
