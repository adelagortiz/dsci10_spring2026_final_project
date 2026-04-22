import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# sklearn is used for scaling features and running k-means clustering
# install with: pip install scikit-learn
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from config import RESULTS_DIR, N_CLUSTERS, RANDOM_STATE, CLUSTER_FEATURES


# AI generated: k-means clustering and feature scaling using Claude
def run_kmeans(df):
    # drop rows with missing values in our clustering features
    df = df.dropna(subset=CLUSTER_FEATURES)

    # select the three features for clustering
    features = df[CLUSTER_FEATURES].copy()

    # scale features so no single variable dominates due to different units
    # StandardScaler converts each feature to have mean 0 and standard deviation 1
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    # k-means groups counties into N_CLUSTERS clusters based on similarity
    # n_clusters=4 is a design choice — it maps to four policy-relevant tiers:
    # high rent burden, moderate rent burden, low burden, and high unemployment burden
    # random_state is set so results are the same every time we run it
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    df["cluster"] = kmeans.fit_predict(scaled)

    return df


# AI generated: cluster labeling logic using Claude
def label_clusters(df):
    # detect correct cluster numbers by inspecting means
    # rather than hardcoding, so labels are always correct regardless of run order
    cluster_means = df.groupby("cluster")[["median_gross_rent", "unemployment_rate"]].mean()

    # highest rent -> high rent burden
    high_rent = cluster_means["median_gross_rent"].idxmax()

    # highest unemployment -> high unemployment burden
    high_unemp = cluster_means["unemployment_rate"].idxmax()

    # among the remaining two, higher rent -> moderate rent burden
    remaining = [c for c in cluster_means.index if c not in [high_rent, high_unemp]]
    moderate = cluster_means.loc[remaining, "median_gross_rent"].idxmax()
    low = [c for c in remaining if c != moderate][0]

    label_map = {
        high_rent: "high rent burden",
        high_unemp: "high unemployment burden",
        moderate: "moderate rent burden",
        low: "low burden"
    }

    print("cluster label map:", label_map)
    print("cluster means:")
    print(cluster_means.round(1))

    df["policy_tier"] = df["cluster"].map(label_map)
    return df


def get_tier_summary(df):
    # return average values per policy tier for display in the notebook
    summary = df.groupby("policy_tier")[CLUSTER_FEATURES].mean().round(2)
    return summary


def get_counties_by_tier(df, year=2023):
    # return county tier assignments for a given year
    result = df[df["year"] == year][["county_name", "policy_tier", "median_gross_rent", "unemployment_rate"]]
    result = result.sort_values("policy_tier")
    return result


def plot_cluster_summary(df):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    summary = df.groupby("policy_tier")[CLUSTER_FEATURES].mean().round(0)

    # left panel ordered by rent descending so bars step down cleanly
    rent_tiers = ["high rent burden", "moderate rent burden", "low burden", "high unemployment burden"]

    # right panel ordered by unemployment descending so bars step down cleanly
    unemp_tiers = ["high unemployment burden", "low burden", "moderate rent burden", "high rent burden"]

    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # left panel: rent variables ordered by rent descending
    summary_rent = summary.reindex(rent_tiers)
    x1 = range(len(rent_tiers))

    bars1 = ax1.bar([i - width/2 for i in x1], summary_rent["median_gross_rent"],
                    width=width, label="median gross rent", color="#4a7fb5", alpha=0.85)
    bars2 = ax1.bar([i + width/2 for i in x1], summary_rent["fmr_2br"],
                    width=width, label="hud 2br fair market rent", color="#4a9e6b", alpha=0.85)

    ax1.set_xticks(list(x1))
    ax1.set_xticklabels(rent_tiers, rotation=15, ha="right")
    ax1.set_ylabel("dollars ($)")
    ax1.set_title("avg rent by policy tier (high to low)")
    ax1.legend()

    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 30,
                 f"${int(bar.get_height()):,}",
                 ha="center", va="bottom", fontsize=8)
    for bar in bars2:
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 30,
                 f"${int(bar.get_height()):,}",
                 ha="center", va="bottom", fontsize=8)

    # right panel: unemployment ordered by unemployment descending
    summary_unemp = summary.reindex(unemp_tiers)
    x2 = range(len(unemp_tiers))

    bars3 = ax2.bar(list(x2), summary_unemp["unemployment_rate"],
                    width=0.5, color="#e05c4b", alpha=0.85)

    ax2.set_xticks(list(x2))
    ax2.set_xticklabels(unemp_tiers, rotation=15, ha="right")
    ax2.set_ylabel("percent (%)")
    ax2.set_title("avg unemployment rate by policy tier (high to low)")

    for bar in bars3:
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.1,
                 f"{bar.get_height():.1f}%",
                 ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    outpath = os.path.join(RESULTS_DIR, "cluster_summary.png")
    plt.savefig(outpath, dpi=150)
    plt.close()
    print(f"Saved cluster summary chart to {outpath}")


def plot_counties_by_tier(df):
    # scatter plot of unemployment vs rent colored by policy tier for 2023
    os.makedirs(RESULTS_DIR, exist_ok=True)

    colors = {
        "high rent burden": "tomato",
        "high unemployment burden": "steelblue",
        "moderate rent burden": "goldenrod",
        "low burden": "seagreen"
    }

    # counties to label on the chart so the audience can orient themselves
    label_these = [
        "Los Angeles", "San Francisco", "San Mateo", "Santa Clara",
        "Imperial", "Fresno", "Tulare", "Marin", "Kings", "Colusa"
    ]

    fig, ax = plt.subplots(figsize=(12, 8))

    for tier, group in df[df["year"] == 2023].groupby("policy_tier"):
        ax.scatter(group["unemployment_rate"], group["median_gross_rent"],
                   label=tier, color=colors[tier], alpha=0.7, s=70)

    # add labels for notable counties
    df_2023 = df[df["year"] == 2023]
    for _, row in df_2023.iterrows():
        if row["county_name"] in label_these:
            ax.annotate(row["county_name"],
                        xy=(row["unemployment_rate"], row["median_gross_rent"]),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=8,
                        color="black")

    ax.set_xlabel("unemployment rate (%)")
    ax.set_ylabel("median gross rent ($)")
    ax.set_title("california counties by policy tier (2023)")
    ax.legend()

    plt.tight_layout()
    outpath = os.path.join(RESULTS_DIR, "counties_by_tier_2023.png")
    plt.savefig(outpath)
    plt.close()
    print(f"Saved county scatter plot to {outpath}")


def plot_tier_over_time(df):
    # line chart showing how many counties fall in each tier per year
    os.makedirs(RESULTS_DIR, exist_ok=True)

    counts = df.groupby(["year", "policy_tier"]).size().unstack(fill_value=0)

    ax = counts.plot(figsize=(10, 5), marker="o")
    plt.title("number of counties per policy tier over time")
    plt.xlabel("year")
    plt.ylabel("number of counties")
    plt.legend(title="policy tier")

    # annotate 2020 pandemic spike
    ax.axvline(x=2020, color="grey", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(2020.1, ax.get_ylim()[1] * 0.92,
            "2020 pandemic\nunemployment spike",
            fontsize=8, color="grey", ha="right")

    plt.tight_layout()
    outpath = os.path.join(RESULTS_DIR, "tier_over_time.png")
    plt.savefig(outpath)
    plt.close()
    print(f"Saved tier over time chart to {outpath}")


# AI generated: geopandas map plot using Claude (Anthropic)
def plot_california_map(df):
    # geopandas is used to plot county boundaries on a map
    # install with: pip install geopandas
    import geopandas as gpd

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # use the 2023 snapshot for the map
    df_2023 = df[df["year"] == 2023].copy()

    # load california county boundaries from census tiger shapefiles
    # geopandas reads the shapefile directly from the url, no manual download needed
    url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
    counties = gpd.read_file(url)

    # filter to california only (state fips 06)
    counties = counties[counties["STATEFP"] == "06"]

    # build a 9-digit fips to match our data
    counties["fips2010"] = pd.to_numeric(counties["GEOID"] + "99999", errors="coerce")

    # merge county shapes with our cluster results
    merged = counties.merge(df_2023[["fips2010", "policy_tier", "county_name"]],
                            on="fips2010", how="left")

    # assign colors to each tier
    color_map = {
        "high rent burden": "#e05c4b",
        "high unemployment burden": "#4a7fb5",
        "moderate rent burden": "#e8a838",
        "low burden": "#4a9e6b"
    }
    merged["color"] = merged["policy_tier"].map(color_map).fillna("lightgrey")

    fig, ax = plt.subplots(figsize=(12, 14))
    fig.patch.set_facecolor("#f5f5f5")
    ax.set_facecolor("#f5f5f5")

    # draw counties with a slightly thicker border
    merged.plot(ax=ax, color=merged["color"], edgecolor="white", linewidth=0.8)

    # label a selection of well-known counties so the map is readable
    label_these = [
        "Los Angeles", "San Diego", "San Francisco", "Sacramento",
        "Fresno", "Kern", "Tulare", "Imperial", "Humboldt", "Shasta"
    ]

    for _, row in merged.iterrows():
        name = row.get("county_name", "")
        if name in label_these:
            centroid = row.geometry.centroid
            ax.annotate(name, xy=(centroid.x, centroid.y),
                        ha="center", fontsize=7, color="white", fontweight="bold")

    # add a manual legend
    legend_elements = [
        Patch(facecolor="#e05c4b", label="high rent burden"),
        Patch(facecolor="#e8a838", label="moderate rent burden"),
        Patch(facecolor="#4a9e6b", label="low burden"),
        Patch(facecolor="#4a7fb5", label="high unemployment burden"),
        Patch(facecolor="lightgrey", label="no data")
    ]
    ax.legend(handles=legend_elements, loc="lower left",
              fontsize=13, title="policy tier", title_fontsize=14,
              framealpha=0.9, edgecolor="grey")

    ax.set_title("california counties by policy tier (2023)",
                 fontsize=16, pad=15)
    ax.axis("off")

    plt.tight_layout()
    outpath = os.path.join(RESULTS_DIR, "ca_map_2023.png")
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved california map to {outpath}")


def run_analysis(df):
    df = run_kmeans(df)
    df = label_clusters(df)

    plot_cluster_summary(df)
    plot_counties_by_tier(df)
    plot_tier_over_time(df)
    plot_california_map(df)

    return df