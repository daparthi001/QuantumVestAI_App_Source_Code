import pandas as pd
from prophet_model import run_prophet
from xgboost_model import run_xgboost
from ensemble import ensemble_predictions

def run_ensemble_pipeline(df: pd.DataFrame, forecast_days: int = 7):
    preds_prophet = run_prophet(df, forecast_days)
    preds_xgb = run_xgboost(df, forecast_days)
    return ensemble_predictions([preds_prophet, preds_xgb])
