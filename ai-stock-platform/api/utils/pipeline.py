import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

import aiohttp
import numpy as np
import pandas as pd
from core.cache import cache
from core.config import settings

from models.finbert_sentiment import FinBertSentiment

logger = logging.getLogger("api")

class DataPipeline:
    """
    Pipeline for processing stock data and preparing it for forecasting.
    
    The pipeline handles:
    1. Data fetching from various sources
    2. Data cleaning and preprocessing
    3. Feature engineering
    4. Technical indicators calculation
    5. Sentiment analysis integration
    6. Pipeline execution with caching
    """
    
    def __init__(self):
        """Initialize data pipeline."""
        self.stages = []
        self.finbert = FinBertSentiment()
        self.http_session = None
    
    async def setup(self):
        """Set up HTTP session for async requests."""
        if self.http_session is None:
            self.http_session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session."""
        if self.http_session:
            await self.http_session.close()
            self.http_session = None
    
    def add_stage(self, stage: 'PipelineStage') -> 'DataPipeline':
        """
        Add a processing stage to the pipeline.
        
        Args:
            stage: Pipeline stage to add
            
        Returns:
            Self for chaining
        """
        self.stages.append(stage)
        return self
    
    async def execute(
        self, ticker: str, period: str = "1y", include_sentiment: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the pipeline for a stock ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for historical data
            include_sentiment: Whether to include sentiment analysis
            
        Returns:
            Dictionary with processed data and metadata
        """
        try:
            await self.setup()
            
            # Initialize pipeline data
            pipeline_data = {
                "ticker": ticker,
                "period": period,
                "start_time": datetime.utcnow(),
                "raw_data": None,
                "processed_data": None,
                "features": {},
                "metadata": {
                    "source": "pipeline",
                    "version": "1.0.0",
                    "stages_executed": []
                }
            }
            
            # Execute each stage in sequence
            for stage in self.stages:
                stage_name = stage.__class__.__name__
                try:
                    logger.debug(f"Executing pipeline stage: {stage_name}")
                    pipeline_data = await stage.process(pipeline_data, self)
                    pipeline_data["metadata"]["stages_executed"].append(stage_name)
                except Exception as e:
                    logger.exception(f"Error in pipeline stage {stage_name}: {e}")
                    # Continue with next stage
            
            # Include sentiment analysis if requested
            if include_sentiment:
                try:
                    sentiment_data = await self._get_sentiment_data(ticker)
                    pipeline_data["sentiment"] = sentiment_data
                except Exception as e:
                    logger.exception(f"Error getting sentiment data: {e}")
                    pipeline_data["sentiment"] = None
            
            # Calculate execution time
            pipeline_data["execution_time"] = (
                datetime.utcnow() - pipeline_data["start_time"]
            ).total_seconds()
            
            return pipeline_data
            
        except Exception as e:
            logger.exception(f"Error executing pipeline for {ticker}: {e}")
            return {
                "ticker": ticker,
                "error": str(e),
                "metadata": {
                    "success": False,
                    "error_type": e.__class__.__name__
                }
            }
    
    @cache(ttl_seconds=3600, key_prefix="sentiment")
    async def _get_sentiment_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get sentiment data for a stock ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with sentiment data
        """
        # Fetch news articles for the ticker
        news_items = await self._fetch_news(ticker)
        
        # Analyze sentiment
        news_with_sentiment = self.finbert.analyze_news(news_items)
        
        # Generate sentiment summary
        sentiment_summary = self.finbert.get_stock_sentiment_summary(news_with_sentiment)
        
        return {
            "summary": sentiment_summary,
            "news": news_with_sentiment[:20]  # Limit to 20 articles
        }
    
    async def _fetch_news(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Fetch news articles for a stock ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        # In real implementation, fetch from a news API
        # For this example, generate mock news
        return self._generate_mock_news(ticker)
    
    def _generate_mock_news(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Generate mock news for demonstration.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of mock news articles
        """
        # Define some templates for different sentiment categories
        positive_templates = [
            "{ticker} Reports Strong Quarterly Earnings, Exceeding Expectations",
            "{ticker} Announces New Product Launch, Analysts Optimistic",
            "Analysts Upgrade {ticker} Stock Rating to 'Buy'",
            "{ticker} Expands Market Share in Growing Sector",
            "{ticker} CEO Forecasts Record Growth in Coming Year",
        ]
        
        neutral_templates = [
            "{ticker} Releases Quarterly Results In Line With Expectations",
            "{ticker} Appoints New Chief Financial Officer",
            "{ticker} to Present at Upcoming Industry Conference",
            "{ticker} Completes Previously Announced Acquisition",
            "Regulatory Review of {ticker}'s Merger Proceeding as Expected",
        ]
        
        negative_templates = [
            "{ticker} Misses Earnings Expectations, Shares Drop",
            "{ticker} Announces Restructuring Plan, Including Layoffs",
            "Analysts Downgrade {ticker} Stock Due to Competitive Pressures",
            "{ticker} Faces Lawsuit Over Product Safety Concerns",
            "{ticker} Lowers Guidance for Next Quarter, Citing Market Uncertainty",
        ]
        
        # Generate 15 news articles with mixed sentiment
        news = []
        now = datetime.utcnow()
        
        # Use more positive news if ticker starts with A-M, more negative otherwise
        # Just to create some variety in the mock data
        if ticker[0].upper() < 'N':
            sentiment_distribution = [0.5, 0.3, 0.2]  # Positive, neutral, negative
        else:
            sentiment_distribution = [0.2, 0.3, 0.5]  # Positive, neutral, negative
        
        for i in range(15):
            # Determine sentiment category based on distribution
            rand = np.random.random()
            if rand < sentiment_distribution[0]:
                template = np.random.choice(positive_templates)
                sentiment = "positive"
            elif rand < sentiment_distribution[0] + sentiment_distribution[1]:
                template = np.random.choice(neutral_templates)
                sentiment = "neutral"
            else:
                template = np.random.choice(negative_templates)
                sentiment = "negative"
            
            # Generate news article
            title = template.format(ticker=ticker)
            
            # Generate a more detailed description
            descriptions = {
                "positive": [
                    f"{ticker} reported quarterly earnings that exceeded analyst expectations, driving shares up in after-hours trading.",
                    f"Analysts are optimistic about {ticker}'s growth prospects following recent strategic initiatives.",
                    f"The market responded positively to {ticker}'s latest announcements, with trading volume above average."
                ],
                "neutral": [
                    f"{ticker}'s recent performance has aligned with market expectations, with stable revenue growth.",
                    f"Industry experts maintain a neutral outlook on {ticker}'s competitive position in the market.",
                    f"Shareholders of {ticker} approved all proposed measures at the annual meeting held yesterday."
                ],
                "negative": [
                    f"{ticker} faces increased competition and margin pressure, according to industry analysts.",
                    f"The recent quarterly results for {ticker} disappointed investors, who had expected stronger growth.",
                    f"Market uncertainty has negatively impacted {ticker}'s forecast for the coming quarters."
                ]
            }
            
            description = np.random.choice(descriptions[sentiment])
            
            # Generate a random date within the last 30 days
            days_ago = np.random.randint(0, 30)
            published_at = (now - timedelta(days=days_ago, 
                                          hours=np.random.randint(0, 24))).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Create news item
            news.append({
                "title": title,
                "description": description,
                "source": np.random.choice(["Financial Times", "Bloomberg", "WSJ", "Reuters", "CNBC"]),
                "url": f"https://example.com/news/{ticker.lower()}/{i}",
                "published_at": published_at,
                # Don't include sentiment here - it will be added by FinBERT
            })
        
        return news


class PipelineStage(ABC):
    """Abstract base class for pipeline stages."""
    
    @abstractmethod
    async def process(
        self, data: Dict[str, Any], pipeline: 'DataPipeline'
    ) -> Dict[str, Any]:
        """
        Process data in this pipeline stage.
        
        Args:
            data: Pipeline data
            pipeline: Pipeline instance
            
        Returns:
            Updated pipeline data
        """
        pass


class DataFetchStage(PipelineStage):
    """Pipeline stage for fetching stock data."""
    
    async def process(
        self, data: Dict[str, Any], pipeline: 'DataPipeline'
    ) -> Dict[str, Any]:
        """
        Fetch historical price data for a ticker.
        
        Args:
            data: Pipeline data
            pipeline: Pipeline instance
            
        Returns:
            Updated pipeline data with raw price data
        """
        ticker = data["ticker"]
        period = data["period"]
        
        # In a real implementation, fetch from data provider
        # For this example, generate mock data
        raw_data = self._generate_mock_price_data(ticker, period)
        
        data["raw_data"] = raw_data
        return data
    
    def _generate_mock_price_data(self, ticker: str, period: str) -> pd.DataFrame:
        """
        Generate mock price data for demonstration.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (e.g., "1y", "6mo", etc.)
            
        Returns:
            DataFrame with mock price data
        """
        # Determine number of days based on period
        days_map = {
            "1d": 1,
            "5d": 5,
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
            "2y": 365*2,
            "5y": 365*5,
            "max": 365*10
        }
        days = days_map.get(period, 365)
        
        # Generate dates
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days)]
        dates.reverse()  # Oldest to newest
        
        # Filter for business days (rough approximation)
        dates = [date for date in dates if date.weekday() < 5]
        
        # Generate a starting price (use ticker's first char ascii value for variety)
        base_price = ord(ticker[0].upper()) * 2 + 50
        
        # Add some randomness
        np.random.seed(sum(ord(c) for c in ticker))
        
        # Generate price data with a trend based on ticker
        trend = 0.0002 * (ord(ticker[0].upper()) % 10 - 5)  # -0.001 to 0.001
        volatility = 0.01 + 0.01 * (ord(ticker[0].lower()) % 5)  # 0.01 to 0.05
        
        prices = [base_price]
        for i in range(1, len(dates)):
            # Random walk with drift
            change = trend + np.random.normal(0, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # Generate OHLCV data
        df = pd.DataFrame()
        df["date"] = dates
        df["ticker"] = ticker
        df["close"] = prices
        
        # Open is previous day's close with some noise
        df["open"] = df["close"].shift(1) * (1 + np.random.normal(0, 0.002, size=len(df)))
        df.loc[0, "open"] = df.loc[0, "close"] * (1 - 0.002)  # First day
        
        # High is max of open/close plus some noise
        df["high"] = df[["open", "close"]].max(axis=1) * (1 + np.abs(np.random.normal(0, 0.005, size=len(df))))
        
        # Low is min of open/close minus some noise
        df["low"] = df[["open", "close"]].min(axis=1) * (1 - np.abs(np.random.normal(0, 0.005, size=len(df))))
        
        # Volume varies with price volatility
        price_changes = np.abs(df["close"].pct_change())
        df["volume"] = np.random.randint(100000, 1000000, size=len(df)) * (1 + 5 * price_changes)
        df["volume"] = df["volume"].fillna(df["volume"].mean()).astype(int)
        
        # Adjusted close same as close for this example
        df["adjusted_close"] = df["close"]
        
        return df


class DataCleanStage(PipelineStage):
    """Pipeline stage for cleaning and preprocessing data."""
    
    async def process(
        self, data: Dict[str, Any], pipeline: 'DataPipeline'
    ) -> Dict[str, Any]:
        """
        Clean and preprocess raw stock data.
        
        Args:
            data: Pipeline data
            pipeline: Pipeline instance
            
        Returns:
            Updated pipeline data with cleaned data
        """
        raw_data = data.get("raw_data")
        if raw_data is None:
            return data
        
        df = raw_data.copy()
        
        # Ensure date column is datetime
        df["date"] = pd.to_datetime(df["date"])
        
        # Sort by date
        df = df.sort_values("date")
        
        # Remove duplicates
        df = df.drop_duplicates(subset=["date"], keep="last")
        
        # Fill missing values
        for col in ["open", "high", "low", "close", "adjusted_close"]:
            if col in df.columns:
                # Forward fill, then backward fill
                df[col] = df[col].fillna(method="ffill").fillna(method="bfill")
        
        # Fill missing volume with zeros
        if "volume" in df.columns:
            df["volume"] = df["volume"].fillna(0).astype(int)
        
        # Add day of week
        df["day_of_week"] = df["date"].dt.dayofweek
        
        # Add is_month_end
        df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
        
        # Store cleaned data
        data["processed_data"] = df
        
        return data


class FeatureEngineeringStage(PipelineStage):
    """Pipeline stage for feature engineering."""
    
    async def process(
        self, data: Dict[str, Any], pipeline: 'DataPipeline'
    ) -> Dict[str, Any]:
        """
        Add engineered features to stock data.
        
        Args:
            data: Pipeline data
            pipeline: Pipeline instance
            
        Returns:
            Updated pipeline data with features
        """
        df = data.get("processed_data")
        if df is None:
            return data
        
        # Calculate various technical indicators
        
        # Price Features
        # Returns
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
        
        # Moving Averages
        df["ma5"] = df["close"].rolling(window=5).mean()
        df["ma10"] = df["close"].rolling(window=10).mean()
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["ma50"] = df["close"].rolling(window=50).mean()
        df["ma200"] = df["close"].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
        
        # MACD (Moving Average Convergence Divergence)
        df["macd"] = df["ema12"] - df["ema26"]
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]
        
        # Bollinger Bands
        df["bb_middle"] = df["close"].rolling(window=20).mean()
        stddev = df["close"].rolling(window=20).std()
        df["bb_upper"] = df["bb_middle"] + 2 * stddev
        df["bb_lower"] = df["bb_middle"] - 2 * stddev
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        df["bb_pct"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
        
        # Momentum Indicators
        # Relative Strength Index (RSI)
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        # Stochastic Oscillator
        n = 14
        df["stoch_k"] = 100 * ((df["close"] - df["low"].rolling(window=n).min()) / 
                              (df["high"].rolling(window=n).max() - df["low"].rolling(window=n).min()))
        df["stoch_d"] = df["stoch_k"].rolling(window=3).mean()
        
        # Volume Indicators
        # On-Balance Volume (OBV)
        df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()
        
        # Volume Moving Average
        df["volume_ma20"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_ma20"]
        
        # Volatility Indicators
        # Average True Range (ATR)
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df["atr"] = true_range.rolling(window=14).mean()
        df["atr_pct"] = df["atr"] / df["close"]
        
        # Historical Volatility
        df["volatility"] = df["log_returns"].rolling(window=20).std() * np.sqrt(252)
        
        # Trend Indicators
        # Average Directional Index (ADX)
        plus_dm = df["high"].diff()
        minus_dm = -df["low"].diff()
        plus_dm[plus_dm < minus_dm] = 0
        minus_dm[minus_dm < plus_dm] = 0
        
        tr = true_range
        plus_di = 100 * plus_dm.rolling(window=14).mean() / tr.rolling(window=14).mean()
        minus_di = 100 * minus_dm.rolling(window=14).mean() / tr.rolling(window=14).mean()
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df["adx"] = dx.rolling(window=14).mean()
        
        # Price Relative to Moving Averages
        df["price_to_ma50"] = df["close"] / df["ma50"]
        df["price_to_ma200"] = df["close"] / df["ma200"]
        
        # Golden Cross / Death Cross
        df["ma_cross"] = np.where(df["ma50"] > df["ma200"], 1, -1)
        
        # Fill NaN values
        df = df.fillna(0)
        
        # Store processed data with features
        data["processed_data"] = df
        
        # Store feature metadata
        data["features"] = {
            "trend_features": ["ma_cross", "price_to_ma50", "price_to_ma200", "adx"],
            "momentum_features": ["rsi", "stoch_k", "stoch_d", "macd"],
            "volatility_features": ["atr", "volatility", "bb_width"],
            "volume_features": ["obv", "volume_ratio"],
            "total_features": len(df.columns) - 7  # Excluding date, ticker, OHLCV
        }
        
        return data


class PredictabilityAnalysisStage(PipelineStage):
    """Pipeline stage for analyzing stock predictability."""
    
    async def process(
        self, data: Dict[str, Any], pipeline: 'DataPipeline'
    ) -> Dict[str, Any]:
        """
        Analyze stock predictability based on technical patterns.
        
        Args:
            data: Pipeline data
            pipeline: Pipeline instance
            
        Returns:
            Updated pipeline data with predictability metrics
        """
        df = data.get("processed_data")
        if df is None or len(df) < 60:
            return data
        
        # Use recent data for analysis (last 60 days)
        recent_df = df.tail(60)
        
        # Calculate predictability metrics
        
        # 1. Trend strength
        trend_metrics = {}
        
        # ADX strength (>25 indicates strong trend)
        adx_mean = recent_df["adx"].mean() if "adx" in recent_df.columns else 15
        adx_score = min(100, adx_mean * 4)  # Scale to 0-100
        trend_metrics["adx_score"] = adx_score
        
        # Moving average alignment
        ma_alignment = 0
        if "ma5" in recent_df.columns and "ma20" in recent_df.columns:
            ma_alignment = (recent_df["ma5"] > recent_df["ma20"]).mean() * 100
            if ma_alignment < 50:
                ma_alignment = 100 - ma_alignment  # Consistent bearish trend is still predictable
        trend_metrics["ma_alignment"] = ma_alignment
        
        # Linear trend R² coefficient
        try:
            from sklearn.linear_model import LinearRegression
            X = np.arange(len(recent_df)).reshape(-1, 1)
            y = recent_df["close"].values
            model = LinearRegression().fit(X, y)
            r2 = model.score(X, y) * 100
            trend_metrics["r2_score"] = r2
        except ImportError:
            trend_metrics["r2_score"] = 60  # Default if sklearn not available
        
        # Overall trend score
        trend_score = (
            0.4 * trend_metrics["adx_score"] +
            0.3 * trend_metrics["ma_alignment"] +
            0.3 * trend_metrics["r2_score"]
        )
        
        # 2. Volatility metrics
        volatility_metrics = {}
        
        # Realized volatility
        volatility = recent_df["volatility"].mean() if "volatility" in recent_df.columns else 0.2
        # Lower volatility is more predictable (inverse relationship)
        volatility_score = max(0, 100 - volatility * 100)
        volatility_metrics["volatility_score"] = volatility_score
        
        # Bollinger Band width
        if "bb_width" in recent_df.columns:
            bb_width = recent_df["bb_width"].mean()
            # Lower BB width is more predictable (inverse relationship)
            bb_score = max(0, 100 - bb_width * 100)
            volatility_metrics["bb_score"] = bb_score
        else:
            volatility_metrics["bb_score"] = 60
        
        # Average True Range percentage
        if "atr_pct" in recent_df.columns:
            atr_pct = recent_df["atr_pct"].mean()
            # Lower ATR is more predictable (inverse relationship)
            atr_score = max(0, 100 - atr_pct * 2000)
            volatility_metrics["atr_score"] = atr_score
        else:
            volatility_metrics["atr_score"] = 60
        
        # Overall volatility score (higher score = lower volatility = more predictable)
        volatility_score = (
            0.4 * volatility_metrics["volatility_score"] +
            0.3 * volatility_metrics["bb_score"] +
            0.3 * volatility_metrics["atr_score"]
        )
        
        # 3. Volume consistency
        volume_metrics = {}
        
        # Volume stability (coefficient of variation)
        if "volume" in recent_df.columns:
            vol_mean = recent_df["volume"].mean()
            vol_std = recent_df["volume"].std()
            vol_cv = vol_std / vol_mean if vol_mean > 0 else 1
            # Lower CV is more predictable (inverse relationship)
            vol_consistency = max(0, 100 - vol_cv * 100)
            volume_metrics["vol_consistency"] = vol_consistency
        else:
            volume_metrics["vol_consistency"] = 60
        
        # Volume trend alignment
        if "volume" in recent_df.columns and "returns" in recent_df.columns:
            # Calculate correlation between volume and absolute returns
            vol_return_corr = recent_df["volume"].corr(recent_df["returns"].abs())
            # Higher correlation is more predictable (0-1 scale)
            vol_alignment = (vol_return_corr * 50) + 50  # Scale to 0-100
            volume_metrics["vol_alignment"] = vol_alignment
        else:
            volume_metrics["vol_alignment"] = 60
        
        # Overall volume score
        volume_score = (
            0.6 * volume_metrics["vol_consistency"] +
            0.4 * volume_metrics["vol_alignment"]
        )
        
        # 4. Pattern predictability
        pattern_metrics = {}
        
        # RSI stability
        if "rsi" in recent_df.columns:
            rsi_range = recent_df["rsi"].max() - recent_df["rsi"].min()
            # Lower range indicates less predictability (inverse relationship)
            rsi_stability = max(0, 100 - rsi_range)
            pattern_metrics["rsi_stability"] = rsi_stability
        else:
            pattern_metrics["rsi_stability"] = 60
        
        # MACD signal line crossovers (fewer crossovers = more predictable trend)
        if "macd" in recent_df.columns and "macd_signal" in recent_df.columns:
            crossovers = ((recent_df["macd"] > recent_df["macd_signal"]) != 
                          (recent_df["macd"].shift(1) > recent_df["macd_signal"].shift(1))).sum()
            # Fewer crossovers is more predictable (inverse relationship)
            crossover_score = max(0, 100 - crossovers * 5)
            pattern_metrics["macd_stability"] = crossover_score
        else:
            pattern_metrics["macd_stability"] = 60
        
        # Overall pattern score
        pattern_score = (
            0.5 * pattern_metrics["rsi_stability"] +
            0.5 * pattern_metrics["macd_stability"]
        )
        
        # Combine all metrics into overall predictability score
        predictability_score = int(
            0.4 * trend_score +
            0.3 * volatility_score +
            0.2 * volume_score +
            0.1 * pattern_score
        )
        
        # Store predictability metrics
        data["predictability"] = {
            "score": predictability_score,
            "category": self._get_predictability_category(predictability_score),
            "factors": {
                "trend": {
                    "score": round(trend_score),
                    "description": self._get_trend_description(trend_score),
                    "metrics": {k: round(v, 2) for k, v in trend_metrics.items()}
                },
                "volatility": {
                    "score": round(volatility_score),
                    "description": self._get_volatility_description(volatility_score),
                    "metrics": {k: round(v, 2) for k, v in volatility_metrics.items()}
                },
                "volume": {
                    "score": round(volume_score),
                    "description": self._get_volume_description(volume_score),
                    "metrics": {k: round(v, 2) for k, v in volume_metrics.items()}
                },
                "pattern": {
                    "score": round(pattern_score),
                    "description": self._get_pattern_description(pattern_score),
                    "metrics": {k: round(v, 2) for k, v in pattern_metrics.items()}
                }
            }
        }
        
        return data
    
    def _get_predictability_category(self, score: int) -> str:
        """Convert predictability score to category."""
        if score >= 85:
            return "Very High"
        elif score >= 70:
            return "High"
        elif score >= 50:
            return "Medium"
        elif score >= 30:
            return "Low"
        else:
            return "Very Low"
    
    def _get_trend_description(self, score: float) -> str:
        """Generate description for trend score."""
        if score >= 85:
            return "Strong and consistent directional trend"
        elif score >= 70:
            return "Clear trend with occasional reversals"
        elif score >= 50:
            return "Moderate trending behavior"
        elif score >= 30:
            return "Weak trends with frequent direction changes"
        else:
            return "No discernible trend pattern"
    
    def _get_volatility_description(self, score: float) -> str:
        """Generate description for volatility score."""
        if score >= 85:
            return "Very stable price movements making forecasting more reliable"
        elif score >= 70:
            return "Moderate volatility creates manageable price patterns"
        elif score >= 50:
            return "Average volatility with some predictable patterns"
        elif score >= 30:
            return "High volatility makes price movements less predictable"
        else:
            return "Extreme volatility makes forecasting very challenging"
    
    def _get_volume_description(self, score: float) -> str:
        """Generate description for volume score."""
        if score >= 85:
            return "High and consistent trading volume creates reliable signals"
        elif score >= 70:
            return "Good trading volume with clear patterns"
        elif score >= 50:
            return "Adequate volume for most forecasting methods"
        elif score >= 30:
            return "Low volume may reduce forecast reliability"
        else:
            return "Very thin trading makes forecasting difficult"
    
    def _get_pattern_description(self, score: float) -> str:
        """Generate description for pattern score."""
        if score >= 85:
            return "Strong recurring patterns provide excellent forecast basis"
        elif score >= 70:
            return "Recognizable patterns appear frequently in price data"
        elif score >= 50:
            return "Some technical patterns visible but not always reliable"
        elif score >= 30:
            return "Few discernible patterns in technical indicators"
        else:
            return "Chaotic price action with minimal pattern formation"
