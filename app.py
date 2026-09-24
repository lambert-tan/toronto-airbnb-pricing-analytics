import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Toronto Airbnb Pricing Analytics", page_icon="🏙️", layout="wide")

COEFFICIENTS = {
    "const": 4.09408960199153,
    "accommodates": 0.08549697083778691,
    "bedrooms": 0.09310739033187514,
    "bathrooms": 0.12565295489071823,
    "is_shared_bath": -0.2361033071586235,
    "is_entire_home": 0.36343451834267926,
    "distance_to_downtown_km": -0.02747827269687229,
    "amenity_count": 0.0036536335952634313,
    "instant_bookable": 0.023284560714505832,
}

METRICS = {
    "train_r2": 0.6176,
    "test_r2": 0.6185,
    "test_rmse_log": 0.4139,
    "test_mae_log": 0.3210,
}

def percent_impact(beta):
    return (np.exp(beta) - 1) * 100

def estimate_price(features):
    log_price = COEFFICIENTS["const"]
    for variable, value in features.items():
        log_price += COEFFICIENTS[variable] * value
    return float(np.exp(log_price))

st.title("Toronto Airbnb Pricing Analytics")
st.caption("15,332 listings · Toronto · Inside Airbnb, November 2025")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings analyzed", "15,332")
c2.metric("Test R²", f"{METRICS['test_r2']:.3f}")
c3.metric("Entire-home premium", f"{percent_impact(COEFFICIENTS['is_entire_home']):.1f}%")
c4.metric("Downtown distance effect", f"{percent_impact(COEFFICIENTS['distance_to_downtown_km']):.1f}% / km")

st.subheader("What drives nightly price?")

impact_data = pd.DataFrame({
    "Driver": ["Entire home", "Shared bathroom", "Instant booking", "Amenity count", "Distance to downtown"],
    "Estimated impact (%)": [
        percent_impact(COEFFICIENTS["is_entire_home"]),
        percent_impact(COEFFICIENTS["is_shared_bath"]),
        percent_impact(COEFFICIENTS["instant_bookable"]),
        percent_impact(COEFFICIENTS["amenity_count"]),
        percent_impact(COEFFICIENTS["distance_to_downtown_km"]),
    ],
}).set_index("Driver")

left, right = st.columns([1.15, 1])
with left:
    st.bar_chart(impact_data)
with right:
    st.markdown("""
**The main pricing story is the property itself.**

Room type, bathroom setup and size create the largest differences in nightly price. Distance from downtown still matters, but it works better as an adjustment after a comparable-property benchmark has been set.

**Three-layer pricing framework**
1. Start with property fundamentals.
2. Adjust for distance from downtown.
3. Fine-tune with operational features.
""")

st.divider()
st.subheader("Explore a pricing scenario")
st.caption("This applies the final log-price OLS coefficients to the selected listing characteristics. The result is a model-implied scenario, not an expected market-price forecast.")

with st.form("pricing_form"):
    a, b, c, d = st.columns(4)
    with a:
        accommodates = st.slider("Guests accommodated", 1, 16, 4)
        bedrooms = st.slider("Bedrooms", 0, 10, 2)
    with b:
        bathrooms = st.slider("Bathrooms", 0.5, 8.0, 1.0, 0.5)
        amenity_count = st.slider("Amenity count", 0, 80, 30)
    with c:
        distance = st.slider("Distance to downtown (km)", 0.0, 35.0, 5.0, 0.5)
        entire_home = st.toggle("Entire home", value=True)
    with d:
        shared_bath = st.toggle("Shared bathroom", value=False)
        instant = st.toggle("Instant booking", value=True)
    submitted = st.form_submit_button("Calculate model-implied price", type="primary", use_container_width=True)

if submitted:
    features = {
        "accommodates": accommodates,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "is_shared_bath": int(shared_bath),
        "is_entire_home": int(entire_home),
        "distance_to_downtown_km": distance,
        "amenity_count": amenity_count,
        "instant_bookable": int(instant),
    }
    estimate = estimate_price(features)
    st.success(f"Model-implied nightly price: **{estimate:,.0f} CAD**")\n    st.caption("The model is estimated in log dollars. This value is obtained by exponentiating the fitted log price and does not include a retransformation correction for the conditional mean.")

st.divider()
st.subheader("Model diagnostics")
d1, d2, d3, d4 = st.columns(4)
d1.metric("Train R²", f"{METRICS['train_r2']:.3f}")
d2.metric("Test R²", f"{METRICS['test_r2']:.3f}")
d3.metric("Test RMSE", f"{METRICS['test_rmse_log']:.3f}")
d4.metric("Test MAE", f"{METRICS['test_mae_log']:.3f}")
st.caption("Breusch–Pagan testing identified heteroskedasticity; HC3 robust standard errors were therefore used for inference.")

with st.expander("Final model coefficients"):
    table = pd.DataFrame({
        "Coefficient": COEFFICIENTS,
        "Estimated impact (%)": {key: percent_impact(value) for key, value in COEFFICIENTS.items()},
    })
    st.dataframe(table.round(4), use_container_width=True)

st.divider()
st.caption("Lambert Tan · Portfolio reconstruction and extension of a graduate analytics team project that I led.")
