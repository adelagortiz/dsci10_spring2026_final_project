import requests
import pandas as pd
from config import CENSUS_API_KEY, CENSUS_VARIABLES, STATE_FIPS, YEARS

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