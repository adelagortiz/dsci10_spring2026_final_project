# Housing Cost Burden and Economic Vulnerability in California

A county-level analysis of rent burden, fair market rents, and labor market
conditions across California's 58 counties from 2012 to 2023. Using data from 
the U.S. Census Bureau, HUD, and the Bureau of Labor Statistics, this project 
clusters California counties into four policy-relevant tiers based on their 
housing and labor market conditions.

## Introduction

Housing cost burden, defined as spending more than 30% of household income
on rent, does not affect all California counties equally. This project
examines where rent burden is highest, where labor markets are weakest, and
how these conditions have shifted over time. Using K-Means clustering applied 
to three variables (median gross rent, HUD 2-bedroom fair market rent, and unemployment 
rate), counties are grouped into four tiers: high rent burden, moderate rent burden, low burden, 
and high unemployment burden. The analysis covers 2012 to 2023, allowing us to track 
how county-level housing stress changed before, during, and after the COVID-19 pandemic.

## Data Sources

| # | Name | Source | Type | Fields | Format |
|---|------|--------|------|--------|--------|
| 1 | ACS 5-Year Estimates | census.gov | API | NAME, B25064_001E (median gross rent), B25070_010E (renters paying 50%+ of income on rent) | JSON via API, saved as CSV |
| 2 | HUD Fair Market Rents | huduser.gov | File | county name, state, year, FMR for 0-4 bedroom units | CSV, single historical file covering 1983 to present |
| 3 | BLS Local Area Unemployment Statistics | data.ca.gov | File | county name, year, labor force, employment, unemployment rate | CSV |

## Analysis

The pipeline loads and merges all three datasets at the county-year level,
joining on county FIPS code (Census and HUD) and county name (LAUS). After
cleaning and merging, K-Means clustering (k=4) is applied to three scaled
features: median gross rent, HUD 2-bedroom fair market rent, and unemployment 
rate. Features are standardized using StandardScaler before clustering so that
no single variable dominates due to differences in units or scale.

The number of clusters (k=4) was chosen after evaluating k=2 through k=6. K=3 produced a 
24/31/2 county split where one tier contained only two counties, which is not useful for 
policy interpretation. K=4 produced a more balanced 14/15/26/2 distribution and surfaced a 
meaningful distinction between Bay Area coastal counties with very high rents and low unemployment, 
and suburban metros like Los Angeles where rents are rising but labor markets remain relatively stable. 

Results are visualized as a cluster summary bar chart, a 2023 county scatter plot,
a tier-over-time line chart, and a color-coded California county map.

## Summary of Results

K-Means clustering identified four distinct county types across the 2012-2023
period. High rent burden counties (14 counties) are concentrated along the
coast and in the Bay Area, averaging $2,204 in median gross rent and 4%
unemployment. Moderate rent burden counties (15 counties) include large
suburban metros like Los Angeles, Sacramento, and Riverside, averaging $1,605
in median gross rent and 5% unemployment. Low burden counties (26 counties)
cover most inland and rural areas, averaging $1,061 in median gross rent and
7% unemployment. The label reflects where these counties fall relative to the
rest of the state, not that housing is affordable or that residents are not
stretched. High unemployment burden counties (2 counties), Colusa and
Imperial, average 13% unemployment and $913 in median gross rent, reflecting
structural conditions tied to agricultural and border economies.

The tier-over-time analysis reveals a clear statewide shift. In 2012, 36 of
58 counties were classified as high unemployment burden following the Great
Recession. By 2023 that number had fallen to 2 as labor markets recovered,
while the high rent burden tier grew from near zero to 14 counties. COVID-19
caused a temporary reversal in 2020 before a rapid recovery through 2022.

## How to Run

### 1. Clone the repository
git clone https://github.com/adelagortiz/dsci10_spring2026_final_project 
cd dsci10_spring2026_final_project

### 2. Install required packages
pip install pandas requests numpy scikit-learn python-dotenv matplotlib geopandas

### 3. Set up your Census API key

Get a free Census API key at https://api.census.gov/data/key_signup.html

In the `src/` directory, create a `.env` file using `.env.example` as a
template and add your key: CENSUS_API_KEY=your_key_here

### 4. Download the HUD Fair Market Rents data

Go to https://www.huduser.gov/portal/datasets/fmr.html and click the
"History" tab. Download the file labeled "FMR History 1983 - Present:
2-Bedroom Unit data in CSV" and save it to your `data/` folder as:

data/fmr_history.csv

### 5. Download the BLS LAUS data

Go to https://data.ca.gov/dataset/local-area-unemployment-statistics-laus-annual-average
and download the CSV file. Save it to the `data/` folder as: data/laus_ca.csv

### 6. Run the pipeline

From inside the `src/` directory run: python3 main.py

This will fetch Census data automatically via API, load the HUD and LAUS
files from your `data/` folder, merge all three datasets, run K-Means
clustering, and save four charts to the `results/` folder.

To run tests: python3 tests.py

### 7. Run the results notebook

Open `results.ipynb` from the root of the repository in Jupyter Notebook
or JupyterLab. Make sure you have run `main.py` first, as the notebook
reads from the processed data file saved by the pipeline.

jupyter notebook results.ipynb

The notebook loads the clustered dataset, prints summary statistics by
policy tier, and displays all four visualizations.

### Libraries used

- `pandas` — data loading, cleaning, and merging
- `requests` — Census API calls
- `numpy` — numerical operations
- `scikit-learn` — StandardScaler and KMeans clustering
- `matplotlib` — chart generation
- `geopandas` — California county map
- `python-dotenv` — loading the Census API key from .env

## Generative AI Usage

Claude was used to assist with portions of this project,
including the geopandas county map visualization, the HUD history CSV
loading and reshaping logic, the FIPS code construction for merging
Census and HUD data, the cluster labeling function, and the config
file structure. All AI generated code sections are labeled with a
comment # AI generated: in the source files.