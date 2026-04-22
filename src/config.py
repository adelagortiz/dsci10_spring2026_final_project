import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

# directory paths
DATA_DIR = "../data"
RESULTS_DIR = "../results"

# years to pull data for
YEARS = list(range(2012, 2024))

# california state fips code
STATE_FIPS = "06"

# census variables: county name, median gross rent, renters paying 50%+ of income on rent
CENSUS_VARIABLES = "NAME,B25064_001E,B25070_010E"

# file names for downloaded data
LAUS_FILE = "laus_ca.csv"
HUD_HISTORY_FILE = "fmr_history.csv"

# output file names
MERGED_FILE = "merged_ca_housing.csv"
CLUSTERED_FILE = "ca_housing_clustered.csv"

# number of clusters set to 4 after evaluating k=2 through k=6
# k=3 produced a 24/31/2 county split where one tier had only 2 counties
# k=4 produces a more balanced 14/15/26/2 split and surfaces a meaningful
# distinction between high rent burden (coastal) and moderate rent burden
# (suburban/inland) that k=3 was collapsing into a single group
# random state is fixed so cluster numbers are stable across runs
N_CLUSTERS = 4
RANDOM_STATE = 42

# features used for k-means clustering
CLUSTER_FEATURES = ["median_gross_rent", "fmr_2br", "unemployment_rate"]