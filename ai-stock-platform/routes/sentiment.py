from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from fastapi import APIRouter, HTTPException, Query
import requests
import os
import yfinance as yf
import tweepy

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

# Load FinBERT model
MODEL_NAME = "yiyanghkust/finbert-tone"
tokenizer = None
model = None

def load_models():
    """Lazy loading of models to save memory"""
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        except Exception as e:
            print(f"Error loading FinBERT model: {str(e)}")
            # Fall back to a simpler model if needed

# Twitter API Setup
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
twitter_client = None if not TWITTER_BEARER_TOKEN else tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of a text using FinBERT"""
    load_models()
    
    if tokenizer is None or model is None:
        return {"positive": 0.33, "neutral": 0.34, "negative": 0.33, "error": "Model not loaded"}
        
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        outputs = model(**inputs)
        scores = outputs[0][0].detach().numpy()
        probs = softmax(scores)
        return {
            "positive": float(probs[0]),
            "neutral": float(probs[1]),
            "negative": float(probs[2]),
        }
    except Exception as e:
        return {"positive": 0.33, "neutral": 0.34, "negative": 0.33, "error": str(e)}

@router.get("/analyze")
def analyze(text: str = Query(..., description="Text to analyze")):
    """Analyze sentiment of provided text"""
    try:
        return analyze_sentiment(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticker")
def analyze_ticker(ticker: str = Query(..., description="Stock ticker symbol")):
    """Analyze social media sentiment for a ticker"""
    try:
        if not twitter_client:
            return {
                "ticker": ticker,
                "sentiment": {"positive": 0.33, "neutral": 0.34, "negative": 0.33},
                "error": "Twitter API not configured"
            }
            
        query = f"${ticker} lang:en -is:retweet"
        tweets = twitter_client.search_recent_tweets(query=query, max_results=10)

        if not tweets.data or len(tweets.data) == 0:
            return {
                "ticker": ticker,
                "sentiment": {"positive": 0.33, "neutral": 0.34, "negative": 0.33},
                "error": "No tweets found for ticker"
            }

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
        return {"ticker": ticker, "sentiment": avg_sentiment, "tweets_analyzed": len(sentiments)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis")
def get_long_term_analysis(ticker: str = Query(..., description="Stock ticker symbol")):
    """Get analyst recommendations and valuation metrics"""
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