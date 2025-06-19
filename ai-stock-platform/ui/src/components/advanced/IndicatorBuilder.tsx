/**
 * Custom Technical Indicator Builder
 * Created: 2025-06-19 03:09:13
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { stockService } from '../../services/api';
import { useError } from '../../contexts/ErrorContext';

interface IndicatorComponent {
  id: string;
  name: string;
  type: 'price' | 'volume' | 'indicator' | 'function';
  description: string;
  parameterCount?: number;
}

// Available indicator components
const indicatorComponents: IndicatorComponent[] = [
  { id: 'close', name: 'Close Price', type: 'price', description: 'Closing price of the stock' },
  { id: 'open', name: 'Open Price', type: 'price', description: 'Opening price of the stock' },
  { id: 'high', name: 'High Price', type: 'price', description: 'Highest price of the stock' },
  { id: 'low', name: 'Low Price', type: 'price', description: 'Lowest price of the stock' },
  { id: 'volume', name: 'Volume', type: 'volume', description: 'Trading volume' },
  { id: 'sma', name: 'SMA', type: 'indicator', description: 'Simple Moving Average', parameterCount: 1 },
  { id: 'ema', name: 'EMA', type: 'indicator', description: 'Exponential Moving Average', parameterCount: 1 },
  { id: 'rsi', name: 'RSI', type: 'indicator', description: 'Relative Strength Index', parameterCount: 1 },
  { id: 'macd', name: 'MACD', type: 'indicator', description: 'Moving Average Convergence Divergence', parameterCount: 3 },
  { id: 'bbands', name: 'Bollinger Bands', type: 'indicator', description: 'Bollinger Bands', parameterCount: 2 },
  { id: 'add', name: 'Add', type: 'function', description: 'Addition operation', parameterCount: 2 },
  { id: 'subtract', name: 'Subtract', type: 'function', description: 'Subtraction operation', parameterCount: 2 },
  { id: 'multiply', name: 'Multiply', type: 'function', description: 'Multiplication operation', parameterCount: 2 },
  { id: 'divide', name: 'Divide', type: 'function', description: 'Division operation', parameterCount: 2 },
  { id: 'crossover', name: 'Crossover', type: 'function', description: 'Detect when one line crosses another', parameterCount: 2 },
  { id: 'max', name: 'Max', type: 'function', description: 'Maximum value', parameterCount: 2 },
  { id: 'min', name: 'Min', type: 'function', description: 'Minimum value', parameterCount: 2 },
];

interface IndicatorBuilderProps {
  symbol: string;
  onApply: (formula: string, name: string) => void;
}

const IndicatorBuilder: React.FC<IndicatorBuilderProps> = ({ symbol, onApply }) => {
  const [formula, setFormula] = useState<string>('');
  const [indicatorName, setIndicatorName] = useState<string>('');
  const [isBuilding, setIsBuilding] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const { showErrorMessage } = useError();
  
  const handleAddComponent = (component: IndicatorComponent) => {
    if (component.type === 'function' || component.type === 'indicator') {
      setFormula(prev => `${prev}${component.id}()`);
    } else {
      setFormula(prev => `${prev}${component.id}`);
    }
  };
  
  const handlePreview = async () => {
    if (!formula.trim()) {
      showErrorMessage('Please enter a formula first');
      return;
    }
    
    setIsBuilding(true);
    
    try {
      const response = await stockService.calculateCustomIndicator(symbol, formula);
      setPreviewData(response);
    } catch (error: any) {
      showErrorMessage(error.response?.data?.message || 'Failed to preview indicator');
    } finally {
      setIsBuilding(false);
    }
  };
  
  const handleApply = () => {
    if (!formula.trim()) {
      showErrorMessage('Please enter a formula first');
      return;
    }
    
    if (!indicatorName.trim()) {
      showErrorMessage('Please enter a name for your indicator');
      return;
    }
    
    onApply(formula, indicatorName);
    
    // Reset the form
    setFormula('');
    setIndicatorName('');
    setPreviewData(null);
  };
  
  return (
    <div className="indicator-builder">
      <h3>Custom Indicator Builder</h3>
      <p className="text-muted">Build custom technical indicators by combining existing indicators and mathematical operations.</p>
      
      <div className="form-group mb-3">
        <label htmlFor="indicatorName">Indicator Name</label>
        <input
          type="text"
          id="indicatorName"
          className="form-control"
          value={indicatorName}
          onChange={(e) => setIndicatorName(e.target.value)}
          placeholder="My Custom Indicator"
        />
      </div>
      
      <div className="form-group mb-3">
        <label htmlFor="formula">Formula</label>
        <textarea
          id="formula"
          className="formula-editor"
          value={formula}
          onChange={(e) => setFormula(e.target.value)}
          placeholder="e.g., subtract(sma(close, 20), sma(close, 50))"
        />
      </div>
      
      <div className="mb-3">
        <h5>Components</h5>
        <div className="mb-2">
          <strong>Data Types:</strong>
        </div>
        <div className="component-list">
          {indicatorComponents.filter(c => c.type === 'price' || c.type === 'volume').map(component => (
            <span 
              key={component.id} 
              className="component-item" 
              onClick={() => handleAddComponent(component)}
              title={component.description}
            >
              {component.name}
            </span>
          ))}
        </div>
        
        <div className="mt-3 mb-2">
          <strong>Indicators:</strong>
        </div>
        <div className="component-list">
          {indicatorComponents.filter(c => c.type === 'indicator').map(component => (
            <span 
              key={component.id} 
              className="component-item" 
              onClick={() => handleAddComponent(component)}
              title={component.description}
            >
              {component.name}
            </span>
          ))}
        </div>
        
        <div className="mt-3 mb-2">
          <strong>Operations:</strong>
        </div>
        <div className="component-list">
          {indicatorComponents.filter(c => c.type === 'function').map(component => (
            <span 
              key={component.id} 
              className="component-item" 
              onClick={() => handleAddComponent(component)}
              title={component.description}
            >
              {component.name}
            </span>
          ))}
        </div>
      </div>
      
      <div className="row">
        <div className="col">
          <button 
            className="btn btn-outline-primary" 
            onClick={handlePreview}
            disabled={isBuilding || !formula.trim()}
          >
            {isBuilding ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Previewing...
              </>
            ) : 'Preview'}
          </button>
        </div>
        <div className="col text-end">
          <button 
            className="btn btn-primary" 
            onClick={handleApply}
            disabled={isBuilding || !formula.trim() || !indicatorName.trim()}
          >
            Apply Indicator
          </button>
        </div>
      </div>
      
      {previewData && (
        <div className="preview-container mt-4">
          <h5>Preview</h5>
          <div className="chart-container">
            {/* Chart rendering code would go here */}
            <p className="text-muted">Preview data is available. Apply the indicator to see it on the main chart.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default IndicatorBuilder;