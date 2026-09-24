import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.stats.diagnostic import het_breuschpagan

FINAL_VARS = [
    "accommodates", "bedrooms", "bathrooms", "is_shared_bath",
    "is_entire_home", "distance_to_downtown_km", "amenity_count",
    "instant_bookable"
]

def fit_final_model(df, random_state=0):
    """Fit the final log-price OLS model and evaluate it on a holdout sample."""
    X = df[FINAL_VARS]
    y = np.log(df["price"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=random_state
    )

    X_train_const = sm.add_constant(X_train)
    X_test_const = sm.add_constant(X_test, has_constant="add")

    model = sm.OLS(y_train, X_train_const).fit()
    robust = model.get_robustcov_results(cov_type="HC3")
    pred = model.predict(X_test_const)

    metrics = {
        "train_r2": model.rsquared,
        "test_r2": 1 - ((y_test - pred) ** 2).sum()
        / ((y_test - y_test.mean()) ** 2).sum(),
        "test_rmse_log": mean_squared_error(y_test, pred) ** 0.5,
        "test_mae_log": mean_absolute_error(y_test, pred),
    }

    bp = het_breuschpagan(model.resid, X_train_const)
    diagnostics = {
        "lm_stat": bp[0],
        "lm_pvalue": bp[1],
        "f_stat": bp[2],
        "f_pvalue": bp[3],
    }
    return model, robust, metrics, diagnostics

def coefficient_table(model, robust):
    """Return coefficients, HC3 p-values, and log-to-percent transformations."""
    pvalues = pd.Series(robust.pvalues, index=model.params.index)
    out = pd.DataFrame(
        {"coefficient": model.params, "robust_pvalue": pvalues}
    )
    out["percent_impact"] = (np.exp(out["coefficient"]) - 1) * 100
    return out

def estimate_nightly_price(model, **features):
    """Exponentiate the fitted log price for scenario exploration.

    This is a model-implied level, not an unbiased estimate of conditional
    mean price. A mean-price forecast would require a retransformation
    adjustment such as Duan's smearing estimator.
    """
    row = pd.DataFrame([{key: features[key] for key in FINAL_VARS}])
    log_pred = float(
        model.predict(sm.add_constant(row, has_constant="add")).iloc[0]
    )
    return float(np.exp(log_pred))
