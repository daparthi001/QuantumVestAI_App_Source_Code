import pandas as pd
from ai_stock_platform.api.ml.ensemble_model import random_forest_predict


def test_random_forest_prediction_shape():
    dates = pd.date_range(end="2024-01-10", periods=30)
    df = pd.DataFrame({'adjusted_close': range(30)}, index=dates)
    result = random_forest_predict('TEST', df, days_ahead=3)
    assert len(result) == 3
    assert 'predicted_close' in result.columns
