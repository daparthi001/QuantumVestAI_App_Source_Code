"""
Portfolio Analytics Service
Created: 2025-05-19 04:33:12
Author: daparthi001
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from api.models.portfolio import Position, Transaction
from api.services.market_data_service import MarketDataService

class PortfolioAnalytics:
    def __init__(self, db: Session, market_data: MarketDataService):
        self.db = db
        self.market_data = market_data

    async def calculate_portfolio_metrics(self, user_id: int) -> Dict:
        """Calculate key portfolio metrics including risk and returns"""
        try:
            positions = await self._get_positions_with_history(user_id)
            if not positions:
                return self._get_empty_metrics()

            portfolio_value = sum(p['market_value'] for p in positions)
            weights = [p['market_value'] / portfolio_value for p in positions]
            
            # Calculate returns
            daily_returns = self._calculate_daily_returns(positions)
            portfolio_return = self._calculate_portfolio_return(positions)
            
            # Calculate risk metrics
            volatility = np.std(daily_returns) * np.sqrt(252)  # Annualized volatility
            sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
            beta = await self._calculate_portfolio_beta(positions, weights)
            
            # Calculate diversification metrics
            correlation_matrix = self._calculate_correlation_matrix(positions)
            diversification_score = self._calculate_diversification_score(correlation_matrix, weights)

            return {
                'performance_metrics': {
                    'total_return': portfolio_return,
                    'annualized_return': self._annualize_return(portfolio_return),
                    'daily_returns': daily_returns.tolist(),
                    'monthly_returns': self._calculate_monthly_returns(daily_returns).tolist()
                },
                'risk_metrics': {
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'beta': beta,
                    'max_drawdown': self._calculate_max_drawdown(daily_returns),
                    'var_95': self._calculate_value_at_risk(daily_returns, 0.95)
                },
                'diversification_metrics': {
                    'diversification_score': diversification_score,
                    'sector_weights': self._calculate_sector_weights(positions),
                    'correlation_matrix': correlation_matrix.tolist()
                }
            }
        except Exception as e:
            raise ValueError(f"Failed to calculate portfolio metrics: {str(e)}")

    async def generate_performance_report(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict:
        """Generate detailed performance report for a specified time period"""
        try:
            positions = await self._get_positions_with_history(user_id, start_date, end_date)
            transactions = self._get_transactions(user_id, start_date, end_date)
            
            daily_values = self._calculate_daily_portfolio_values(positions, start_date, end_date)
            benchmark_returns = await self._get_benchmark_returns(start_date, end_date)
            
            return {
                'summary': {
                    'start_value': daily_values[0],
                    'end_value': daily_values[-1],
                    'total_return': (daily_values[-1] / daily_values[0] - 1) * 100,
                    'total_contributions': sum(t.total_amount for t in transactions if t.transaction_type == 'BUY'),
                    'total_withdrawals': sum(t.total_amount for t in transactions if t.transaction_type == 'SELL')
                },
                'periodic_returns': {
                    'daily': self._calculate_periodic_returns(daily_values, 'D'),
                    'weekly': self._calculate_periodic_returns(daily_values, 'W'),
                    'monthly': self._calculate_periodic_returns(daily_values, 'M')
                },
                'benchmark_comparison': {
                    'portfolio_returns': (daily_values[-1] / daily_values[0] - 1) * 100,
                    'benchmark_returns': benchmark_returns,
                    'alpha': self._calculate_alpha(daily_values, benchmark_returns),
                    'tracking_error': self._calculate_tracking_error(daily_values, benchmark_returns)
                },
                'position_analysis': [
                    {
                        'symbol': p['symbol'],
                        'weight': p['market_value'] / sum(p['market_value'] for p in positions),
                        'return': (p['current_price'] / p['average_cost'] - 1) * 100,
                        'contribution': self._calculate_position_contribution(p, daily_values[-1])
                    }
                    for p in positions
                ]
            }
        except Exception as e:
            raise ValueError(f"Failed to generate performance report: {str(e)}")

    async def calculate_position_metrics(self, user_id: int, symbol: str) -> Dict:
        """Calculate detailed metrics for a specific position"""
        try:
            position = await self._get_position_with_history(user_id, symbol)
            if not position:
                raise ValueError(f"Position not found for symbol: {symbol}")

            transactions = self._get_position_transactions(user_id, symbol)
            daily_returns = self._calculate_position_daily_returns(position)
            
            return {
                'summary': {
                    'symbol': symbol,
                    'shares': position['shares'],
                    'average_cost': position['average_cost'],
                    'market_value': position['market_value'],
                    'unrealized_gain_loss': position['gain_loss'],
                    'realized_gain_loss': self._calculate_realized_gains(transactions)
                },
                'risk_metrics': {
                    'volatility': np.std(daily_returns) * np.sqrt(252),
                    'beta': await self._calculate_position_beta(position),
                    'r_squared': self._calculate_r_squared(position),
                    'sharpe_ratio': self._calculate_sharpe_ratio(daily_returns)
                },
                'technical_indicators': await self._calculate_technical_indicators(symbol),
                'transaction_history': [
                    {
                        'date': t.timestamp,
                        'type': t.transaction_type,
                        'shares': t.shares,
                        'price': t.price,
                        'total': t.total_amount
                    }
                    for t in transactions
                ]
            }
        except Exception as e:
            raise ValueError(f"Failed to calculate position metrics: {str(e)}")

    def _calculate_daily_returns(self, positions: List[Dict]) -> np.ndarray:
        """Calculate daily returns for the portfolio"""
        daily_values = self._calculate_daily_portfolio_values(positions)
        return np.diff(daily_values) / daily_values[:-1]

    def _calculate_sharpe_ratio(self, daily_returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate the Sharpe ratio"""
        excess_returns = daily_returns - risk_free_rate/252
        return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)

    async def _calculate_portfolio_beta(self, positions: List[Dict], weights: List[float]) -> float:
        """Calculate portfolio beta against market benchmark"""
        betas = []
        for position in positions:
            position_beta = await self._calculate_position_beta(position)
            betas.append(position_beta)
        return np.sum(np.array(betas) * np.array(weights))

    def _calculate_diversification_score(self, correlation_matrix: np.ndarray, weights: List[float]) -> float:
        """Calculate portfolio diversification score"""
        weighted_corr = correlation_matrix * np.outer(weights, weights)
        return 1 - np.sum(weighted_corr) / (np.sum(weights) ** 2)

    def _calculate_value_at_risk(self, daily_returns: np.ndarray, confidence_level: float) -> float:
        """Calculate Value at Risk at specified confidence level"""
        return np.percentile(daily_returns, (1 - confidence_level) * 100)

    def _calculate_max_drawdown(self, daily_returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        cumulative_returns = np.cumprod(1 + daily_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = cumulative_returns / running_max - 1
        return np.min(drawdowns)

    async def _get_benchmark_returns(self, start_date: datetime, end_date: datetime) -> np.ndarray:
        """Get benchmark (S&P 500) returns for comparison"""
        benchmark_data = await self.market_data.get_index_data('SPY', start_date, end_date)
        return np.diff(benchmark_data) / benchmark_data[:-1]

    def _calculate_alpha(self, portfolio_values: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """Calculate portfolio alpha"""
        portfolio_returns = np.diff(portfolio_values) / portfolio_values[:-1]
        beta = np.cov(portfolio_returns, benchmark_returns)[0,1] / np.var(benchmark_returns)
        return np.mean(portfolio_returns) - beta * np.mean(benchmark_returns)

    async def _calculate_technical_indicators(self, symbol: str) -> Dict:
        """Calculate technical indicators for a position"""
        prices = await self.market_data.get_historical_prices(symbol)
        return {
            'sma_50': self._calculate_sma(prices, 50),
            'sma_200': self._calculate_sma(prices, 200),
            'rsi': self._calculate_rsi(prices),
            'macd': self._calculate_macd(prices)
        }

    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'performance_metrics': {
                'total_return': 0,
                'annualized_return': 0,
                'daily_returns': [],
                'monthly_returns': []
            },
            'risk_metrics': {
                'volatility': 0,
                'sharpe_ratio': 0,
                'beta': 0,
                'max_drawdown': 0,
                'var_95': 0
            },
            'diversification_metrics': {
                'diversification_score': 0,
                'sector_weights': {},
                'correlation_matrix': [[]]
            }
        }