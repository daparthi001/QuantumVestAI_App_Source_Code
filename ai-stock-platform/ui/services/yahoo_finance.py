import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import yfinance as yf
from ui.config.constants import (
    DATE_FORMAT,
    DEFAULT_TICKERS,
    MARKET_INDICES,
    TIMEFRAME_1D,
    TIMEFRAME_1Y,
    TIMEFRAME_MAX,
)

# Import settings from the shared configuration module.
# ``ui.config.settings`` was deprecated and no longer exposes a ``settings``
# instance which caused runtime import errors when this service was imported
# directly.  Using the shared ``core.config.settings`` ensures the service
# always has access to the application settings object.
from core.config.settings import settings


class YahooFinanceService:
    """Service for interacting with Yahoo Finance API"""

    logger = logging.getLogger(__name__)

    @classmethod
    def get_stock_info(cls, ticker: str) -> Dict[str, Any]:
        """
        Get basic information for a stock ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary containing stock information
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            # Extract the most relevant information
            stock_info = {
                "name": info.get("shortName", info.get("longName", ticker)),
                "ticker": ticker,
                "price": info.get("regularMarketPrice", info.get("currentPrice", 0)),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0),
                "previous_close": info.get("regularMarketPreviousClose", 0),
                "open": info.get("regularMarketOpen", 0),
                "day_high": info.get("regularMarketDayHigh", 0),
                "day_low": info.get("regularMarketDayLow", 0),
                "volume": info.get("regularMarketVolume", 0),
                "average_volume": info.get("averageVolume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "dividend_yield": info.get("dividendYield", None),
                "high_52w": info.get("fiftyTwoWeekHigh", 0),
                "low_52w": info.get("fiftyTwoWeekLow", 0),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "exchange": info.get("exchange", "Unknown"),
                "currency": info.get("currency", "USD"),
                "logo_url": info.get("logo_url", ""),
                "website": info.get("website", ""),
                "description": info.get("longBusinessSummary", ""),
            }

            # Format the dividend yield as percentage if available
            if stock_info["dividend_yield"] is not None:
                stock_info["dividend_yield"] = stock_info["dividend_yield"] * 100

            return stock_info

        except Exception as e:
            cls.logger.error(f"Error getting stock info for {ticker}: {str(e)}")
            raise ValueError(f"Could not retrieve information for ticker {ticker}")

    @classmethod
    def get_historical_data(
        cls, ticker: str, period: str = TIMEFRAME_1Y, interval: str = TIMEFRAME_1D
    ) -> pd.DataFrame:
        """
        Get historical price data for a ticker

        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame containing historical data
        """
        try:
            # For intraday data, we need to limit the period to avoid hitting API limits
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                if period == TIMEFRAME_MAX or period == TIMEFRAME_1Y:
                    period = "7d"  # Limit to 7 days for intraday data

            data = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                show_errors=False,
                auto_adjust=True,
            )

            # Reset index to make Date a column instead of index
            data = data.reset_index()

            # Convert timestamp to string format
            if "Date" in data.columns:
                data["Date"] = data["Date"].dt.strftime(DATE_FORMAT)

            # Rename columns to more user-friendly names
            data = data.rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume",
                    "Adj Close": "adjusted_close",
                }
            )

            return data

        except Exception as e:
            cls.logger.error(f"Error getting historical data for {ticker}: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    @classmethod
    def get_stock_news(cls, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news articles for a specific stock

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of news articles to return

        Returns:
            List of news article dictionaries
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            news = ticker_obj.news

            # Limit the number of articles
            news = news[:limit]

            # Process news items to standardize format
            processed_news = []
            for item in news:
                # Convert timestamps to readable date/time
                published_at = datetime.fromtimestamp(
                    item.get("providerPublishTime", 0)
                )

                processed_news.append(
                    {
                        "title": item.get("title", ""),
                        "summary": item.get("summary", ""),
                        "url": item.get("link", ""),
                        "published_at": published_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "source": item.get("publisher", "Yahoo Finance"),
                        "thumbnail": item.get("thumbnail", {})
                        .get("resolutions", [{}])[0]
                        .get("url", ""),
                    }
                )

            return processed_news

        except Exception as e:
            cls.logger.error(f"Error getting news for {ticker}: {str(e)}")
            return []  # Return empty list on error

    @classmethod
    def search_tickers(cls, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for ticker symbols based on a query

        Args:
            query: Search query (company name or ticker)
            limit: Maximum number of results to return

        Returns:
            List of matching ticker dictionaries
        """
        try:
            # Use yfinance's search functionality
            import yfinance as yf

            # Get tickers that match the query
            tickers = yf.Tickers(query).tickers

            results = []
            for ticker_symbol, ticker_obj in tickers.items():
                try:
                    info = ticker_obj.info

                    # Check if we got valid data
                    if not info or "shortName" not in info:
                        continue

                    results.append(
                        {
                            "symbol": ticker_symbol,
                            "name": info.get(
                                "shortName", info.get("longName", ticker_symbol)
                            ),
                            "exchange": info.get("exchange", ""),
                            "sector": info.get("sector", ""),
                            "industry": info.get("industry", ""),
                        }
                    )

                    # Limit the results
                    if len(results) >= limit:
                        break

                except Exception:
                    # Skip tickers that cause errors
                    continue

            return results

        except Exception as e:
            cls.logger.error(
                f"Error searching for tickers with query {query}: {str(e)}"
            )
            return []  # Return empty list on error

    @classmethod
    def get_market_summary(cls) -> Dict[str, Any]:
        """
        Get summary of major market indices and sectors

        Returns:
            Dictionary containing market summary data
        """
        try:
            result = {"indices": {}, "sectors": {}, "top_movers": {}}

            # Get major indices
            for name, symbol in MARKET_INDICES.items():
                try:
                    index_data = cls.get_stock_info(symbol)
                    result["indices"][symbol] = {
                        "name": name,
                        "price": index_data.get("price", 0),
                        "change": index_data.get("change", 0),
                        "change_percent": index_data.get("change_percent", 0),
                    }
                except Exception:
                    # Skip indices that cause errors
                    continue

            # Get sector performance using Vanguard ETFs as proxies
            sector_etfs = {
                "Technology": "VGT",
                "Healthcare": "VHT",
                "Financials": "VFH",
                "Consumer Discretionary": "VCR",
                "Consumer Staples": "VDC",
                "Energy": "VDE",
                "Industrials": "VIS",
                "Utilities": "VPU",
                "Materials": "VAW",
                "Real Estate": "VNQ",
                "Communication Services": "VOX",
            }

            for sector_name, etf_symbol in sector_etfs.items():
                try:
                    sector_data = cls.get_stock_info(etf_symbol)
                    result["sectors"][sector_name] = {
                        "price": sector_data.get("price", 0),
                        "change": sector_data.get("change", 0),
                        "change_percent": sector_data.get("change_percent", 0),
                    }
                except Exception:
                    # Skip sectors that cause errors
                    continue

            # Get top gainers, losers, and active stocks
            # For simplicity, using a sample of commonly traded stocks
            sample_tickers = DEFAULT_TICKERS + ["GOOGL", "FB", "NFLX", "TSLA"]

            stocks_data = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(cls.get_stock_info, ticker): ticker
                    for ticker in sample_tickers
                }
                for future in as_completed(futures):
                    ticker = futures[future]
                    try:
                        data = future.result()
                        stocks_data.append(data)
                    except Exception:
                        # Skip stocks that cause errors
                        continue

            # Sort for top gainers, losers, and active stocks
            if stocks_data:
                # Top gainers
                gainers = sorted(
                    stocks_data, key=lambda x: x.get("change_percent", 0), reverse=True
                )[:5]
                result["top_movers"]["gainers"] = gainers

                # Top losers
                losers = sorted(stocks_data, key=lambda x: x.get("change_percent", 0))[
                    :5
                ]
                result["top_movers"]["losers"] = losers

                # Most active by volume
                active = sorted(
                    stocks_data, key=lambda x: x.get("volume", 0), reverse=True
                )[:5]
                result["top_movers"]["active"] = active

            return result

        except Exception as e:
            cls.logger.error(f"Error getting market summary: {str(e)}")
            return {"indices": {}, "sectors": {}, "top_movers": {}}

    @classmethod
    def get_technical_indicators(
        cls, ticker: str, period: str = TIMEFRAME_1Y
    ) -> Dict[str, Any]:
        """
        Calculate basic technical indicators for a stock

        Args:
            ticker: Stock ticker symbol
            period: Time period for data

        Returns:
            Dictionary containing technical indicators
        """
        try:
            # Get historical data
            data = cls.get_historical_data(ticker, period=period)

            if data.empty:
                raise ValueError(f"No historical data available for {ticker}")

            # Calculate moving averages
            data["MA_50"] = data["close"].rolling(window=50).mean()
            data["MA_200"] = data["close"].rolling(window=200).mean()

            # Calculate Relative Strength Index (RSI)
            # Simplified implementation
            delta = data["close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()

            rs = avg_gain / avg_loss
            data["RSI"] = 100 - (100 / (1 + rs))

            # Calculate Bollinger Bands
            data["BB_MIDDLE"] = data["close"].rolling(window=20).mean()
            std_dev = data["close"].rolling(window=20).std()
            data["BB_UPPER"] = data["BB_MIDDLE"] + (std_dev * 2)
            data["BB_LOWER"] = data["BB_MIDDLE"] - (std_dev * 2)

            # Extract the latest values
            latest = data.iloc[-1].to_dict()

            # Prepare indicators dictionary
            indicators = {
                "moving_averages": {
                    "ma_50": latest.get("MA_50"),
                    "ma_200": latest.get("MA_200"),
                },
                "rsi": latest.get("RSI"),
                "bollinger_bands": {
                    "upper": latest.get("BB_UPPER"),
                    "middle": latest.get("BB_MIDDLE"),
                    "lower": latest.get("BB_LOWER"),
                },
            }

            # Add trend signals
            indicators["signals"] = {
                "ma_trend": "bullish"
                if latest.get("MA_50", 0) > latest.get("MA_200", 0)
                else "bearish",
                "rsi_signal": "oversold"
                if latest.get("RSI", 50) < 30
                else "overbought"
                if latest.get("RSI", 50) > 70
                else "neutral",
                "bollinger_position": "upper"
                if latest.get("close", 0) > latest.get("BB_UPPER", 0)
                else "lower"
                if latest.get("close", 0) < latest.get("BB_LOWER", 0)
                else "middle",
            }

            return indicators

        except Exception as e:
            cls.logger.error(
                f"Error calculating technical indicators for {ticker}: {str(e)}"
            )
            return {
                "moving_averages": {"ma_50": None, "ma_200": None},
                "rsi": None,
                "bollinger_bands": {"upper": None, "middle": None, "lower": None},
                "signals": {
                    "ma_trend": "unknown",
                    "rsi_signal": "unknown",
                    "bollinger_position": "unknown",
                },
            }
