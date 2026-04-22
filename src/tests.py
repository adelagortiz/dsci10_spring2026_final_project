import pandas as pd
from load import get_census_rent_burden, get_all_years, load_laus, load_hud_one_year
from process import clean_census, clean_hud, clean_laus


def test_single_year_returns_data():
    df = get_census_rent_burden(2023)
    assert df is not None, "API call returned None"
    assert len(df) > 0, "DataFrame is empty"
    print("PASSED: single year returns data")


def test_expected_columns_present():
    df = get_census_rent_burden(2023)
    assert "NAME" in df.columns, "missing county name column"
    assert "B25064_001E" in df.columns, "missing median gross rent column"
    assert "B25070_010E" in df.columns, "missing rent burden column"
    assert "year" in df.columns, "missing year column"
    print("PASSED: all expected columns present")


def test_returns_california_counties():
    df = get_census_rent_burden(2023)
    assert len(df) == 58, f"Expected 58 counties, got {len(df)}"
    print("PASSED: returns all 58 california counties")


def test_year_column_correct():
    df = get_census_rent_burden(2021)
    assert all(df["year"] == 2021), "year column contains incorrect values"
    print("PASSED: year column values are correct")


def test_laus_loads_correctly():
    df = load_laus()
    assert len(df) > 0, "laus data is empty"
    assert "unemployment_rate" in df.columns, "missing unemployment_rate column"
    assert "county_name" in df.columns, "missing county_name column"
    print("PASSED: laus data loads correctly")


def test_hud_loads_one_year():
    df = load_hud_one_year(2023)
    assert len(df) == 58, f"Expected 58 CA counties, got {len(df)}"
    assert "fmr_2br" in df.columns, "missing fmr_2br column"
    print("PASSED: hud loads 58 california counties for one year")


def test_clean_census_adds_fips():
    df = get_census_rent_burden(2023)
    df = clean_census(df)
    assert "fips2010" in df.columns, "missing fips2010 column after cleaning"
    assert "county_name" in df.columns, "missing county_name after cleaning"
    print("PASSED: clean_census creates fips2010 and county_name columns")


test_single_year_returns_data()
test_expected_columns_present()
test_returns_california_counties()
test_year_column_correct()
test_laus_loads_correctly()
test_hud_loads_one_year()
test_clean_census_adds_fips()

print("\nAll tests passed.")