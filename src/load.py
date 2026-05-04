import os
import requests
import pandas as pd

from config import (CENSUS_API_KEY, CENSUS_VARIABLES, STATE_FIPS,
                    YEARS, DATA_DIR, LAUS_FILE, HUD_HISTORY_FILE,
                    LAUS_DOWNLOAD_URL, HUD_DOWNLOAD_URL)


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

# AI generated: added robust file downloading with validation and retries using Claude
def download_file(url, filepath, description):
    """Download a file from url and save to filepath if not already present or if corrupted."""
    if os.path.exists(filepath):
        # validate the file is actually a CSV and not an HTML error page
        with open(filepath, "rb") as f:
            first_bytes = f.read(512)
        if b"<html" in first_bytes.lower() or b"<!doctype" in first_bytes.lower():
            print(f"  Cached file appears corrupted (HTML page), re-downloading...")
            os.remove(filepath)
        else:
            print(f"{description} already exists at {filepath}, skipping download.")
            return True
    print(f"Downloading {description} from {url} ...")
    try:
        session = requests.Session()
        response = session.get(url, timeout=120)
        if "confirm=" in response.url or "confirm=" in response.text[:500]:
            confirm_token = None
            for key, value in response.cookies.items():
                if key.startswith("download_warning"):
                    confirm_token = value
            if confirm_token:
                response = session.get(url, params={"confirm": confirm_token}, timeout=120)
        if response.status_code != 200:
            print(f"  Error: received status code {response.status_code}")
            return False
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"  Saved to {filepath}")
        return True
    except Exception as e:
        print(f"  Error downloading {description}: {e}")
        return False

def ensure_laus_downloaded():
    """Download LAUS CSV from data.ca.gov if not already present."""
    filepath = os.path.join(DATA_DIR, LAUS_FILE)
    return download_file(
        url=LAUS_DOWNLOAD_URL,
        filepath=filepath,
        description="BLS LAUS California unemployment data"
    )

def ensure_hud_downloaded():
    """Download HUD FMR history CSV from huduser.gov if not already present."""
    filepath = os.path.join(DATA_DIR, HUD_HISTORY_FILE)
    return download_file(
        url=HUD_DOWNLOAD_URL,
        filepath=filepath,
        description="HUD Fair Market Rents history (1983-present)"
    )

def load_laus():
    if not ensure_laus_downloaded():
        raise FileNotFoundError(
            f"Could not auto-download LAUS data. Please download manually from:\n"
            f"  {LAUS_DOWNLOAD_URL}\n"
            f"and save to: {os.path.join(DATA_DIR, LAUS_FILE)}"
        )
    
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
    if not ensure_hud_downloaded():
        raise FileNotFoundError(
            f"Could not auto-download HUD FMR data. Please download manually from:\n"
            f"  {HUD_DOWNLOAD_URL}\n"
            f"and save to: {os.path.join(DATA_DIR, HUD_HISTORY_FILE)}"
        )
    
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

def load_hud_one_year(year):
    # load HUD FMR data for a single year; used by tests.py
    if not ensure_hud_downloaded():
        raise FileNotFoundError(
            f"Could not auto-download HUD FMR data. Please download manually from:\n"
            f"  {HUD_DOWNLOAD_URL}\n"
            f"and save to: {os.path.join(DATA_DIR, HUD_HISTORY_FILE)}"
        )
    filepath = os.path.join(DATA_DIR, HUD_HISTORY_FILE)
    df = pd.read_csv(filepath, encoding="latin1")
    df = df[df["state"] == 6]
    col = f"fmr{str(year)[2:]}_2"
    year_df = df[["fips", "name", col]].copy()
    year_df = year_df.rename(columns={
        "fips": "fips2010",
        "name": "countyname",
        col: "fmr_2br"
    })
    year_df["year"] = year
    year_df["fmr_2br"] = pd.to_numeric(year_df["fmr_2br"], errors="coerce")
    return year_df