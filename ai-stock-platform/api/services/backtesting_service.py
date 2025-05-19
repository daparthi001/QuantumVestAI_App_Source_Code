"""
Backtesting Service
Created: 2025-05-19 04:42:55
Author: daparthi001
"""
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from api.services.market_data_service import MarketDataService
from api.services.portfolio_analytics import PortfolioAnalytics

class BacktestingService:
    def __init__(
        self,
        market_data: MarketDataService,
        portfolio_analytics: PortfolioAnalytics
    ):
        self.market_data = market_data
        self.portfolio_analytics = portfolio_analytics
        self.risk_free_rate = 0.02  # Annual risk-free rate

    async def run_strategy_backtest(
        self,
        strategy_config: Dict,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
        trading_costs: Optional[Dict] = None
    ) -> Dict:
        """
        Run a backtest for a given trading strategy
        """
        try:
            # Initialize backtest parameters
            self.trading_costs = trading_costs or {
                'commission': 0.001,  # 0.1% per trade
                'slippage': 0.0005   # 0.05% slippage
            }
            
            # Get historical data
            historical_data = await self._get_backtest_data(
                strategy_config['symbols'],
                start_date,
                end_date
            )
            
            # Run strategy simulation
            results = await self._simulate_strategy(
                strategy_config,
                historical_data,
                initial_capital
            )
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(results)
            
            return {
                'summary': {
                    'initial_capital': initial_capital,
                    'final_capital': results['portfolio_value'][-1],
                    'total_return': (results['portfolio_value'][-1] / initial_capital - 1) * 100,
                    'annualized_return': performance_metrics['annualized_return'],
                    'sharpe_ratio': performance_metrics['sharpe_ratio'],
                    'max_drawdown': performance_metrics['max_drawdown'],
                    'win_rate': performance_metrics['win_rate']
                },
                'trades': results['trades'],
                'metrics': performance_metrics,
                'equity_curve': results['portfolio_value'],
                'positions': results['positions'],
                'timestamps': results['timestamps']
            }
        except Exception as e:
            raise ValueError(f"Backtest execution failed: {str(e)}")

    async def _simulate_strategy(
        self,
        strategy_config: Dict,
        historical_data: pd.DataFrame,
        initial_capital: float
    ) -> Dict:
        """
        Simulate trading strategy execution
        """
        portfolio = {
            'cash': initial_capital,
            'positions': {},
            'portfolio_value': [initial_capital],
            'timestamps': [historical_data.index[0]],
            'trades': []
        }

        for timestamp in historical_data.index:
            # Get current market data slice
            current_data = historical_data.loc[:timestamp]
            
            # Generate trading signals
            signals = self._generate_signals(
                strategy_config,
                current_data
            )
            
            # Execute trades based on signals
            for symbol, signal in signals.items():
                if signal != 0:  # 1 for buy, -1 for sell
                    current_price = current_data[symbol].iloc[-1]
                    
                    if signal > 0:  # Buy signal
                        cash_available = portfolio['cash'] * strategy_config.get(
                            'position_size',
                            0.1
                        )
                        shares = self._calculate_position_size(
                            cash_available,
                            current_price
                        )
                        
                        if shares > 0:
                            cost = self._calculate_trade_cost(
                                shares,
                                current_price,
                                'buy'
                            )
                            
                            if cost <= portfolio['cash']:
                                portfolio['positions'][symbol] = portfolio['positions'].get(
                                    symbol,
                                    0
                                ) + shares
                                portfolio['cash'] -= cost
                                
                                portfolio['trades'].append({
                                    'timestamp': timestamp,
                                    'symbol': symbol,
                                    'action': 'buy',
                                    'shares': shares,
                                    'price': current_price,
                                    'cost': cost
                                })
                    
                    elif signal < 0 and symbol in portfolio['positions']:  # Sell signal
                        shares = portfolio['positions'][symbol]
                        proceeds = self._calculate_trade_cost(
                            shares,
                            current_price,
                            'sell'
                        )
                        
                        portfolio['cash'] += proceeds
                        del portfolio['positions'][symbol]
                        
                        portfolio['trades'].append({
                            'timestamp': timestamp,
                            'symbol': symbol,
                            'action': 'sell',
                            'shares': shares,
                            'price': current_price,
                            'proceeds': proceeds
                        })
            
            # Update portfolio value
            portfolio_value = portfolio['cash']
            for symbol, shares in portfolio['positions'].items():
                portfolio_value += shares * historical_data[symbol].loc[timestamp]
            
            portfolio['portfolio_value'].append(portfolio_value)
            portfolio['timestamps'].append(timestamp)

        return portfolio

    def _generate_signals(
        self,
        strategy_config: Dict,
        data: pd.DataFrame
    ) -> Dict[str, int]:
        """
        Generate trading signals based on strategy configuration
        """
        signals = {}
        
        for symbol in strategy_config['symbols']:
            if strategy_config['type'] == 'moving_average_crossover':
                signals[symbol] = self._moving_average_signal(
                    data[symbol],
                    strategy_config['parameters']
                )
            elif strategy_config['type'] == 'mean_reversion':
                signals[symbol] = self._mean_reversion_signal(
                    data[symbol],
                    strategy_config['parameters']
                )
            elif strategy_config['type'] == 'momentum':
                signals[symbol] = self._momentum_signal(
                    data[symbol],
                    strategy_config['parameters']
                )
                
        return signals

    def _calculate_performance_metrics(self, results: Dict) -> Dict:
        """
        Calculate comprehensive performance metrics
        """
        returns = pd.Series(results['portfolio_value']).pct_change().dropna()
        
        metrics = {
            'total_return': (results['portfolio_value'][-1] / results['portfolio_value'][0] - 1) * 100,
            'annualized_return': self._calculate_annualized_return(returns),
            'volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(results['portfolio_value']),
            'win_rate': self._calculate_win_rate(results['trades']),
            'profit_factor': self._calculate_profit_factor(results['trades']),
            'average_trade': self._calculate_average_trade(results['trades']),
            'trade_count': len(results['trades'])
        }
        
        return metrics

    def _calculate_trade_cost(
        self,
        shares: float,
        price: float,
        trade_type: str
    ) -> float:
        """
        Calculate total cost/proceeds of a trade including commission and slippage
        """
        base_amount = shares * price
        commission = base_amount * self.trading_costs['commission']
        slippage = base_amount * self.trading_costs['slippage']
        
        if trade_type == 'buy':
            return base_amount + commission + slippage
        else:
            return base_amount - commission - slippage

    @staticmethod
    def _moving_average_signal(
        data: pd.Series,
        parameters: Dict
    ) -> int:
        """
        Generate moving average crossover signals
        """
        short_ma = data.rolling(parameters['short_window']).mean()
        long_ma = data.rolling(parameters['long_window']).mean()
        
        if short_ma.iloc[-1] > long_ma.iloc[-1] and short_ma.iloc[-2] <= long_ma.iloc[-2]:
            return 1
        elif short_ma.iloc[-1] < long_ma.iloc[-1] and short_ma.iloc[-2] >= long_ma.iloc[-2]:
            return -1
        return 0

    @staticmethod
    def _mean_reversion_signal(
        data: pd.Series,
        parameters: Dict
    ) -> int:
        """
        Generate mean reversion signals
        """
        z_score = (data - data.rolling(parameters['window']).mean()) / data.rolling(parameters['window']).std()
        
        if z_score.iloc[-1] < -parameters['threshold']:
            return 1
        elif z_score.iloc[-1] > parameters['threshold']:
            return -1
        return 0

    @staticmethod
    def _momentum_signal(
        data: pd.Series,
        parameters: Dict
    ) -> int:
        """
        Generate momentum signals
        """
        returns = data.pct_change(parameters['lookback'])
        
        if returns.iloc[-1] > parameters['threshold']:
            return 1
        elif returns.iloc[-1] < -parameters['threshold']:
            return -1
        return 0