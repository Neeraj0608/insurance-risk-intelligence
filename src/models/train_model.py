import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import TimeSeriesSplit
from loguru import logger
import mlflow
import mlflow.xgboost

class BaselineModel:
    """Naive previous-period baseline."""
    def predict(self, df: pd.DataFrame, target_col: str) -> np.ndarray:
        # Prediction is simply the value from the previous period
        lag_col = f"{target_col.split('_')[0]}_lag_1"
        if lag_col in df.columns:
            return df[lag_col].values
        else:
            return np.zeros(len(df))

class MovingAverageModel:
    """3-Month moving average baseline."""
    def predict(self, df: pd.DataFrame, target_col: str) -> np.ndarray:
        ma_col = f"{target_col.split('_')[0]}_rolling_3m_avg"
        if ma_col in df.columns:
            return df[ma_col].values
        else:
            return np.zeros(len(df))

class XGBoostForecaster:
    """XGBoost ML Forecasting Model."""
    def __init__(self):
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.features = None
        
    def train(self, X: pd.DataFrame, y: pd.Series):
        self.features = X.columns.tolist()
        self.model.fit(X, y)
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X[self.features])

def evaluate_models(df: pd.DataFrame, target_col: str = 'premium_collected'):
    """
    Evaluates baselines vs XGBoost using time-aware splitting.
    """
    logger.info(f"Evaluating models for target: {target_col}")
    
    # Sort chronologically to ensure no future leakage in validation
    df = df.sort_values(by=['fiscal_year', 'month_num'])
    
    # Define features
    feature_cols = [
        'premium_lag_1', 'policies_lag_1', 'premium_rolling_3m_avg', 
        'policies_rolling_3m_avg', 'month_num'
    ]
    
    # One-hot encode categorical features for XGBoost
    if 'insurance_company' in df.columns:
        company_dummies = pd.get_dummies(df['insurance_company'], prefix='comp')
        feature_cols.extend(company_dummies.columns)
        X = pd.concat([df[feature_cols[:5]], company_dummies], axis=1)
    else:
        X = df[feature_cols]
        
    y = df[target_col]
    
    # Time-aware split (last 20% of chronological data as test)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    results = {}
    
    # 1. Naive Baseline
    baseline = BaselineModel()
    y_pred_naive = baseline.predict(df.iloc[split_idx:], target_col)
    results['Naive_Baseline'] = {
        'MAE': mean_absolute_error(y_test, y_pred_naive),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_naive))
    }
    
    # 2. Moving Average Baseline
    ma_model = MovingAverageModel()
    y_pred_ma = ma_model.predict(df.iloc[split_idx:], target_col)
    results['Moving_Average'] = {
        'MAE': mean_absolute_error(y_test, y_pred_ma),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_ma))
    }
    
    # 3. XGBoost
    # Start MLflow run
    mlflow.set_experiment("insurance-risk-intelligence")
    with mlflow.start_run(run_name="XGBoost_Forecaster"):
        xgb_model = XGBoostForecaster()
        xgb_model.train(X_train, y_train)
        y_pred_xgb = xgb_model.predict(X_test)
        
        xgb_metrics = {
            'MAE': mean_absolute_error(y_test, y_pred_xgb),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_xgb))
        }
        results['XGBoost'] = xgb_metrics
        
        mlflow.log_metrics(xgb_metrics)
        mlflow.xgboost.log_model(xgb_model.model, "model")
        
    for model_name, metrics in results.items():
        logger.info(f"{model_name} - MAE: {metrics['MAE']:.2f}, RMSE: {metrics['RMSE']:.2f}")
        
    return xgb_model, results, X_test, y_test, y_pred_xgb
