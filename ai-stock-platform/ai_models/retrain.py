import pandas as pd
import yfinance as yf
from ai_models.prophet_model import run_prophet
from ai_models.xgboost_model import run_xgboost
import datetime
import json
import requests
import os

tickers = ["AAPL", "MSFT", "GOOG"]

def send_slack(message):
    webhook = os.getenv("SLACK_WEBHOOK")
    if webhook:
        requests.post(webhook, json={"text": message})

for ticker in tickers:
    df = yf.download(ticker, period="3y").reset_index()
    _ = run_prophet(df)
    _ = run_xgboost(df)
    send_slack(f"✅ Model retrained for {ticker} at {datetime.datetime.utcnow()}")
