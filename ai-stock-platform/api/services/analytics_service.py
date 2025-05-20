"""
Analytics Service
Created: 2025-05-20 05:05:14
Author: daparthi001
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy import stats

from core.exceptions import ResourceNotFoundError, ValidationError
from api.utils.market_data import MarketDataClient
from api.utils.time_series import TimeSeriesAnalyzer
from api.utils.statistical import StatisticalAnalyzer
from api.utils.ml_models import PredictiveModels
from api.utils.sentiment import SentimentAnalyzer

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data = MarketDataClient()
        self.time_series = TimeSeriesAnalyzer()
        self.stats = StatisticalAnalyzer()
        self.ml_models = PredictiveModels()
        self.sentiment = SentimentAnalyzer()

    async def get_portfolio_analytics(
        self,
        portfolio_id: int,
        metrics: List[str],
        time_range: str,
        user_id: int
    ) -> Dict[str, Any]:
        """Calculate portfolio analytics."""
        # Get portfolio data
        portfolio = await self._get_portfolio_data(portfolio_id, user_id)
        if not portfolio:
            raise ResourceNotFoundError(f"Portfolio {portfolio_id} not found")

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = self._calculate_start_date(end_date, time_range)

        # Initialize results
        results = {
            "portfolio_id": portfolio_id,
            "timestamp": datetime.utcnow(),
            "time_range": time_range,
            "metrics": {},
            "benchmarks": {},
            "insights": [],
            "recommendations": []
        }

        # Calculate requested metrics
        for metric in metrics:
            if metric == "returns":
                results["metrics"]["returns"] = await self._calculate_returns(
                    portfolio, start_date, end_date
                )
            elif metric == "risk":
                results["metrics"]["risk_metrics"] = await self._calculate_risk_metrics(
                    portfolio, start_date, end_date
                )
            elif metric == "allocation":
                results["metrics"]["allocation"] = await self._calculate_allocation(
                    portfolio
                )
            elif metric == "performance":
                results["metrics"]["performance_attribution"] = await self._calculate_performance(
                    portfolio, start_date, end_date
                )

        # Add benchmarks comparison
        results["benchmarks"] = await self._compare_benchmarks(
            portfolio, start_date, end_date
        )

        # Generate insights and recommendations
        results["insights"] = await self._generate_insights(results)
        results["recommendations"] = await self._generate_recommendations(results)

        return results

    async def get_market_analytics(
        self,
        symbols: List[str],
        indicators: List[str]
    ) -> Dict[str, Any]:
        """Calculate market analytics."""
        results = {
            "timestamp": datetime.utcnow(),
            "symbols": symbols,
            "indicators": [],
            "correlations": {},
            "trends": {},
            "market_regime": {}
        }

        # Fetch market data
        market_data = await self.market_data.get_historical_data(
            symbols,
            lookback_days=30
        )

        # Calculate technical indicators
        for symbol in symbols:
            symbol_data = market_data[symbol]
            for indicator in indicators:
                indicator_value = await self._calculate_technical_indicator(
                    symbol_data,
                    indicator
                )
                results["indicators"].append({
                    "symbol": symbol,
                    "indicator": indicator,
                    "value": indicator_value["value"],
                    "signal": indicator_value["signal"],
                    "strength": indicator_value["strength"],
                    "trend": indicator_value["trend"]
                })

        # Calculate correlations
        results["correlations"] = await self._calculate_correlations(market_data)

        # Analyze market trends
        results["trends"] = await self._analyze_market_trends(market_data)

        # Determine market regime
        results["market_regime"] = await self._determine_market_regime(market_data)

        return results

    async def get_predictive_analytics(
        self,
        symbols: List[str],
        horizon: str,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Generate predictive analytics."""
        results = {
            "timestamp": datetime.utcnow(),
            "horizon": horizon,
            "confidence_level": confidence_level,
            "predictions": [],
            "model_metrics": {},
            "feature_importance": {}
        }

        # Convert horizon to days
        horizon_days = self._convert_horizon_to_days(horizon)

        # Get historical data for training
        historical_data = await self.market_data.get_historical_data(
            symbols,
            lookback_days=365
        )

        # Prepare features
        features = await self._prepare_prediction_features(historical_data)

        # Generate predictions for each symbol
        for symbol in symbols:
            prediction = await self.ml_models.generate_prediction(
                symbol,
                features[symbol],
                horizon_days,
                confidence_level
            )
            results["predictions"].append(prediction)

        # Calculate model metrics
        results["model_metrics"] = await self.ml_models.get_model_metrics()

        # Calculate feature importance
        results["feature_importance"] = await self.ml_models.get_feature_importance()

        return results

    async def _calculate_returns(
        self,
        portfolio: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate portfolio returns metrics."""
        returns = {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "daily_returns": [],
            "monthly_returns": [],
            "rolling_returns": {}
        }

        # Calculate returns using numpy for efficiency
        prices = np.array(portfolio["historical_prices"])
        daily_returns = np.diff(prices) / prices[:-1]

        returns["total_return"] = float(np.prod(1 + daily_returns) - 1)
        returns["annualized_return"] = float(
            (1 + returns["total_return"]) ** (365 / len(daily_returns)) - 1
        )

        # Calculate rolling returns
        window_sizes = [30, 90, 180, 365]
        for window in window_sizes:
            rolling = pd.Series(daily_returns).rolling(window=window).mean()
            returns["rolling_returns"][f"{window}d"] = rolling.iloc[-1]

        return returns

    async def _calculate_risk_metrics(
        self,
        portfolio: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate portfolio risk metrics."""
        risk_metrics = {
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "var_95": 0.0,
            "beta": 0.0
        }

        # Calculate daily returns
        prices = np.array(portfolio["historical_prices"])
        daily_returns = np.diff(prices) / prices[:-1]

        # Volatility (annualized)
        risk_metrics["volatility"] = float(np.std(daily_returns) * np.sqrt(252))

        # Sharpe Ratio (assuming risk-free rate of 0.02)
        rf_rate = 0.02
        excess_returns = daily_returns - (rf_rate / 252)
        risk_metrics["sharpe_ratio"] = float(
            np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        )

        # Sortino Ratio
        downside_returns = daily_returns[daily_returns < 0]
        risk_metrics["sortino_ratio"] = float(
            np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(252)
        )

        # Maximum Drawdown
        cumulative_returns = np.cumprod(1 + daily_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        risk_metrics["max_drawdown"] = float(np.min(drawdowns))

        # Value at Risk (95% confidence)
        risk_metrics["var_95"] = float(np.percentile(daily_returns, 5))

        # Beta (relative to S&P 500)
        market_returns = await self.market_data.get_market_returns(start_date, end_date)
        covariance = np.cov(daily_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        risk_metrics["beta"] = float(covariance / market_variance)

        return risk_metrics

    def _convert_horizon_to_days(self, horizon: str) -> int:
        """Convert horizon string to number of days."""
        conversion = {
            "1d": 1,
            "1w": 7,
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365
        }
        return conversion.get(horizon, 30)

    def _calculate_start_date(self, end_date: datetime, time_range: str) -> datetime:
        """Calculate start date based on time range."""
        ranges = {
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "ytd": datetime(end_date.year, 1, 1) - end_date,
            "all": timedelta(days=3650)  # 10 years
        }
        return end_date - ranges.get(time_range, ranges["1m"])