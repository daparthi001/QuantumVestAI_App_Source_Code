from fastapi import APIRouter, HTTPException, Query
from transformers import pipeline
import yfinance as yf
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/whitepaper", tags=["whitepaper"])

# Load a transformer summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_company_description(ticker: str) -> str:
    """Get company description from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        description = stock.info.get("longBusinessSummary", "")
        return description
    except Exception as e:
        return f"Error fetching company description: {str(e)}"

def get_recent_sec_filing_summary(ticker: str) -> str:
    """Get recent SEC filing summary"""
    try:
        cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&action=getcompany&count=10"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        res = requests.get(cik_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        desc = soup.find("span", class_="companyName")
        if desc:
            return desc.text
        return "No summary found."
    except Exception as e:
        return f"Error fetching SEC data: {str(e)}"

@router.get("/summarize")
def summarize_company_whitepaper(ticker: str = Query(..., description="Stock ticker")):
    """Summarize company description and SEC filings"""
    try:
        long_summary = get_company_description(ticker)
        
        # If no description found from Yahoo Finance, try SEC filings
        if not long_summary or len(long_summary) < 100:
            long_summary = get_recent_sec_filing_summary(ticker)
            
        # If still no meaningful data, return an error
        if not long_summary or len(long_summary) < 100:
            raise HTTPException(status_code=404, detail="Insufficient data to summarize")

        # Truncate input to maximum length for transformer model
        truncated_text = long_summary[:1024]
        
        # Generate summary using transformer model
        summary = summarizer(
            truncated_text, 
            max_length=150, 
            min_length=40, 
            do_sample=False
        )[0]['summary_text']
        
        return {
            "ticker": ticker,
            "summary": summary,
            "source": "Yahoo Finance" if get_company_description(ticker) else "SEC Filings"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize whitepaper: {str(e)}")