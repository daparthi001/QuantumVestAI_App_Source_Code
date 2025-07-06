import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import settings

# Define constants locally that are missing from core.config.constants
DATE_FORMAT = "%Y-%m-%d"
TIMEFRAME_1D = "1d"
TIMEFRAME_1Y = "1y"
TIMEFRAME_MAX = "max"

# Define market indices
MARKET_INDICES = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "Nasdaq": "^IXIC",
    "Russell 2000": "^RUT",
    "VIX": "^VIX"
}

# Default tickers
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

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
            cls.logger.error(f"Error getting stock info for {ticker}: {str(e)}")
            raise ValueError(f"Could not retrieve information for ticker {ticker}")
    
    @classmethod
    def get_historical_data(
        cls, 
        ticker: str, 
        period: str = TIMEFRAME_1Y, 
        interval: str = TIMEFRAME_1D
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
                    # Skip tickers that cause errors
                    continue
                    
            return results
            
        except Exception as e:
            cls.logger.error(f"Error searching for tickers with query {query}: {str(e)}")
            return []  # Return empty list on error
    
    @classmethod
    def get_market_summary(cls) -> Dict[str, Any]:
        """
        Get summary of major market indices and sectors
        
        Returns:
            Dictionary containing market summary data
        """
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
                "Communication Services": "VOX"
            }
            
            for sector_name, etf_symbol in sector_etfs.items():
                    # Skip sectors that cause errors
                    continue
            
            # Get top gainers, losers, and active stocks
            # For simplicity, using a sample of commonly traded stocks
            sample_tickers = DEFAULT_TICKERS + ["GOOGL", "FB", "NFLX", "TSLA"]
            
            stocks_data = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(cls.get_stock_info, ticker): ticker for ticker in sample_tickers}
                for future in as_completed(futures):
                    ticker = futures[future]
                        # Skip stocks that cause errors
                        continue
            
            # Sort for top gainers, losers, and active stocks
            if stocks_data:
                # Top gainers
                gainers = sorted(stocks_data, key=lambda x: x.get("change_percent", 0), reverse=True)[:5]
                result["top_movers"]["gainers"] = gainers
                
                # Top losers
                losers = sorted(stocks_data, key=lambda x: x.get("change_percent", 0))[:5]
                result["top_movers"]["losers"] = losers
                
                # Most active by volume
                active = sorted(stocks_data, key=lambda x: x.get("volume", 0), reverse=True)[:5]
                result["top_movers"]["active"] = active
            
            return result
            
        except Exception as e:
            cls.logger.error(f"Error getting market summary: {str(e)}")
            return {"indices": {}, "sectors": {}, "top_movers": {}}
    
    @classmethod
    def get_technical_indicators(cls, ticker: str, period: str = TIMEFRAME_1Y) -> Dict[str, Any]:
        """
        Calculate basic technical indicators for a stock
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for data
            
        Returns:
            Dictionary containing technical indicators
        """
            cls.logger.error(f"Error calculating technical indicators for {ticker}: {str(e)}")
            return {
                "moving_averages": {"ma_50": None, "ma_200": None},
                "rsi": None,
                "bollinger_bands": {"upper": None, "middle": None, "lower": None},
                "signals": {"ma_trend": "unknown", "rsi_signal": "unknown", "bollinger_position": "unknown"}
            }