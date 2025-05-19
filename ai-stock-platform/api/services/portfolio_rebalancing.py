"""
Portfolio Rebalancing Service
Created: 2025-05-19 04:36:33
Author: daparthi001
"""
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.portfolio import Position
from api.services.market_data_service import MarketDataService
from api.services.portfolio_analytics import PortfolioAnalytics

class PortfolioRebalancer:
    def __init__(
        self,
        db: Session,
        market_data: MarketDataService,
        analytics: PortfolioAnalytics
    ):
        self.db = db
        self.market_data = market_data
        self.analytics = analytics

    async def analyze_portfolio_balance(
        self, 
        user_id: int,
        target_allocation: Dict[str, float]
    ) -> Dict:
        """Analyze current portfolio balance against target allocation"""
        try:
            positions = await self._get_current_positions(user_id)
            total_value = sum(p['market_value'] for p in positions)
            
            current_allocation = {
                p['symbol']: p['market_value'] / total_value
                for p in positions
            }

            deviations = {
                symbol: {
                    'current': current_allocation.get(symbol, 0) * 100,
                    'target': target_allocation.get(symbol, 0) * 100,
                    'deviation': (current_allocation.get(symbol, 0) - 
                                target_allocation.get(symbol, 0)) * 100
                }
                for symbol in set(list(current_allocation.keys()) + 
                                list(target_allocation.keys()))
            }

            return {
                'analysis': {
                    'total_value': total_value,
                    'current_allocation': current_allocation,
                    'target_allocation': target_allocation,
                    'deviations': deviations
                },
                'rebalancing_needed': any(
                    abs(dev['deviation']) > 5 for dev in deviations.values()
                ),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ValueError(f"Failed to analyze portfolio balance: {str(e)}")

    async def generate_rebalancing_plan(
        self,
        user_id: int,
        target_allocation: Dict[str, float],
        cash_injection: float = 0,
        tolerance: float = 0.05
    ) -> Dict:
        """Generate a rebalancing plan to achieve target allocation"""
        try:
            current_state = await self.analyze_portfolio_balance(
                user_id,
                target_allocation
            )
            
            total_value = current_state['analysis']['total_value'] + cash_injection
            trades = []
            
            # Calculate required trades
            for symbol, target in target_allocation.items():
                current_value = (current_state['analysis']['current_allocation']
                               .get(symbol, 0) * total_value)
                target_value = target * total_value
                difference = target_value - current_value
                
                if abs(difference) > tolerance * target_value:
                    current_price = await self.market_data.get_current_price(symbol)
                    shares = round(difference / current_price, 2)
                    
                    trades.append({
                        'symbol': symbol,
                        'action': 'BUY' if shares > 0 else 'SELL',
                        'shares': abs(shares),
                        'estimated_cost': abs(difference),
                        'current_price': current_price
                    })

            return {
                'rebalancing_plan': {
                    'trades': trades,
                    'estimated_total_cost': sum(
                        t['estimated_cost'] for t in trades 
                        if t['action'] == 'BUY'
                    ),
                    'estimated_total_proceeds': sum(
                        t['estimated_cost'] for t in trades 
                        if t['action'] == 'SELL'
                    )
                },
                'post_rebalance_projection': await self._project_post_rebalance_state(
                    current_state['analysis'],
                    trades
                ),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ValueError(f"Failed to generate rebalancing plan: {str(e)}")

    async def execute_rebalancing_plan(
        self,
        user_id: int,
        plan_id: str,
        dry_run: bool = True
    ) -> Dict:
        """Execute a generated rebalancing plan"""
        try:
            # Retrieve the plan
            plan = await self._get_rebalancing_plan(plan_id)
            if not plan:
                raise ValueError(f"Rebalancing plan {plan_id} not found")

            execution_results = []
            
            if not dry_run:
                # Execute trades
                for trade in plan['rebalancing_plan']['trades']:
                    try:
                        result = await self._execute_trade(
                            user_id,
                            trade['symbol'],
                            trade['action'],
                            trade['shares']
                        )
                        execution_results.append({
                            **trade,
                            'status': 'completed',
                            'executed_price': result['executed_price'],
                            'actual_cost': result['actual_cost']
                        })
                    except Exception as e:
                        execution_results.append({
                            **trade,
                            'status': 'failed',
                            'error': str(e)
                        })

            return {
                'execution_summary': {
                    'plan_id': plan_id,
                    'dry_run': dry_run,
                    'trades_executed': len([
                        r for r in execution_results 
                        if r['status'] == 'completed'
                    ]),
                    'trades_failed': len([
                        r for r in execution_results 
                        if r['status'] == 'failed'
                    ]),
                    'total_cost': sum(
                        r['actual_cost'] for r in execution_results 
                        if r['status'] == 'completed' and r['action'] == 'BUY'
                    ),
                    'total_proceeds': sum(
                        r['actual_cost'] for r in execution_results 
                        if r['status'] == 'completed' and r['action'] == 'SELL'
                    )
                },
                'trade_results': execution_results,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ValueError(f"Failed to execute rebalancing plan: {str(e)}")

    async def optimize_portfolio_weights(
        self,
        user_id: int,
        risk_tolerance: float,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """Optimize portfolio weights based on modern portfolio theory"""
        try:
            positions = await self._get_current_positions(user_id)
            returns = await self._calculate_historical_returns(positions)
            
            # Calculate expected returns and covariance matrix
            expected_returns = np.mean(returns, axis=0)
            cov_matrix = np.cov(returns.T)
            
            # Optimize portfolio weights
            optimal_weights = await self._optimize_weights(
                expected_returns,
                cov_matrix,
                risk_tolerance,
                constraints
            )
            
            return {
                'optimal_allocation': {
                    positions[i]['symbol']: weight
                    for i, weight in enumerate(optimal_weights)
                },
                'projected_metrics': {
                    'expected_return': float(np.dot(optimal_weights, expected_returns)),
                    'volatility': float(np.sqrt(
                        np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
                    )),
                    'sharpe_ratio': float(
                        np.dot(optimal_weights, expected_returns) /
                        np.sqrt(np.dot(
                            optimal_weights.T,
                            np.dot(cov_matrix, optimal_weights)
                        ))
                    )
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ValueError(f"Failed to optimize portfolio weights: {str(e)}")

    async def _get_current_positions(self, user_id: int) -> List[Dict]:
        """Get current portfolio positions with market values"""
        positions = self.db.query(Position).filter(
            Position.user_id == user_id
        ).all()
        
        result = []
        for position in positions:
            current_price = await self.market_data.get_current_price(
                position.symbol
            )
            result.append({
                'symbol': position.symbol,
                'shares': position.shares,
                'market_value': position.shares * current_price,
                'current_price': current_price
            })
        
        return result

    async def _project_post_rebalance_state(
        self,
        current_state: Dict,
        trades: List[Dict]
    ) -> Dict:
        """Project portfolio state after rebalancing"""
        projected_positions = current_state['current_allocation'].copy()
        
        for trade in trades:
            if trade['action'] == 'BUY':
                projected_positions[trade['symbol']] = (
                    projected_positions.get(trade['symbol'], 0) +
                    trade['estimated_cost']
                )
            else:
                projected_positions[trade['symbol']] = (
                    projected_positions.get(trade['symbol'], 0) -
                    trade['estimated_cost']
                )
        
        total_value = sum(projected_positions.values())
        return {
            symbol: value / total_value
            for symbol, value in projected_positions.items()
            if value > 0
        }