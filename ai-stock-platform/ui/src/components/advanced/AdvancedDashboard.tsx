/**
 * Advanced Features Dashboard
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useState } from 'react';
import { Tab, Nav } from 'react-bootstrap';
import PredictionAnalysis from './PredictionAnalysis';
import SentimentAnalysis from './SentimentAnalysis';
import IndicatorBuilder from './IndicatorBuilder';
import BacktestingForm from './BacktestingForm';
import BacktestResults from './BacktestResults';
import { useError } from '../../contexts/ErrorContext';

const AdvancedDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('predictions');
  const [backtestId, setBacktestId] = useState<string | null>(null);
  const { showErrorMessage } = useError();
  
  const handleBacktestComplete = (id: string) => {
    setBacktestId(id);
    // Switch to results sub-tab within backtesting
    setActiveTab('backtesting-results');
  };
  
  const handleApplyIndicator = (formula: string, name: string) => {
    // This would typically update a global state or context
    // For now, we'll just show a success message
    showErrorMessage(`Custom indicator "${name}" applied successfully`);
  };
  
  return (
    <div className="advanced-dashboard">
      <h2 className="section-title">Advanced Analysis Tools</h2>
      <p className="section-description">
        Leverage AI and machine learning to gain deeper insights into market trends and stock performance.
      </p>
      
      <div className="advanced-tabs-container mt-4">
        <Nav variant="tabs" className="advanced-tabs">
          <Nav.Item>
            <Nav.Link 
              className={activeTab === 'predictions' ? 'active' : ''} 
              onClick={() => setActiveTab('predictions')}
            >
              <i className="bi bi-graph-up-arrow"></i> AI Predictions
            </Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link 
              className={activeTab === 'sentiment' ? 'active' : ''} 
              onClick={() => setActiveTab('sentiment')}
            >
              <i className="bi bi-chat-square-text"></i> Sentiment Analysis
            </Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link 
              className={activeTab === 'indicators' ? 'active' : ''} 
              onClick={() => setActiveTab('indicators')}
            >
              <i className="bi bi-sliders"></i> Custom Indicators
            </Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link 
              className={activeTab === 'backtesting' ? 'active' : ''} 
              onClick={() => setActiveTab('backtesting')}
            >
              <i className="bi bi-clipboard-data"></i> Backtesting
            </Nav.Link>
          </Nav.Item>
          {backtestId && (
            <Nav.Item>
              <Nav.Link 
                className={activeTab === 'backtesting-results' ? 'active' : ''} 
                onClick={() => setActiveTab('backtesting-results')}
              >
                <i className="bi bi-bar-chart-line"></i> Backtest Results
              </Nav.Link>
            </Nav.Item>
          )}
        </Nav>
        
        <div className="tab-content p-4 border border-top-0 rounded-bottom">
          {activeTab === 'predictions' && (
            <PredictionAnalysis />
          )}
          
          {activeTab === 'sentiment' && (
            <SentimentAnalysis />
          )}
          
          {activeTab === 'indicators' && (
            <IndicatorBuilder 
              symbol="AAPL" // This would typically be dynamic
              onApply={handleApplyIndicator} 
            />
          )}
          
          {activeTab === 'backtesting' && (
            <BacktestingForm onBacktestComplete={handleBacktestComplete} />
          )}
          
          {activeTab === 'backtesting-results' && backtestId && (
            <BacktestResults backtestId={backtestId} />
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedDashboard;