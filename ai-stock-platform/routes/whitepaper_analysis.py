from fastapi import APIRouter, HTTPException, Query, Depends
import os
import logging
import yfinance as yf
import pandas as pd
from datetime import datetime
from routes.auth import get_current_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load with PyTorch first
summarizer = None
try:
    os.environ["TRANSFORMERS_FRAMEWORK"] = "pt"  # Force PyTorch mode first
    from transformers import pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)  # device=-1 forces CPU
    logger.info("Using PyTorch backend for transformers")
except Exception as e:
    logger.error(f"PyTorch backend failed: {e}")
    try:
        # Try with tf-keras if available
        os.environ["TRANSFORMERS_FRAMEWORK"] = "tf"
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Reduce TensorFlow logging
        try:
            import tf_keras
        except ImportError:
            logger.warning("tf-keras not found, using smaller model")
            
        import transformers
        from transformers import pipeline
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6", device=-1)
        logger.info("Using TensorFlow backend for transformers")
    except Exception as e2:
        logger.error(f"TensorFlow backend failed: {e2}")
        try:
            os.environ["TRANSFORMERS_FRAMEWORK"] = "pt"
            from transformers import pipeline
            summarizer = pipeline("summarization", model="facebook/bart-base", device=-1)
            logger.info("Using fallback small model with PyTorch")
        except Exception as e3:
            logger.error(f"All model attempts failed: {e3}")

router = APIRouter(prefix="/whitepaper", tags=["whitepaper"])

def get_stock_info(ticker):
    """Get stock information using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {e}")
        return None

@router.get("/analyze")
async def analyze_whitepaper(
    text: str = Query(..., description="Whitepaper text to analyze"),
    ticker: str = Query(None, description="Optional stock ticker to include related data")
):
    response = {}
    
    # Add ticker data if provided
    if ticker:
        try:
            stock_info = get_stock_info(ticker)
            if stock_info:
                response["ticker_data"] = {
                    "name": stock_info.get("shortName", ticker),
                    "sector": stock_info.get("sector", "Unknown"),
                    "industry": stock_info.get("industry", "Unknown"),
                    "market_cap": stock_info.get("marketCap", 0),
                    "current_price": stock_info.get("currentPrice", 0),
                    "recommendation": stock_info.get("recommendationKey", "unknown")
                }
        except Exception as e:
            logger.error(f"Error processing ticker {ticker}: {e}")
            response["ticker_error"] = str(e)
    
    # Text summarization
    if summarizer is None:
        response["error"] = "Summarization model not available"
        response["message"] = "Please install required packages: pip install torch tf-keras"
        response["simple_summary"] = text[:200] + "..." if len(text) > 200 else text
        return response
    
    try:
        # Handle very long inputs by chunking
        if len(text) > 1024:
            logger.info(f"Long text received ({len(text)} chars), chunking...")
            chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
            summaries = []
            
            for i, chunk in enumerate(chunks[:3]):  # Process up to 3 chunks to avoid timeouts
                chunk_summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
                summaries.append(chunk_summary[0]["summary_text"])
            
            final_summary = " ".join(summaries)
            response["summary"] = final_summary
        else:
            # Normal case for shorter text
            summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
            response["summary"] = summary[0]["summary_text"]
    except Exception as e:
        logger.exception("Error during summarization")
        response["error"] = str(e)
        response["simple_summary"] = text[:200] + "..." if len(text) > 200 else text
    
    return response

@router.get("/ticker-report/{ticker}")
async def ticker_whitepaper(
    ticker: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate a comprehensive report for a ticker by analyzing company info and news"""
    try:
        # Get stock information
        stock_info = get_stock_info(ticker)
        if not stock_info:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Extract company description/business summary
        business_summary = stock_info.get("longBusinessSummary", "")
        
        # If we have a summary, analyze it
        if business_summary and summarizer:
            try:
                summary = summarizer(business_summary, max_length=200, min_length=50, do_sample=False)
                analyzed_summary = summary[0]["summary_text"]
            except:
                analyzed_summary = business_summary[:300] + "..."
        else:
            analyzed_summary = "No business summary available"
            
        # Get recent price data
        hist = yf.download(ticker, period="1y")
        price_change = None
        if not hist.empty:
            recent = hist.iloc[-1]
            year_ago = hist.iloc[0] if len(hist) > 1 else recent
            price_change = {
                "current": round(float(recent["Close"]), 2),
                "year_ago": round(float(year_ago["Close"]), 2),
                "change_pct": round(((recent["Close"] - year_ago["Close"]) / year_ago["Close"]) * 100, 2)
            }
        
        # Prepare the report
        report = {
            "ticker": ticker,
            "name": stock_info.get("shortName", ticker),
            "sector": stock_info.get("sector", "Unknown"),
            "industry": stock_info.get("industry", "Unknown"),
            "market_cap": stock_info.get("marketCap", 0),
            "pe_ratio": stock_info.get("trailingPE", 0),
            "dividend_yield": stock_info.get("dividendYield", 0),
            "analyst_recommendation": stock_info.get("recommendationKey", "unknown"),
            "business_summary": analyzed_summary,
            "price_data": price_change,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))