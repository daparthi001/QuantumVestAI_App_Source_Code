"""
Risk Management Service
Created: 2025-05-19 04:45:08
Author: daparthi001
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from api.services.market_data_service import MarketDataService

class RiskManagementService:
    def __init__(self, market_data: MarketDataService):
        self.market_data = market_data
        self.confidence_level = 0.95
        self.lookback_period = 252  # One trading year

    async def analyze_portfolio_risk(
        self,
        symbols: List[str],
        weights: List[float],
        custom_metrics: Optional[List[str]] = None
    ) -> Dict:
        """
        Comprehensive portfolio risk analysis
        """
        try:
            # Get historical data
            historical_data = await self._get_historical_data(symbols)
            returns = historical_data.pct_change().dropna()
            
            # Calculate basic risk metrics
            risk_metrics = {
                'value_at_risk': self._calculate_var(returns, weights),
                'conditional_var': self._calculate_cvar(returns, weights),
                'volatility': self._calculate_volatility(returns, weights),
                'downside_risk': self._calculate_downside_risk(returns, weights),
                'tail_risk': self._calculate_tail_risk(returns, weights)
            }
            
            # Calculate stress test scenarios
            stress_tests = await self._run_stress_tests(symbols, weights)
            
            # Calculate correlation matrix
            correlation_matrix = returns.corr().to_dict()
            
            # Get sector exposure
            sector_exposure = await self._calculate_sector_exposure(symbols, weights)
            
            # Calculate liquidity risk
            liquidity_risk = await self._analyze_liquidity_risk(symbols, weights)
            
            # Calculate factor exposures
            factor_exposure = await self._calculate_factor_exposure(symbols, weights)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'risk_metrics': risk_metrics,
                'stress_tests': stress_tests,
                'correlation_matrix': correlation_matrix,
                'sector_exposure': sector_exposure,
                'liquidity_risk': liquidity_risk,
                'factor_exposure': factor_exposure,
                'risk_decomposition': self._calculate_risk_decomposition(
                    returns,
                    weights
                ),
                'concentration_risk': self._calculate_concentration_risk(weights)
            }
        except Exception as e:
            raise ValueError(f"Risk analysis failed: {str(e)}")

    def _calculate_var(
        self,
        returns: pd.DataFrame,
        weights: List[float],
        method: str = 'historical'
    ) -> Dict:
        """
        Calculate Value at Risk using different methods
        """
        portfolio_returns = np.dot(returns, weights)
        
        if method == 'historical':
            var = np.percentile(portfolio_returns, (1 - self.confidence_level) * 100)
        elif method == 'parametric':
            var = -(np.mean(portfolio_returns) + 
                   np.std(portfolio_returns) * 
                   self._get_z_score(self.confidence_level))
        elif method == 'monte_carlo':
            var = self._monte_carlo_var(returns, weights)
        else:
            raise ValueError(f"Unsupported VaR method: {method}")
            
        return {
            'value': float(var),
            'method': method,
            'confidence_level': self.confidence_level,
            'holding_period': '1d'
        }

    def _calculate_cvar(
        self,
        returns: pd.DataFrame,
        weights: List[float]
    ) -> Dict:
        """
        Calculate Conditional Value at Risk (Expected Shortfall)
        """
        portfolio_returns = np.dot(returns, weights)
        var = self._calculate_var(returns, weights)['value']
        cvar = -np.mean(portfolio_returns[portfolio_returns <= -var])
        
        return {
            'value': float(cvar),
            'confidence_level': self.confidence_level,
            'holding_period': '1d'
        }

    async def _run_stress_tests(
        self,
        symbols: List[str],
        weights: List[float]
    ) -> Dict:
        """
        Run various stress test scenarios
        """
        scenarios = {
            'market_crash': {'market': -0.20, 'volatility': 2.0},
            'recession': {'market': -0.30, 'rates': 0.02},
            'recovery': {'market': 0.15, 'rates': -0.01},
            'inflation': {'market': -0.05, 'rates': 0.03},
            'deflation': {'market': -0.10, 'rates': -0.02}
        }
        
        results = {}
        for scenario, shocks in scenarios.items():
            impact = await self._calculate_scenario_impact(
                symbols,
                weights,
                shocks
            )
            results[scenario] = {
                'portfolio_impact': float(impact),
                'shocks': shocks
            }
            
        return results

    async def _analyze_liquidity_risk(
        self,
        symbols: List[str],
        weights: List[float]
    ) -> Dict:
        """
        Analyze portfolio liquidity risk
        """
        liquidity_metrics = {}
        total_portfolio_value = 1000000  # Assume $1M portfolio for calculation
        
        for symbol, weight in zip(symbols, weights):
            position_value = total_portfolio_value * weight
            volume_data = await self.market_data.get_average_daily_volume(symbol)
            
            days_to_liquidate = position_value / (volume_data['average_volume'] * 
                                                volume_data['average_price'] * 0.1)
            
            liquidity_metrics[symbol] = {
                'days_to_liquidate': float(days_to_liquidate),
                'average_daily_volume': float(volume_data['average_volume']),
                'volume_participation': float(position_value / 
                    (volume_data['average_volume'] * volume_data['average_price']))
            }
            
        return {
            'position_liquidity': liquidity_metrics,
            'portfolio_liquidity_score': self._calculate_liquidity_score(
                liquidity_metrics
            )
        }

    async def _calculate_factor_exposure(
        self,
        symbols: List[str],
        weights: List[float]
    ) -> Dict:
        """
        Calculate exposure to various risk factors
        """
        factors = ['market', 'size', 'value', 'momentum', 'quality']
        exposures = {}
        
        for factor in factors:
            factor_data = await self._get_factor_data(symbols, factor)
            exposure = np.dot(weights, factor_data)
            exposures[factor] = float(exposure)
            
        return {
            'factor_exposures': exposures,
            'total_factor_risk': self._calculate_total_factor_risk(exposures)
        }

    def _calculate_risk_decomposition(
        self,
        returns: pd.DataFrame,
        weights: List[float]
    ) -> Dict:
        """
        Calculate risk decomposition using principal components
        """
        cov_matrix = returns.cov()
        total_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Calculate marginal contribution to risk
        mcr = np.dot(cov_matrix, weights) * weights / total_risk
        
        return {
            'total_risk': float(total_risk),
            'risk_contribution': {
                symbol: float(contrib)
                for symbol, contrib in zip(returns.columns, mcr)
            },
            'diversification_ratio': float(
                np.sum(np.sqrt(np.diag(cov_matrix)) * weights) / total_risk
            )
        }

    def _calculate_concentration_risk(self, weights: List[float]) -> Dict:
        """
        Calculate portfolio concentration metrics
        """
        # Herfindahl-Hirschman Index
        hhi = np.sum(np.square(weights))
        
        # Gini coefficient
        gini = self._calculate_gini_coefficient(weights)
        
        return {
            'hhi': float(hhi),
            'gini': float(gini),
            'concentration_threshold': 0.20,  # 20% threshold for concentration
            'high_concentration_positions': [
                (symbol, weight)
                for symbol, weight in zip(self.symbols, weights)
                if weight > 0.20
            ]
        }

    @staticmethod
    def _calculate_gini_coefficient(weights: List[float]) -> float:
        """
        Calculate Gini coefficient for portfolio concentration
        """
        weights = np.array(weights)
        weights = np.sort(weights)
        n = len(weights)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * weights) / (n * np.sum(weights))) - (n + 1) / n

    def _monte_carlo_var(
        self,
        returns: pd.DataFrame,
        weights: List[float],
        n_simulations: int = 10000
    ) -> float:
        """
        Calculate VaR using Monte Carlo simulation
        """
        # Implementation of Monte Carlo VaR calculation
        pass

    async def monitor_risk_limits(
        self,
        portfolio_id: str,
        risk_limits: Dict
    ) -> Dict:
        """
        Monitor portfolio risk limits in real-time
        """
        current_risk = await self.analyze_portfolio_risk(
            self.symbols,
            self.weights
        )
        
        violations = []
        for metric, limit in risk_limits.items():
            if current_risk['risk_metrics'].get(metric) > limit:
                violations.append({
                    'metric': metric,
                    'current_value': current_risk['risk_metrics'][metric],
                    'limit': limit
                })
                
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'portfolio_id': portfolio_id,
            'status': 'breach' if violations else 'normal',
            'violations': violations,
            'current_risk_levels': current_risk['risk_metrics']
        }