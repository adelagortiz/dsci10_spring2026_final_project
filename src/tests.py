from load import get_census_rent_burden

def test_census_api():
    df = get_census_rent_burden(2023)
    assert df is not None, "API call returned None"
    assert len(df) > 0, "DataFrame is empty"
    assert "B25064_001E" in df.columns, "Missing rent column"
    assert "B25070_010E" in df.columns, "Missing burden column"
    print("All tests passed.")
    print(df.head())

test_census_api()