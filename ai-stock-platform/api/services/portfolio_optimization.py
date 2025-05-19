"""
Portfolio Optimization Service
Created: 2025-05-19 04:44:01
Author: daparthi001
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from api.services.market_data_service import MarketDataService
from api.services.risk_management import RiskManagementService

class PortfolioOptimizer:
    def __init__(
        self,
        market_data: MarketDataService,
        risk_management: RiskManagementService
    ):
        self.market_data = market_data
        self.risk_management = risk_management
        self.risk_free_rate = 0.02  # Annual risk-free rate

    async def optimize_portfolio(
        self,
        symbols: List[str],
        objective: str = 'sharpe_ratio',
        constraints: Optional[Dict] = None,
        risk_tolerance: Optional[float] = None
    ) -> Dict:
        """
        Optimize portfolio weights based on different objectives
        """
        try:
            # Get historical data
            historical_data = await self._get_historical_data(symbols)
            returns = historical_data.pct_change().dropna()
            
            # Calculate expected returns and covariance
            expected_returns = returns.mean() * 252  # Annualized returns
            covariance_matrix = returns.cov() * 252  # Annualized covariance
            
            # Set up optimization constraints
            constraints = self._prepare_constraints(
                len(symbols),
                constraints,
                risk_tolerance
            )
            
            # Optimize based on objective
            if objective == 'sharpe_ratio':
                optimal_weights = self._maximize_sharpe_ratio(
                    expected_returns,
                    covariance_matrix,
                    constraints
                )
            elif objective == 'minimum_volatility':
                optimal_weights = self._minimize_volatility(
                    covariance_matrix,
                    constraints
                )
            elif objective == 'maximum_return':
                optimal_weights = self._maximize_return(
                    expected_returns,
                    covariance_matrix,
                    constraints
                )
            else:
                raise ValueError(f"Unsupported optimization objective: {objective}")
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(
                optimal_weights,
                expected_returns,
                covariance_matrix
            )
            
            # Get risk analysis
            risk_analysis = await self.risk_management.analyze_portfolio_risk(
                symbols,
                optimal_weights
            )
            
            return {
                'optimal_weights': {
                    symbol: weight
                    for symbol, weight in zip(symbols, optimal_weights)
                },
                'portfolio_metrics': portfolio_metrics,
                'risk_analysis': risk_analysis,
                'efficient_frontier': await self._generate_efficient_frontier(
                    expected_returns,
                    covariance_matrix,
                    constraints
                )
            }
        except Exception as e:
            raise ValueError(f"Portfolio optimization failed: {str(e)}")

    def _maximize_sharpe_ratio(
        self,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        constraints: List[Dict]
    ) -> np.ndarray:
        """
        Maximize portfolio Sharpe ratio
        """
        n_assets = len(expected_returns)
        args = (expected_returns, covariance_matrix, self.risk_free_rate)
        
        def objective(weights):
            return -self._calculate_sharpe_ratio(weights, *args)
        
        result = minimize(
            objective,
            x0=np.ones(n_assets) / n_assets,  # Equal weights initial guess
            method='SLSQP',
            constraints=constraints,
            bounds=[(0, 1) for _ in range(n_assets)]
        )
        
        if not result.success:
            raise ValueError("Optimization failed to converge")
        
        return result.x

    def _minimize_volatility(
        self,
        covariance_matrix: pd.DataFrame,
        constraints: List[Dict]
    ) -> np.ndarray:
        """
        Minimize portfolio volatility
        """
        n_assets = len(covariance_matrix)
        
        def objective(weights):
            return np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        
        result = minimize(
            objective,
            x0=np.ones(n_assets) / n_assets,
            method='SLSQP',
            constraints=constraints,
            bounds=[(0, 1) for _ in range(n_assets)]
        )
        
        if not result.success:
            raise ValueError("Optimization failed to converge")
        
        return result.x

    def _maximize_return(
        self,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        constraints: List[Dict]
    ) -> np.ndarray:
        """
        Maximize portfolio expected return subject to risk constraints
        """
        n_assets = len(expected_returns)
        
        def objective(weights):
            return -np.dot(weights, expected_returns)
        
        result = minimize(
            objective,
            x0=np.ones(n_assets) / n_assets,
            method='SLSQP',
            constraints=constraints,
            bounds=[(0, 1) for _ in range(n_assets)]
        )
        
        if not result.success:
            raise ValueError("Optimization failed to converge")
        
        return result.x

    async def _generate_efficient_frontier(
        self,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame,
        constraints: List[Dict],
        points: int = 50
    ) -> List[Dict]:
        """
        Generate efficient frontier points
        """
        min_vol_weights = self._minimize_volatility(covariance_matrix, constraints)
        max_ret_weights = self._maximize_return(
            expected_returns,
            covariance_matrix,
            constraints
        )
        
        min_ret = np.dot(min_vol_weights, expected_returns)
        max_ret = np.dot(max_ret_weights, expected_returns)
        target_returns = np.linspace(min_ret, max_ret, points)
        
        efficient_frontier = []
        for target_return in target_returns:
            weights = await self._optimize_for_target_return(
                target_return,
                expected_returns,
                covariance_matrix,
                constraints
            )
            metrics = self._calculate_portfolio_metrics(
                weights,
                expected_returns,
                covariance_matrix
            )
            efficient_frontier.append({
                'return': metrics['expected_return'],
                'volatility': metrics['volatility'],
                'sharpe_ratio': metrics['sharpe_ratio']
            })
        
        return efficient_frontier

    def _calculate_portfolio_metrics(
        self,
        weights: np.ndarray,
        expected_returns: pd.Series,
        covariance_matrix: pd.DataFrame
    ) -> Dict:
        """
        Calculate portfolio performance metrics
        """
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(covariance_matrix, weights))
        )
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'expected_return': float(portfolio_return),
            'volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'diversification_ratio': float(
                self._calculate_diversification_ratio(weights, covariance_matrix)
            )
        }

    @staticmethod
    def _calculate_diversification_ratio(
        weights: np.ndarray,
        covariance_matrix: pd.DataFrame
    ) -> float:
        """
        Calculate portfolio diversification ratio
        """
        weighted_volatilities = np.sqrt(np.diag(covariance_matrix)) * weights
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(covariance_matrix, weights))
        )
        return np.sum(weighted_volatilities) / portfolio_volatility

    def _prepare_constraints(
        self,
        n_assets: int,
        constraints: Optional[Dict],
        risk_tolerance: Optional[float]
    ) -> List[Dict]:
        """
        Prepare optimization constraints
        """
        base_constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        
        if constraints:
            if 'min_weight' in constraints:
                base_constraints.append({
                    'type': 'ineq',
                    'fun': lambda x: x - constraints['min_weight']
                })
            if 'max_weight' in constraints:
                base_constraints.append({
                    'type': 'ineq',
                    'fun': lambda x: constraints['max_weight'] - x
                })
        
        if risk_tolerance:
            base_constraints.append({
                'type': 'ineq',
                'fun': lambda x: risk_tolerance - np.sqrt(
                    np.dot(x.T, np.dot(self.covariance_matrix, x))
                )
            })
        
        return base_constraints