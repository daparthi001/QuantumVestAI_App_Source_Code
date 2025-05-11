from fastapi import APIRouter, HTTPException, Query
from transformers import pipeline
import yfinance as yf
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/whitepaper", tags=["whitepaper"])

# Load a transformer summarization model (can be replaced with better one in prod)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_company_description(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    return stock.info.get("longBusinessSummary", "")

def get_recent_sec_filing_summary(ticker: str) -> str:
    try:
        cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&action=getcompany&count=10"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(cik_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        desc = soup.find("span", class_="companyName")
        return desc.text if desc else "No summary found."
    except Exception as e:
        return f"Error fetching SEC data: {str(e)}"

@router.get("/summarize")
def summarize_company_whitepaper(ticker: str = Query(..., description="Stock ticker")):
    try:
        long_summary = get_company_description(ticker)
        if not long_summary:
            long_summary = get_recent_sec_filing_summary(ticker)
        if not long_summary or len(long_summary) < 100:
            raise Exception("Insufficient data to summarize")

        summary = summarizer(long_summary[:1024], max_length=150, min_length=40, do_sample=False)[0]['summary_text']
        return {
            "ticker": ticker,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize whitepaper: {str(e)}")