"""Interactive asking-price scenarios for the Toronto Inside Airbnb snapshot."""
import json
import math
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rate Studio · Toronto", page_icon="◒", layout="wide")
ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "outputs" / "model_results"
COEFFICIENTS = pd.read_csv(RESULTS / "final_coefficients.csv", index_col=0)["coefficient"]
METRICS = json.loads((RESULTS / "model_metrics.json").read_text())
SNAPSHOT = pd.Period(METRICS["snapshot_month"], freq="M").strftime("%B %Y")
LABELS = {
    "is_entire_home": "Entire home",
    "accommodates": "Guests",
    "bedrooms": "Bedrooms",
    "bathrooms": "Bathrooms",
    "is_shared_bath": "Shared bathroom",
    "distance_to_downtown_km": "Distance to Union Station (km)",
    "amenity_count": "Amenities",
    "instant_bookable": "Instant booking",
}
TABLEAU = "https://public.tableau.com/views/Toronto_Airbnb_Pricing_Analytics/Dashboard01MarketPulse"
PROJECT = "https://github.com/lambert-tan/toronto-airbnb-pricing-analytics"


def estimate_price(features):
    return math.exp(COEFFICIENTS["const"] + sum(COEFFICIENTS[k] * v for k, v in features.items()))


def rate_curve(features):
    """Show the fitted rate as distance varies, keeping every other input fixed."""
    distances = range(36)
    prices = [estimate_price({**features, "distance_to_downtown_km": d}) for d in distances]
    floor = math.floor(min(prices) / 10) * 10
    ceiling = math.ceil(max(prices) / 10) * 10

    def y(price):
        return 132 - 110 * (price - floor) / (ceiling - floor)

    def x(distance):
        return 64 + 395 * distance / 35

    points = " ".join(f"{x(d):.1f},{y(p):.1f}" for d, p in zip(distances, prices))
    guides = []
    for price in (floor, (floor + ceiling) / 2, ceiling):
        height = y(price)
        guides.append(f'<line x1="64" x2="459" y1="{height}" y2="{height}" stroke="#44625d"/>'
                      f'<text x="54" y="{height+4}" text-anchor="end">${price:,.0f}</text>')
    for distance in (0, 10, 20, 35):
        guides.append(f'<text x="{x(distance)}" y="155" text-anchor="middle">{distance} km</text>')
    current = features["distance_to_downtown_km"]
    return f"""<svg viewBox="0 0 492 168" role="img" aria-label="Model rate falls from CAD {prices[0]:.0f} at zero kilometres to CAD {prices[-1]:.0f} at 35 kilometres. Selected distance {current:g} kilometres." xmlns="http://www.w3.org/2000/svg">
    <g font-family="Arial,sans-serif" font-size="12" fill="#d5e5de">{''.join(guides)}</g>
    <polygon points="64,132 {points} 459,132" fill="#92d6b8" fill-opacity=".12"/>
    <polyline points="{points}" fill="none" stroke="#a5ebbf" stroke-width="3"/>
    <circle cx="{x(current)}" cy="{y(estimate_price(features))}" r="5" fill="#e9ffb6" stroke="#18433c" stroke-width="2"/>
    </svg>"""


st.markdown("""<style>
.stApp {background:#f6f7f2;color:#182e2b}
.block-container {max-width:1220px;padding-top:3.25rem;padding-bottom:3rem}
h1,h2,h3 {letter-spacing:-.04em}
.stApp h1 {font-family:Georgia,serif;font-weight:500;font-size:clamp(36px,5vw,62px);line-height:1.08}
.stApp h3 {font-size:1.28rem}
.rs-nav {display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #c8d1c8;padding:0 0 13px;margin-bottom:15px;color:#274b42}
.rs-name {font-weight:750;letter-spacing:-.04em;font-size:21px}
.rs-mark {display:inline-grid;place-items:center;width:29px;height:29px;background:#19453a;color:#d1f3a5;border-radius:8px;margin-right:8px}
.rs-meta,.rs-kicker {font:600 11px/1.5 ui-monospace,monospace;letter-spacing:.09em;text-transform:uppercase}
.rs-card {background:#153c35;color:#f6fbef;border-radius:20px;padding:clamp(18px,3vw,32px);margin:.3rem 0 1.1rem}
.rs-kicker {color:#bde3ce}.rs-price {font:500 clamp(50px,6vw,78px)/1 Georgia,serif;letter-spacing:-.055em;margin:10px 0 6px}
.rs-unit {font:500 15px/1.5 sans-serif;color:#c4dbce;letter-spacing:0}
.rs-card p {font-size:14px;color:#d2e4da;margin:5px 0}
.rs-chart {border-top:1px solid #547269;margin-top:20px;padding-top:16px}
.rs-chart svg {width:100%;display:block;margin-top:4px}
[data-testid="stVerticalBlockBorderWrapper"] {background:#fff;border-radius:15px}
@media(max-width:650px){.block-container{padding-left:1rem;padding-right:1rem}.rs-meta{letter-spacing:0}}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="rs-nav"><span class="rs-name"><span class="rs-mark">◒</span>Rate Studio</span>'
            '<span class="rs-meta">Toronto &nbsp;/&nbsp; CAD</span></div>', unsafe_allow_html=True)
st.title("Toronto pricing workspace")
st.write("Model a nightly asking rate, then pin a scenario to compare changes to your listing.")
left, right = st.columns([1.05, 1], gap="large")
with left:
    with st.container(border=True):
        st.subheader("Listing details")
        room = st.radio("Room type", ["Entire home", "Private room"], horizontal=True)
        a, b, c = st.columns(3)
        guests = a.number_input("Guests", 1, 16, 4)
        beds = b.number_input("Bedrooms", 0, 10, 2)
        baths = c.number_input("Bathrooms", 0.5, 8.0, 1.0, 0.5)
        distance = st.slider("Distance to Union Station (km)", 0.0, 35.0, 5.0, 0.5)
        amenities = st.slider("Amenity count", 0, 80, 30)
        a, b = st.columns(2)
        shared = a.toggle("Shared bathroom")
        instant = b.toggle("Instant booking", value=True)
features = {
    "is_entire_home": int(room == "Entire home"),
    "accommodates": guests,
    "bedrooms": beds,
    "bathrooms": baths,
    "is_shared_bath": int(shared),
    "distance_to_downtown_km": distance,
    "amenity_count": amenities,
    "instant_bookable": int(instant),
}
rate = estimate_price(features)
with right:
    st.markdown(f"""<section class="rs-card"><div class="rs-kicker">Modelled nightly asking rate</div>
    <div class="rs-price">${rate:,.0f} <span class="rs-unit">CAD / night</span></div>
    <p>{room} · {guests} guests · {beds} bedrooms · {distance:g} km from Union Station</p>
    <div class="rs-chart"><div class="rs-kicker">Same listing at different distances</div>{rate_curve(features)}</div></section>""", unsafe_allow_html=True)
    median = METRICS["entire_home_median" if room == "Entire home" else "private_room_median"]
    st.caption(f"Market reference · {room} listings had a median asking rate of CAD {median:,.0f} in {SNAPSHOT}. The median includes properties of different sizes and locations.")
    if not 15 <= rate <= 900:
        st.warning("This estimate falls outside the CAD 15–900 asking-price range used to fit the model.")

st.subheader("Scenario comparison")
reference = st.session_state.get("pinned_listing")
if st.button("Replace baseline with current listing" if reference else "Pin current listing as baseline", type="primary"):
    st.session_state.pinned_listing = features.copy()
    st.rerun()
if reference:
    old_rate = estimate_price(reference)
    m1, m2, m3 = st.columns(3)
    m1.metric("Pinned baseline", f"CAD {old_rate:,.0f}")
    m2.metric("Current listing", f"CAD {rate:,.0f}")
    m3.metric("Nightly difference", f"{rate-old_rate:+,.2f} CAD", f"{(rate/old_rate-1)*100:+.1f}%", delta_color="off")
    changes = [{"Input": label, "Baseline": reference[k], "Current": features[k]}
               for k, label in LABELS.items() if features[k] != reference[k]]
    if changes:
        st.dataframe(pd.DataFrame(changes), hide_index=True, use_container_width=True)
    else:
        st.caption("Baseline pinned. Change a listing detail above to compare rates.")
    if st.button("Clear baseline"):
        del st.session_state.pinned_listing
        st.rerun()
else:
    st.caption("Pin this listing to keep a reference rate while you edit. The baseline lasts for this session.")

def export_row(name, values):
    return {"Scenario": name, **{label: values[k] for k, label in LABELS.items()},
            "Modelled nightly rate (CAD)": round(estimate_price(values), 2), "Market snapshot": METRICS["snapshot_month"]}

rows = [export_row("Baseline", reference)] if reference else []
rows.append(export_row("Current", features))
st.download_button("Download scenario CSV", pd.DataFrame(rows).to_csv(index=False), "toronto-pricing-scenarios.csv", "text/csv")

with st.expander("Market data and model diagnostics"):
    st.write(f"The model uses {METRICS['listings']:,} Toronto listings from the {SNAPSHOT} Inside Airbnb snapshot. It exponentiates the fitted log asking price. Actual booked rates, occupancy and revenue are outside its scope.")
    st.write("The 70/30 train/test split evaluates log-price fit. The regression uses HC3 robust standard errors following a Breusch–Pagan test for unequal residual variance.")
    for col, (label, key) in zip(st.columns(4), [("Train R²","train_r2"),("Test R²","test_r2"),("Test RMSE (log)","test_rmse_log"),("Test MAE (log)","test_mae_log")]):
        col.metric(label, f"{METRICS[key]:.3f}")
    effects = [{"Listing input": label, "Coefficient": COEFFICIENTS[k],
                "One-unit price difference (%)": 100 * math.expm1(COEFFICIENTS[k])} for k, label in LABELS.items()]
    st.dataframe(pd.DataFrame(effects).round(3), hide_index=True, use_container_width=True)
    st.caption(f"Intercept on the log-price scale: {COEFFICIENTS['const']:.4f}. All differences hold the other inputs constant.")
st.divider()
st.markdown(f"**Lambert Tan** · [Toronto market dashboard]({TABLEAU}) · [Data and methodology]({PROJECT})")
