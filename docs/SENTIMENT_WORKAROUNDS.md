# Stock Sentiment Workarounds Without a Twitter Pro Plan

This guide summarizes alternative approaches for collecting sentiment data when a paid Twitter plan is not available.

## 1. Reddit & News APIs
- Use [NewsAPI.org](https://newsapi.org) for financial headlines.
- Query the Reddit API for subreddits such as `r/stocks` and `r/investing`.
- Analyze text with models like **FinBERT** to obtain sentiment scores.

The `MultiSourceSentimentAnalyzer` in the backend now integrates these sources
directly, fetching news via NewsAPI when an API key is provided and scraping
relevant Reddit discussions for sentiment analysis using FinBERT.

These sources provide rich, real sentiment data without relying on Twitter.

## 2. Public Twitter Search via Web Scraping
Tools such as [`snscrape`](https://github.com/JustAnotherArchivist/snscrape) can fetch tweets without using the official API:

```bash
pip install snscrape
```

```python
import snscrape.modules.twitter as sntwitter

query = "$AAPL since:2024-07-01 until:2024-07-25"
for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    print(f"{tweet.date} - @{tweet.user.username}: {tweet.content}")
```

⚠️ **Use cautiously.** Web scraping may conflict with Twitter's Terms of Service and should be limited to prototyping or personal experimentation.

## 3. Financial News Providers
Services like **Finviz**, **Yahoo Finance**, and **Alpha Vantage** offer:
- Stock news and trending tickers
- Market sentiment indicators
- Additional financial data feeds

## 4. Recommended Basic-Plan Architecture
A possible setup without a paid Twitter subscription:

```
[Reddit API]         [NewsAPI]        [Twitter (limited)]
      ↓                   ↓                    ↓
 [Text Pipeline + FinBERT/NLTK sentiment model]
      ↓
 [QuantumVestAI Backend API] — Python/FastAPI
      ↓
 [Frontend UI] — React/Next.js
```

This approach keeps the application functional even on the basic plan while still delivering social sentiment insights.
