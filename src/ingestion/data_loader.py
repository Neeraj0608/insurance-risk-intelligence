import pandas as pd
import os
from pathlib import Path
from loguru import logger

class IRDAIDataLoader:
    def __init__(self, raw_data_dir: str = "data/raw", processed_data_dir: str = "data/processed"):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        
    def load_raw_data(self, filename: str = "irdai_life_business.csv") -> pd.DataFrame:
        """
        Loads the raw IRDAI dataset from the local directory.
        """
        file_path = self.raw_data_dir / filename
        
        if not file_path.exists():
            logger.error(f"Data file not found: {file_path}")
            logger.info("Please download the real IRDAI dataset and place it in data/raw/. See data/raw/README.md for instructions.")
            raise FileNotFoundError(f"Missing required dataset: {file_path}")
            
        logger.info(f"Loading raw data from {file_path}")
        
        # Handle both CSV and Excel based on extension
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
            
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns.")
        return df
        
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes column names for consistency.
        """
        df = df.copy()
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(r'[^a-z0-9]', '_', regex=True)
            .str.replace(r'_+', '_', regex=True)
        )
        logger.info("Standardized column names.")
        return df
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies basic preprocessing to the raw data.
        """
        df = self.clean_column_names(df)
        
        # Mapping common variations in IRDAI/Dataful columns to a standard schema
        column_mapping = {
            'financial_year': 'fiscal_year',
            'company': 'insurance_company',
            'company_name': 'insurance_company',
            'insurer': 'insurance_company',
            'policies': 'policies_issued',
            'no_of_policies': 'policies_issued',
            'premium': 'premium_collected',
            'first_year_premium': 'premium_collected'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure critical columns exist (basic validation before pandera)
        critical_cols = ['insurance_company', 'premium_collected']
        missing = [col for col in critical_cols if col not in df.columns]
        if missing:
            logger.warning(f"Could not find standard columns: {missing}. Available columns: {df.columns.tolist()}")
            
        return df

    def save_processed_data(self, df: pd.DataFrame, filename: str = "processed_life_business.csv"):
        """
        Saves the cleaned dataset.
        """
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.processed_data_dir / filename
        df.to_csv(out_path, index=False)
        logger.info(f"Saved processed data to {out_path}")
