import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loguru import logger

class ModelExplainer:
    def __init__(self, model, feature_names: list):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)
        
    def get_feature_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        """Calculate global feature importance."""
        logger.info("Calculating SHAP feature importance...")
        shap_values = self.explainer.shap_values(X)
        
        # Calculate mean absolute SHAP value for each feature
        mean_shap = np.abs(shap_values).mean(axis=0)
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': mean_shap
        }).sort_values(by='Importance', ascending=False)
        
        return importance_df
        
    def explain_prediction(self, X_instance: pd.DataFrame) -> dict:
        """Explain a single prediction."""
        shap_values = self.explainer.shap_values(X_instance)
        expected_value = self.explainer.expected_value
        
        # Ensure it handles whether expected_value is a scalar or array
        if isinstance(expected_value, np.ndarray):
            expected_value = expected_value[0]
            
        values = shap_values[0] if len(shap_values.shape) > 1 else shap_values
        
        contributions = []
        for feature, val in zip(self.feature_names, values):
            contributions.append({
                'Feature': feature,
                'Contribution': float(val),
                'Direction': 'Positive' if val > 0 else 'Negative'
            })
            
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x['Contribution']), reverse=True)
        
        return {
            'Base_Value': float(expected_value),
            'Prediction': float(expected_value + np.sum(values)),
            'Top_Positive_Factors': [c for c in contributions if c['Direction'] == 'Positive'][:3],
            'Top_Negative_Factors': [c for c in contributions if c['Direction'] == 'Negative'][:3]
        }
