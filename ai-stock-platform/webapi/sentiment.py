from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from fastapi import APIRouter, HTTPException, Query
import requests
import os

import tweepy

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

# Load FinBERT model
MODEL_NAME = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Twitter API Setup
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def analyze_sentiment(text: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    scores = outputs[0][0].detach().numpy()
    probs = softmax(scores)
    return {
        "positive": float(probs[0]),
        "neutral": float(probs[1]),
        "negative": float(probs[2]),
    }

@router.get("/analyze")
def analyze(text: str = Query(..., description="Text to analyze")):
    try:
        return analyze_sentiment(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticker")
def analyze_ticker(ticker: str = Query(..., description="Stock ticker symbol")):
    try:
        query = f"${ticker} lang:en -is:retweet"
        tweets = twitter_client.search_recent_tweets(query=query, max_results=10)

        sentiments = []
        for tweet in tweets.data:
            result = analyze_sentiment(tweet.text)
            sentiments.append(result)

        # Average the sentiment
        avg_sentiment = {
            "positive": sum(s["positive"] for s in sentiments) / len(sentiments),
            "neutral": sum(s["neutral"] for s in sentiments) / len(sentiments),
            "negative": sum(s["negative"] for s in sentiments) / len(sentiments),
        }
        return {"ticker": ticker, "sentiment": avg_sentiment}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import yfinance as yf

@router.get("/analysis")
def get_long_term_analysis(ticker: str = Query(..., description="Stock ticker symbol")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract relevant analysis/valuation fields
        return {
            "ticker": ticker,
            "longName": info.get("longName"),
            "sector": info.get("sector"),
            "forwardPE": info.get("forwardPE"),
            "recommendationKey": info.get("recommendationKey"),
            "targetHighPrice": info.get("targetHighPrice"),
            "targetLowPrice": info.get("targetLowPrice"),
            "targetMeanPrice": info.get("targetMeanPrice"),
            "targetMedianPrice": info.get("targetMedianPrice"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Yahoo Finance data: {str(e)}")