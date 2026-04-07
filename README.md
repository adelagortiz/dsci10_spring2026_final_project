# Housing Cost Burden and Economic Vulnerability in California

A county-level analysis of rent burden, fair market rents, and labor market
conditions across California's 58 counties from 2012 to 2023.

# Data sources

| # | Name | Source | Type | Fields | Format |
|---|------|--------|------|--------|--------|
| 1 | ACS 5-Year Estimates | census.gov | API | NAME, B25064_001E, B25070_010E | JSON via API, saved as CSV |
| 2 | HUD Fair Market Rents | huduser.gov | File | County, year, FMR by unit size | XLSX |
| 3 | BLS Local Area Unemployment Statistics | bls.gov | File | County, year, unemployment rate | XLSX |


# Results 
In progress. K-Means clustering will group California counties into policy
tiers based on rent burden rate, fair market rent, and unemployment rate.

# Installation
1. Clone this repository
2. In the `src/` directory, create a `.env` file using `.env.example` as a template
3. Add your Census API key to `.env` as CENSUS_API_KEY=your_key_here
4. Install required packages:

/usr/local/bin/python3 -m pip install pandas requests numpy scikit-learn python-dotenv

# Running analysis 

From the `src/` directory run:

/usr/local/bin/python3 main.py

Data will be saved to the `data/` folder.