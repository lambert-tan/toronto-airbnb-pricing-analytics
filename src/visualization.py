import matplotlib.pyplot as plt

def price_distribution(df, save_path=None):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df["price"], bins=50)
    ax.set(
        title="Toronto Airbnb Nightly Price Distribution",
        xlabel="Nightly price (CAD)",
        ylabel="Listings",
    )
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=180, bbox_inches="tight")
    return fig

def coefficient_impact_chart(table, save_path=None):
    plot = table.drop(index="const").sort_values("percent_impact")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(plot.index, plot["percent_impact"])
    ax.axvline(0, linestyle="--")
    ax.set(
        title="Estimated Price Impact — Final OLS Model",
        xlabel="Estimated price impact (%)",
    )
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=180, bbox_inches="tight")
    return fig
