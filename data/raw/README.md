# Raw Data Acquisition Guide

## Primary Dataset: IRDAI Monthly Life Insurance Business Data

Since the official IRDAI monthly statistics are published in Excel format without a stable, versioned API endpoint, you must download the dataset manually and place it in this directory.

### Source 1: Official IRDAI Website
1. Visit: [IRDAI Life Insurance Public Disclosures](https://irdai.gov.in/life)
2. Look for the "Monthly Business Figures" or "Business Statistics" section.
3. Download the latest Excel file for the 2024-2025 financial year.
4. Save the file as `irdai_life_business.xlsx` (or `.csv`) in `data/raw/`.

### Source 2: Dataful (Processed Official Data)
1. Visit: [Dataful - IRDAI Life Insurance](https://dataful.in/datasets/19771/)
2. Download the CSV version of the dataset.
3. Save the file as `irdai_life_business.csv` in `data/raw/`.

## Expected Schema

The data ingestion pipeline (`src/ingestion/data_loader.py`) expects the following columns (or similar variations, which it will normalize):

- `fiscal_year` (e.g., "2024-25")
- `month` (e.g., "April", "May")
- `insurance_company` (e.g., "LIC", "HDFC Life")
- `category` (e.g., "Individual Single Premium")
- `policies_issued` (Numeric count)
- `premium_collected` (Numeric amount)
- `sum_assured` (Numeric amount)

*Note: Do NOT use fabricated or synthetic data. If you don't have the real data yet, please download it using the links above before running the pipeline.*
