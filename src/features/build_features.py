import pandas as pd
import numpy as np
from loguru import logger
from typing import Tuple

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs temporal and categorical features from the processed IRDAI dataset.
    
    Expected input columns:
    - fiscal_year
    - month
    - insurance_company
    - category
    - policies_issued
    - premium_collected
    - sum_assured
    """
    logger.info("Starting feature engineering...")
    df = df.copy()
    
    # 1. Temporal Parsing
    # Month mapping for sorting and rolling calculations (assuming standard financial year April-March)
    month_map = {
        'April': 1, 'May': 2, 'June': 3, 'July': 4, 'August': 5, 'September': 6,
        'October': 7, 'November': 8, 'December': 9, 'January': 10, 'February': 11, 'March': 12,
        'Apr': 1, 'May': 2, 'Jun': 3, 'Jul': 4, 'Aug': 5, 'Sep': 6,
        'Oct': 7, 'Nov': 8, 'Dec': 9, 'Jan': 10, 'Feb': 11, 'Mar': 12
    }
    
    if 'month' in df.columns:
        df['month_num'] = df['month'].map(month_map)
        
    # Sort chronologically for proper rolling features
    df = df.sort_values(by=['insurance_company', 'category', 'fiscal_year', 'month_num'])
    
    # 2. Base Metrics
    # Claim frequency = claims / exposure. 
    # NOTE: Since IRDAI Life monthly data focuses on New Business (Premiums/Policies), 
    # we forecast 'premium_collected' or 'policies_issued'. 
    # If using claims data, this would be claims / policies. 
    # We will compute 'average_premium_per_policy' (Severity proxy)
    df['average_premium_per_policy'] = np.where(
        df['policies_issued'] > 0, 
        df['premium_collected'] / df['policies_issued'], 
        0
    )
    
    # 3. Rolling / Lagged Temporal Features (Target: premium_collected or policies_issued)
    # Group by company and category to compute historical features without leakage
    grouped = df.groupby(['insurance_company', 'category'])
    
    # Lag 1 (Previous Month)
    df['premium_lag_1'] = grouped['premium_collected'].shift(1)
    df['policies_lag_1'] = grouped['policies_issued'].shift(1)
    
    # Rolling 3-month averages (excluding current month to prevent leakage)
    df['premium_rolling_3m_avg'] = grouped['premium_collected'].apply(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    ).reset_index(level=[0,1], drop=True)
    
    df['policies_rolling_3m_avg'] = grouped['policies_issued'].apply(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    ).reset_index(level=[0,1], drop=True)
    
    # Growth Rates (MoM)
    df['premium_mom_growth'] = (df['premium_collected'] - df['premium_lag_1']) / (df['premium_lag_1'] + 1e-5)
    
    # 4. Handle Missing Values from Lags
    # For the first few months, lags will be NaN. We fill with 0 or the global company mean.
    features_to_fill = ['premium_lag_1', 'policies_lag_1', 'premium_rolling_3m_avg', 'policies_rolling_3m_avg', 'premium_mom_growth']
    df[features_to_fill] = df[features_to_fill].fillna(0)
    
    logger.info(f"Feature engineering complete. Dataset shape: {df.shape}")
    
    # Document features
    feature_metadata = {
        'premium_lag_1': 'Premium collected in the previous period.',
        'premium_rolling_3m_avg': 'Average premium over the prior 3 periods. Leakage prevented via shift(1).',
        'average_premium_per_policy': 'Proxy for severity; Premium / Policies.',
        'premium_mom_growth': 'Month-over-month growth rate in premium.'
    }
    
    return df, feature_metadata

if __name__ == "__main__":
    # Simple test if run directly
    print("Feature engineering module ready.")
