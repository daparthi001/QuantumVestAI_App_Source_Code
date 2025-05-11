import pandas as pd

def ensemble_predictions(predictions: list):
    combined = pd.concat(predictions)
    grouped = combined.groupby('ds').mean().reset_index()
    grouped = grouped.sort_values(by='ds')
    return grouped
