/**
 * Portfolio Backtesting Form
 * Created: 2025-06-19 03:09:13
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { backtestService, BacktestParameters } from '../../services/backtest-service';
import { stockService } from '../../services/api';
import { useError } from '../../contexts/ErrorContext';

interface BacktestingFormProps {
  onBacktestComplete: (backtestId: string) => void;
}

const BacktestingForm: React.FC<BacktestingFormProps> = ({ onBacktestComplete }) => {
  const [parameters, setParameters] = useState<BacktestParameters>({
    initialCapital: 10000,
    symbols: ['AAPL'],
    startDate: '2024-01-01',
    endDate: '2025-01-01',
    strategy: 'buy_and_hold',
    transactionFee: 0.001,
    slippage: 0.001
  });
  
  const [availableSymbols, setAvailableSymbols] = useState<Array<{symbol: string, name: string}>>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const { showErrorMessage } = useError();
  
  // Fetch available symbols
  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        const symbols = await stockService.getAvailableSymbols();
        setAvailableSymbols(symbols.map(symbol => ({ symbol, name: symbol })));
      } catch (error) {
        console.error('Error fetching symbols:', error);
      }
    };
    
    fetchSymbols();
  }, []);
  
  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    // Handle numeric inputs
    if (type === 'number') {
      setParameters(prev => ({
        ...prev,
        [name]: parseFloat(value)
      }));
    } else {
      setParameters(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  // Handle strategy selection
  const handleStrategyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const strategy = e.target.value as BacktestParameters['strategy'];
    
    setParameters(prev => ({
      ...prev,
      strategy,
      // Add default values for specific strategies
      ...(strategy === 'rebalance' ? { rebalanceFrequency: 'monthly' } : {}),
      ...(strategy === 'momentum' || strategy === 'mean_reversion' ? { 
        stopLoss: 0.05, 
        takeProfit: 0.2 
      } : {})
    }));
  };
  
  // Handle symbol selection
  const handleSymbolSelect = (symbol: string) => {
    if (parameters.symbols.includes(symbol)) {
      // Remove symbol if already selected
      setParameters(prev => ({
        ...prev,
        symbols: prev.symbols.filter(s => s !== symbol)
      }));
    } else {
      // Add symbol if not already selected
      setParameters(prev => ({
        ...prev,
        symbols: [...prev.symbols, symbol]
      }));
    }
  };
  
  // Filter symbols based on search term
  const filteredSymbols = availableSymbols.filter(s => 
    s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || 
    s.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Run backtest
  const handleRunBacktest = async () => {
    if (parameters.symbols.length === 0) {
      showErrorMessage('Please select at least one symbol');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await backtestService.runBacktest(parameters);
      onBacktestComplete(result.id);
    } catch (error: any) {
      showErrorMessage(error.response?.data?.message || 'Failed to run backtest');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="backtest-form">
      <h3>Portfolio Backtesting</h3>
      <p className="text-muted">Test investment strategies on historical data to evaluate performance</p>
      
      <div className="row g-3">
        <div className="col-md-6">
          <div className="form-group mb-3">
            <label htmlFor="initialCapital">Initial Capital ($)</label>
            <input
              type="number"
              id="initialCapital"
              name="initialCapital"
              className="form-control"
              value={parameters.initialCapital}
              onChange={handleInputChange}
              min="1000"
            />
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="form-group mb-3">
            <label htmlFor="strategy">Strategy</label>
            <select
              id="strategy"
              name="strategy"
              className="form-select"
              value={parameters.strategy}
              onChange={handleStrategyChange}
            >
              <option value="buy_and_hold">Buy and Hold</option>
              <option value="rebalance">Periodic Rebalancing</option>
              <option value="momentum">Momentum</option>
              <option value="mean_reversion">Mean Reversion</option>
              <option value="custom">Custom Strategy</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="row g-3">
        <div className="col-md-6">
          <div className="form-group mb-3">
            <label htmlFor="startDate">Start Date</label>
            <input
              type="date"
              id="startDate"
              name="startDate"
              className="form-control"
              value={parameters.startDate}
              onChange={handleInputChange}
            />
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="form-group mb-3">
            <label htmlFor="endDate">End Date</label>
            <input
              type="date"
              id="endDate"
              name="endDate"
              className="form-control"
              value={parameters.endDate}
              onChange={handleInputChange}
            />
          </div>
        </div>
      </div>
      
      {parameters.strategy === 'rebalance' && (
        <div className="form-group mb-3">
          <label htmlFor="rebalanceFrequency">Rebalance Frequency</label>
          <select
            id="rebalanceFrequency"
            name="rebalanceFrequency"
            className="form-select"
            value={parameters.rebalanceFrequency}
            onChange={handleInputChange}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
          </select>
        </div>
      )}
      
      {(parameters.strategy === 'momentum' || parameters.strategy === 'mean_reversion') && (
        <div className="row g-3">
          <div className="col-md-6">
            <div className="form-group mb-3">
              <label htmlFor="stopLoss">Stop Loss (%)</label>
              <input
                type="number"
                id="stopLoss"
                name="stopLoss"
                className="form-control"
                value={parameters.stopLoss}
                onChange={handleInputChange}
                min="0"
                max="100"
                step="0.1"
              />
            </div>
          </div>
          
          <div className="col-md-6">
            <div className="form-group mb-3">
              <label htmlFor="takeProfit">Take Profit (%)</label>
              <input
                type="number"
                id="takeProfit"
                name="takeProfit"
                className="form-control"
                value={parameters.takeProfit}
                onChange={handleInputChange}
                min="0"
                max="100"
                step="0.1"
              />
            </div>
          </div>
        </div>
      )}
      
      <div className="form-group mb-3">
        <label>Select Symbols</label>
        <div className="input-group mb-2">
          <input
            type="text"
            className="form-control"
            placeholder="Search symbols..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button 
            className="btn btn-outline-secondary" 
            type="button"
            onClick={() => setSearchTerm('')}
          >
            Clear
          </button>
        </div>
        
        <div className="symbols-container">
          {filteredSymbols.length > 0 ? (
            <div className="symbol-list">
              {filteredSymbols.slice(0, 20).map(symbol => (
                <div 
                  key={symbol.symbol} 
                  className={`symbol-item ${parameters.symbols.includes(symbol.symbol) ? 'selected' : ''}`}
                  onClick={() => handleSymbolSelect(symbol.symbol)}
                >
                  <span className="symbol-ticker">{symbol.symbol}</span>
                  <span className="symbol-name">{symbol.name}</span>
                </div>
              ))}
              {filteredSymbols.length > 20 && (
                <div className="text-muted small">
                  Showing 20 of {filteredSymbols.length} results. Refine your search to see more.
                </div>
              )}
            </div>
          ) : (
            <div className="text-muted">No symbols match your search.</div>
          )}
        </div>
        
        <div className="selected-symbols mt-2">
          <div className="d-flex flex-wrap gap-2">
            {parameters.symbols.map(symbol => (
              <span key={symbol} className="badge bg-primary">
                {symbol}
                <button 
                  type="button" 
                  className="btn-close btn-close-white ms-2" 
                  onClick={() => handleSymbolSelect(symbol)}
                ></button>
              </span>
            ))}
          </div>
        </div>
      </div>
      
      <div className="advanced-settings mb-3">
        <h5>Advanced Settings</h5>
        <div className="row g-3">
          <div className="col-md-6">
            <div className="form-group">
              <label htmlFor="transactionFee">Transaction Fee (%)</label>
              <input
                type="number"
                id="transactionFee"
                name="transactionFee"
                className="form-control"
                value={parameters.transactionFee}
                onChange={handleInputChange}
                min="0"
                max="10"
                step="0.001"
              />
            </div>
          </div>
          
          <div className="col-md-6">
            <div className="form-group">
              <label htmlFor="slippage">Slippage (%)</label>
              <input
                type="number"
                id="slippage"
                name="slippage"
                className="form-control"
                value={parameters.slippage}
                onChange={handleInputChange}
                min="0"
                max="10"
                step="0.001"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <button 
          className="btn btn-primary btn-lg" 
          onClick={handleRunBacktest}
          disabled={isLoading || parameters.symbols.length === 0}
        >
          {isLoading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Running Backtest...
            </>
          ) : 'Run Backtest'}
        </button>
      </div>
    </div>
  );
};

export default BacktestingForm;