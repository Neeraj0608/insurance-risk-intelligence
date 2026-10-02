import pandera as pa
from pandera import Column, Check, DataFrameSchema
import pandas as pd
from loguru import logger

# Define the expected schema for the processed IRDAI life business data
irdai_schema = DataFrameSchema({
    "fiscal_year": Column(str, Check.str_matches(r"^\d{4}-\d{2}$"), nullable=False),
    "month": Column(str, nullable=False),
    "insurance_company": Column(str, nullable=False),
    "category": Column(str, nullable=True),
    # Some companies might report 0 policies but non-zero premium (e.g., adjustments)
    "policies_issued": Column(float, Check.ge(0), nullable=True), 
    "premium_collected": Column(float, nullable=False),
    "sum_assured": Column(float, Check.ge(0), nullable=True),
}, strict=False) # Strict=False allows extra columns from the raw data

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the dataframe against the IRDAI schema.
    """
    try:
        validated_df = irdai_schema.validate(df)
        logger.info("Data validation passed successfully.")
        return validated_df
    except pa.errors.SchemaError as e:
        logger.error(f"Data validation failed: {e}")
        # In a production pipeline, we might want to quarantine bad rows instead of failing outright.
        # For now, we raise to ensure data integrity.
        raise
