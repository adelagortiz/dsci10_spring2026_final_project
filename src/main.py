import os
from config import DATA_DIR
from load import get_all_years

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)

    df = get_all_years()

    output_path = os.path.join(DATA_DIR, "rent_burden_ca.csv")
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")