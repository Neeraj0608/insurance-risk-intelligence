import pandas as pd
import numpy as np
from loguru import logger

class RiskAnomalyDetector:
    """
    Detects significant deviations between actual and expected claims/premiums.
    """
    def __init__(self, threshold_percentage: float = 0.50):
        # Default: Anomaly flagged if actual deviates from expected by > 50%
        self.threshold = threshold_percentage
        
    def detect(self, df: pd.DataFrame, actual_col: str, expected_col: str) -> pd.DataFrame:
        """
        Calculates deviations and flags anomalies.
        """
        logger.info("Running anomaly detection...")
        results = df.copy()
        
        # Avoid division by zero
        safe_expected = np.where(results[expected_col] == 0, 1e-5, results[expected_col])
        
        # Deviation calculation: (Actual - Expected) / Expected
        results['deviation_pct'] = (results[actual_col] - results[expected_col]) / safe_expected
        
        # Flag as anomaly if deviation exceeds threshold (positive or negative)
        # Note: In risk, positive deviation (actual > expected) is usually higher risk.
        results['is_anomaly'] = np.abs(results['deviation_pct']) > self.threshold
        results['anomaly_status'] = np.where(
            results['deviation_pct'] > self.threshold, 'Significant High Anomaly',
            np.where(results['deviation_pct'] < -self.threshold, 'Significant Low Anomaly', 'Normal')
        )
        
        num_anomalies = results['is_anomaly'].sum()
        logger.info(f"Detected {num_anomalies} anomalies based on threshold {self.threshold*100}%")
        
        return results
