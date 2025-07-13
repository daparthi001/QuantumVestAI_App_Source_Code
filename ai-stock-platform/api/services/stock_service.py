"""
Stock data service
Created: 2025-05-19 03:29:10
Author: daparthi001
Updated: 2025-01-09 (AI Assistant) - Added Warren Buffett analysis methods
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
# Import settings explicitly from the configuration module to avoid
# accidentally importing the module itself when the `core.config`
# package is present in the Python path.
from core.config.settings import settings
from sqlalchemy.orm import Session

from models.stock import Stock, WatchList

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.ALPHA_VANTAGE_API_KEY.get_secret_value()
        self.base_url = "https://www.alphavantage.co/query"

    async def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time stock data from Alpha Vantage"""
        async with aiohttp.ClientSession() as session:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            try:
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
                    if "Global Quote" in data:
                        return data["Global Quote"]
                    return None
            except Exception as e:
                logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
                return None

    async def update_stock_data(self, symbol: str) -> Optional[Stock]:
        """Update stock data in database"""
        data = await self.get_stock_data(symbol)
        if not data:
            return None

        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            stock = Stock(symbol=symbol)

        stock.current_price = float(data.get("05. price", 0))
        stock.high_24h = float(data.get("03. high", 0))
        stock.low_24h = float(data.get("04. low", 0))
        stock.volume_24h = float(data.get("06. volume", 0))
        
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock

    def get_user_watchlist(self, user_id: int) -> List[Stock]:
        """Get user's watchlist"""
        return (self.db.query(Stock)
                .join(WatchList)
                .filter(WatchList.user_id == user_id)
                .all())

    def add_to_watchlist(self, user_id: int, symbol: str) -> bool:
        """Add stock to user's watchlist"""
        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            return False

        if not self.db.query(WatchList).filter(
            WatchList.user_id == user_id,
            WatchList.stock_id == stock.id
        ).first():
            watchlist_item = WatchList(user_id=user_id, stock_id=stock.id)
            self.db.add(watchlist_item)
            self.db.commit()
        return True

    def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """Remove stock from user's watchlist"""
        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            return False

        watchlist_item = self.db.query(WatchList).filter(
            WatchList.user_id == user_id,
            WatchList.stock_id == stock.id
        ).first()
        
        if watchlist_item:
            self.db.delete(watchlist_item)
            self.db.commit()
            return True
        return False

    async def get_buffett_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get Warren Buffett analysis for a stock"""
        try:
            # Fetch fundamental data from multiple sources
            stock_data = await self.get_stock_data(symbol)
            if not stock_data:
                logger.warning(f"No stock data found for {symbol}")
                return None

            # Get additional fundamental metrics
            fundamental_data = await self.get_fundamental_data(symbol)
            
            # Calculate Buffett metrics
            buffett_metrics = self._calculate_buffett_metrics(stock_data, fundamental_data)
            
            return buffett_metrics
        except Exception as e:
            logger.error(f"Error calculating Buffett analysis for {symbol}: {str(e)}")
            return None

    async def get_fundamental_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch fundamental data for a stock"""
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch company overview
                params = {
                    "function": "OVERVIEW",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                async with session.get(self.base_url, params=params) as response:
                    overview_data = await response.json()
                
                # Fetch income statement
                params = {
                    "function": "INCOME_STATEMENT",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                async with session.get(self.base_url, params=params) as response:
                    income_data = await response.json()
                
                # Fetch balance sheet
                params = {
                    "function": "BALANCE_SHEET",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                async with session.get(self.base_url, params=params) as response:
                    balance_data = await response.json()
                
                # Fetch cash flow
                params = {
                    "function": "CASH_FLOW",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                async with session.get(self.base_url, params=params) as response:
                    cash_flow_data = await response.json()
                
                return {
                    "overview": overview_data,
                    "income_statement": income_data,
                    "balance_sheet": balance_data,
                    "cash_flow": cash_flow_data
                }
            except Exception as e:
                logger.error(f"Error fetching fundamental data for {symbol}: {str(e)}")
                return None

    def _calculate_buffett_metrics(self, stock_data: Dict[str, Any], fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Warren Buffett investment metrics"""
        try:
            overview = fundamental_data.get("overview", {})
            income_statements = fundamental_data.get("income_statement", {}).get("annualReports", [])
            balance_sheets = fundamental_data.get("balance_sheet", {}).get("annualReports", [])
            cash_flows = fundamental_data.get("cash_flow", {}).get("annualReports", [])
            
            # Extract key metrics
            current_price = float(stock_data.get("05. price", 0))
            market_cap = float(overview.get("MarketCapitalization", 0))
            
            # Get latest financial data
            latest_income = income_statements[0] if income_statements else {}
            latest_balance = balance_sheets[0] if balance_sheets else {}
            latest_cash_flow = cash_flows[0] if cash_flows else {}
            
            # Calculate key metrics
            revenue = float(latest_income.get("totalRevenue", 0))
            net_income = float(latest_income.get("netIncome", 0))
            total_debt = float(latest_balance.get("totalDebt", 0))
            total_equity = float(latest_balance.get("totalShareholderEquity", 0))
            free_cash_flow = float(latest_cash_flow.get("operatingCashflow", 0)) - float(latest_cash_flow.get("capitalExpenditures", 0))
            
            # Calculate derived metrics
            return_on_equity = net_income / total_equity if total_equity > 0 else 0
            operating_margin = float(latest_income.get("operatingIncome", 0)) / revenue if revenue > 0 else 0
            debt_to_equity = total_debt / total_equity if total_equity > 0 else 0
            
            # Calculate earnings growth rate (simplified)
            if len(income_statements) >= 2:
                current_earnings = float(income_statements[0].get("netIncome", 0))
                previous_earnings = float(income_statements[1].get("netIncome", 0))
                earnings_growth = (current_earnings - previous_earnings) / previous_earnings if previous_earnings > 0 else 0
            else:
                earnings_growth = 0.05  # Default 5% growth
            
            # Calculate intrinsic value using simplified DCF
            intrinsic_value = self._calculate_intrinsic_value(
                free_cash_flow=free_cash_flow,
                growth_rate=max(0.02, min(0.15, earnings_growth)),
                discount_rate=0.10,
                terminal_growth_rate=0.03
            )
            
            # Calculate margin of safety
            margin_of_safety = ((intrinsic_value - current_price) / current_price) * 100 if current_price > 0 else 0
            
            # Calculate quality score
            quality_metrics = self._calculate_quality_metrics(
                return_on_equity=return_on_equity,
                operating_margin=operating_margin,
                debt_to_equity=debt_to_equity,
                earnings_growth=earnings_growth
            )
            
            quality_score = (
                quality_metrics["consistent_earnings_growth"] * 0.25 +
                quality_metrics["high_roe"] * 0.25 +
                quality_metrics["low_debt_to_equity"] * 0.20 +
                quality_metrics["competitive_advantage"] * 0.15 +
                quality_metrics["management_effectiveness"] * 0.15
            )
            
            # Generate investment recommendation
            recommendation, reasoning = self._generate_investment_recommendation(
                margin_of_safety=margin_of_safety,
                quality_score=quality_score,
                return_on_equity=return_on_equity,
                operating_margin=operating_margin
            )
            
            return {
                "intrinsic_value": intrinsic_value,
                "margin_of_safety": margin_of_safety,
                "quality_score": quality_score,
                "investment_recommendation": recommendation,
                "reasoning": reasoning,
                "quality_metrics": quality_metrics
            }
        except Exception as e:
            logger.error(f"Error calculating Buffett metrics: {str(e)}")
            return None

    def _calculate_intrinsic_value(self, free_cash_flow: float, growth_rate: float, discount_rate: float, terminal_growth_rate: float) -> float:
        """Calculate intrinsic value using DCF model"""
        if free_cash_flow <= 0:
            return 0
        
        years_to_project = 10
        total_value = 0
        
        # Calculate present value of projected cash flows
        for year in range(1, years_to_project + 1):
            projected_cash_flow = free_cash_flow * (1 + growth_rate) ** year
            present_value = projected_cash_flow / (1 + discount_rate) ** year
            total_value += present_value
        
        # Calculate terminal value
        final_year_cash_flow = free_cash_flow * (1 + growth_rate) ** years_to_project
        terminal_value = (final_year_cash_flow * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        present_terminal_value = terminal_value / (1 + discount_rate) ** years_to_project
        
        total_value += present_terminal_value
        return total_value

    def _calculate_quality_metrics(self, return_on_equity: float, operating_margin: float, debt_to_equity: float, earnings_growth: float) -> Dict[str, float]:
        """Calculate business quality metrics"""
        return {
            "consistent_earnings_growth": min(100, max(0, earnings_growth * 1000)),
            "high_roe": min(100, max(0, (return_on_equity / 0.15) * 100)),
            "low_debt_to_equity": min(100, max(0, (1 - min(1, debt_to_equity)) * 100)),
            "competitive_advantage": min(100, max(0, operating_margin * 500)),
            "management_effectiveness": min(100, max(0, (return_on_equity + operating_margin) * 50))
        }

    def _generate_investment_recommendation(self, margin_of_safety: float, quality_score: float, return_on_equity: float, operating_margin: float) -> tuple:
        """Generate investment recommendation based on Buffett criteria"""
        reasoning = []
        
        # Strong buy conditions
        if margin_of_safety > 20 and quality_score > 70:
            reasoning.append(f"Excellent margin of safety ({margin_of_safety:.1f}%)")
            reasoning.append(f"High quality business (score: {quality_score:.1f})")
            if return_on_equity > 0.15:
                reasoning.append("Strong return on equity (>15%)")
            if operating_margin > 0.15:
                reasoning.append("Healthy operating margins")
            return "BUY", reasoning
        
        # Moderate buy conditions
        elif margin_of_safety > 10 and quality_score > 60:
            reasoning.append(f"Good margin of safety ({margin_of_safety:.1f}%)")
            reasoning.append(f"Decent quality business (score: {quality_score:.1f})")
            return "BUY", reasoning
        
        # Hold conditions
        elif margin_of_safety > 0 and quality_score > 50:
            reasoning.append(f"Positive margin of safety ({margin_of_safety:.1f}%)")
            reasoning.append(f"Average quality business (score: {quality_score:.1f})")
            return "HOLD", reasoning
        
        # Sell conditions
        else:
            reasoning.append(f"Negative margin of safety ({margin_of_safety:.1f}%)")
            if quality_score < 50:
                reasoning.append(f"Below average quality business (score: {quality_score:.1f})")
            if return_on_equity < 0.10:
                reasoning.append("Low return on equity (<10%)")
            return "SELL", reasoning
        return False
