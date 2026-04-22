import pandas as pd
from load import get_all_years, load_laus, load_hud_all_years


# AI generated: fips code construction to match hud format using Claude
def clean_census(df):
    # convert rent and burden count from string to number
    df["median_gross_rent"] = pd.to_numeric(df["B25064_001E"], errors="coerce")
    df["renter_burden_count"] = pd.to_numeric(df["B25070_010E"], errors="coerce")

    # the census api uses -666666666 as a sentinel value for missing data
    # we replace those with NaN so they don't corrupt our analysis
    df["median_gross_rent"] = df["median_gross_rent"].replace(-666666666, pd.NA)

    # build a 9-digit fips code to match the format hud uses
    # census gives 5 digits (e.g. 06001), hud uses 9 digits (e.g. 600199999)
    df["fips2010"] = df["state"] + df["county"]
    df["fips2010"] = df["fips2010"].str.zfill(5) + "99999"
    df["fips2010"] = pd.to_numeric(df["fips2010"], errors="coerce")

    # clean up county name for merging with laus later
    df["county_name"] = df["NAME"].str.replace(", California", "", regex=False)
    df["county_name"] = df["county_name"].str.replace(" County", "", regex=False)

    df = df[["fips2010", "county_name", "median_gross_rent", "renter_burden_count", "year"]]
    return df

def clean_hud(df):
    df["fips2010"] = pd.to_numeric(df["fips2010"], errors="coerce")
    df["fmr_2br"] = pd.to_numeric(df["fmr_2br"], errors="coerce")
    return df


def clean_laus(df):
    df["unemployment_rate"] = pd.to_numeric(df["unemployment_rate"], errors="coerce")
    return df


def merge_all(census_df, hud_df, laus_df):
    # merge census and hud together using fips code and year
    merged = pd.merge(
        census_df,
        hud_df[["fips2010", "fmr_2br", "year"]],
        on=["fips2010", "year"],
        how="inner"
    )

    # merge in laus using county name and year
    merged = pd.merge(
        merged,
        laus_df,
        on=["county_name", "year"],
        how="inner"
    )

    print(f"Merged dataset: {len(merged)} rows")
    return merged


def build_dataset():
    print("Loading Census data...")
    census_raw = get_all_years()
    census = clean_census(census_raw)

    print("Loading HUD data...")
    hud_raw = load_hud_all_years()
    hud = clean_hud(hud_raw)

    print("Loading LAUS data...")
    laus_raw = load_laus()
    laus = clean_laus(laus_raw)

    print("Merging all three datasets...")
    df = merge_all(census, hud, laus)

    return df