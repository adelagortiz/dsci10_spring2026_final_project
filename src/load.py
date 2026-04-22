import os
import requests
import pandas as pd

from config import (CENSUS_API_KEY, CENSUS_VARIABLES, STATE_FIPS,
                    YEARS, DATA_DIR, LAUS_FILE, HUD_HISTORY_FILE)


def get_census_rent_burden(year):
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {
        "get": CENSUS_VARIABLES,
        "for": "county:*",
        "in": f"state:{STATE_FIPS}",
        "key": CENSUS_API_KEY
    }
    print(f"Fetching Census data for {year}...")
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error for {year}: status code {response.status_code}")
            return None
        data = response.json()
        columns = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=columns)
        df["year"] = year
        return df
    except Exception as e:
        print(f"Error fetching data for {year}: {e}")
        return None


def get_all_years():
    all_dfs = []
    for year in YEARS:
        df = get_census_rent_burden(year)
        if df is not None:
            all_dfs.append(df)
    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"Done. Total rows collected: {len(combined)}")
    return combined


def load_laus():
    # load the bls laus file downloaded from data.ca.gov
    filepath = os.path.join(DATA_DIR, LAUS_FILE)
    df = pd.read_csv(filepath)

    # keep only county rows and the years we need
    df = df[df["Area Type"] == "County"]
    df = df[df["Year"].isin(YEARS)]

    # keep only the columns we need
    df = df[["Area Name", "Year", "Unemployment Rate"]]

    # rename to match naming in the rest of our data
    df = df.rename(columns={
        "Area Name": "county_name",
        "Year": "year",
        "Unemployment Rate": "unemployment_rate"
    })

    # strip " County" from the name so it matches our other datasets
    df["county_name"] = df["county_name"].str.replace(" County", "", regex=False)

    print(f"Loaded LAUS data: {len(df)} rows")
    return df


# AI generated: hud history csv loading and reshaping using Claude
def load_hud_all_years():
    # load the hud fmr history csv downloaded from huduser.gov
    # this single file covers 2-bedroom fmr for all years from 1983 to present
    # the file uses latin1 encoding due to special characters in some area names
    filepath = os.path.join(DATA_DIR, HUD_HISTORY_FILE)
    df = pd.read_csv(filepath, encoding="latin1")

    # keep only california rows (state fips 6)
    df = df[df["state"] == 6]

    # the fmr columns use two-digit year suffixes with _2 for 2-bedroom
    # e.g. fmr12_2 = 2-bedroom fair market rent for fiscal year 2012
    # we use 2-bedroom fmr as a representative rent benchmark
    all_dfs = []
    for year in YEARS:
        col = f"fmr{str(year)[2:]}_2"
        year_df = df[["fips", "name", col]].copy()
        year_df = year_df.rename(columns={
            "fips": "fips2010",
            "name": "countyname",
            col: "fmr_2br"
        })
        year_df["year"] = year
        all_dfs.append(year_df)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined["fmr_2br"] = pd.to_numeric(combined["fmr_2br"], errors="coerce")
    print(f"Done. Total HUD rows: {len(combined)}")
    return combined