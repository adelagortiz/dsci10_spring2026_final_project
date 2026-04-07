import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

DATA_DIR = "../data"
RESULTS_DIR = "../results"

YEARS = list(range(2012, 2024))

STATE_FIPS = "06"

CENSUS_VARIABLES = "NAME,B25064_001E,B25070_010E"