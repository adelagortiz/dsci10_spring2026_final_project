from load import get_census_rent_burden, get_all_years

def test_single_year_returns_data():
    df = get_census_rent_burden(2023)
    assert df is not None, "API call returned None"
    assert len(df) > 0, "DataFrame is empty"
    print("PASSED: single year returns data")

def test_expected_columns_present():
    df = get_census_rent_burden(2023)
    assert "NAME" in df.columns, "Missing county name column"
    assert "B25064_001E" in df.columns, "Missing median gross rent column"
    assert "B25070_010E" in df.columns, "Missing rent burden column"
    assert "year" in df.columns, "Missing year column"
    print("PASSED: all expected columns present")

def test_returns_california_counties():
    df = get_census_rent_burden(2023)
    assert len(df) == 58, f"Expected 58 counties, got {len(df)}"
    print("PASSED: returns all 58 California counties")

def test_year_column_correct():
    df = get_census_rent_burden(2021)
    assert all(df["year"] == 2021), "Year column contains incorrect values"
    print("PASSED: year column values are correct")

def test_all_years_returns_full_dataset():
    df = get_all_years()
    assert len(df) == 696, f"Expected 696 rows, got {len(df)}"
    print("PASSED: full dataset contains 696 rows")

test_single_year_returns_data()
test_expected_columns_present()
test_returns_california_counties()
test_year_column_correct()
test_all_years_returns_full_dataset()

print("\nAll tests passed.")