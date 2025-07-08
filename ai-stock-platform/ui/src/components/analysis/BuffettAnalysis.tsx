/**
 * Warren Buffett Analysis Component
 * Created: 2025-01-09
 * Author: AI Assistant
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Alert, Badge, ProgressBar, Spinner } from 'react-bootstrap';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip
} from 'recharts';
import { stockService } from '../../services/api';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/formatters';
import { 
  calculateBuffettMetrics, 
  BuffettMetrics, 
  FundamentalData,
  BusinessQualityMetrics,
  assessBusinessQuality
} from '../../utils/buffettCalculations';

interface BuffettAnalysisProps {
  symbol: string;
}

const BuffettAnalysis: React.FC<BuffettAnalysisProps> = ({ symbol }) => {
  const [buffettMetrics, setBuffettMetrics] = useState<BuffettMetrics | null>(null);
  const [qualityMetrics, setQualityMetrics] = useState<BusinessQualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBuffettAnalysis();
  }, [symbol]);

  const fetchBuffettAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch fundamental data
      const [metricsResponse, quoteResponse] = await Promise.all([
        stockService.getFundamentalMetrics(symbol),
        stockService.getStockQuote(symbol)
      ]);

      const fundamentalData = metricsResponse.data;
      const quoteData = quoteResponse;

      // Prepare data for Buffett analysis
      const analysisData: FundamentalData = {
        marketCap: fundamentalData.marketCap || 0,
        freeCashFlow: fundamentalData.freeCashFlow || 0,
        revenue: fundamentalData.revenue || 0,
        netIncome: fundamentalData.netIncome || 0,
        totalDebt: fundamentalData.totalDebt || 0,
        totalEquity: fundamentalData.totalEquity || fundamentalData.marketCap * 0.6, // Fallback estimate
        returnOnEquity: fundamentalData.returnOnEquity || 0,
        eps: fundamentalData.eps || 0,
        bookValue: fundamentalData.bookValue || 0,
        dividendYield: fundamentalData.dividendYield || 0,
        currentPrice: quoteData.price || 0,
        historicalGrowthRate: fundamentalData.historicalGrowthRate || 0.05, // Default 5% growth
        operatingMargin: fundamentalData.operatingMargin || 0
      };

      // Calculate Buffett metrics
      const metrics = calculateBuffettMetrics(analysisData);
      const quality = assessBusinessQuality(analysisData);

      setBuffettMetrics(metrics);
      setQualityMetrics(quality);
    } catch (err) {
      setError('Failed to load Buffett analysis data');
      console.error('Error fetching Buffett analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation: string): string => {
    switch (recommendation) {
      case 'BUY': return 'success';
      case 'HOLD': return 'warning';
      case 'SELL': return 'danger';
      default: return 'secondary';
    }
  };

  const getQualityColor = (score: number): string => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  const renderIntrinsicValueCard = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Intrinsic Value Analysis</h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={6}>
            <div className="text-center">
              <h4 className="text-primary">
                {formatCurrency(buffettMetrics?.intrinsicValue || 0)}
              </h4>
              <p className="text-muted">Calculated Intrinsic Value</p>
            </div>
          </Col>
          <Col md={6}>
            <div className="text-center">
              <h4 className={`text-${(buffettMetrics?.marginOfSafety ?? 0) > 0 ? 'success' : 'danger'}`}>
                {formatPercentage(buffettMetrics?.marginOfSafety || 0)}
              </h4>
              <p className="text-muted">Margin of Safety</p>
            </div>
          </Col>
        </Row>
        <Alert variant="info" className="mt-3">
          <strong>What is Intrinsic Value?</strong><br/>
          Intrinsic value represents the true worth of a business based on its future cash flows. 
          Warren Buffett uses this to determine if a stock is undervalued or overvalued.
        </Alert>
      </Card.Body>
    </Card>
  );

  const renderQualityScoreCard = () => {
    const qualityData = qualityMetrics ? [
      { name: 'Earnings Growth', value: qualityMetrics.consistentEarningsGrowth },
      { name: 'Return on Equity', value: qualityMetrics.highROE },
      { name: 'Debt Management', value: qualityMetrics.lowDebtToEquity },
      { name: 'Competitive Advantage', value: qualityMetrics.competitiveAdvantage },
      { name: 'Management Effectiveness', value: qualityMetrics.managementEffectiveness }
    ] : [];

    return (
      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Business Quality Assessment</h5>
        </Card.Header>
        <Card.Body>
          <div className="text-center mb-3">
            <h4 className={`text-${getQualityColor(buffettMetrics?.qualityScore || 0)}`}>
              {formatNumber(buffettMetrics?.qualityScore || 0)}/100
            </h4>
            <p className="text-muted">Overall Quality Score</p>
          </div>
          
          <div className="mb-3">
            {qualityData.map((metric, index) => (
              <div key={index} className="mb-2">
                <div className="d-flex justify-content-between">
                  <small>{metric.name}</small>
                  <small>{formatNumber(metric.value)}</small>
                </div>
                <ProgressBar 
                  now={metric.value} 
                  variant={getQualityColor(metric.value)} 
                  style={{ height: '8px' }}
                />
              </div>
            ))}
          </div>

          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={qualityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Card.Body>
      </Card>
    );
  };

  const renderInvestmentRecommendation = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Investment Recommendation</h5>
      </Card.Header>
      <Card.Body>
        <div className="text-center mb-3">
          <Badge 
            bg={getRecommendationColor(buffettMetrics?.investmentRecommendation || '')}
            className="p-3"
            style={{ fontSize: '1.2rem' }}
          >
            {buffettMetrics?.investmentRecommendation}
          </Badge>
        </div>
        
        <div className="mt-3">
          <h6>Analysis Reasoning:</h6>
          <ul>
            {buffettMetrics?.reasoning.map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
        </div>

        <Alert variant="warning" className="mt-3">
          <strong>Investment Disclaimer:</strong><br/>
          This analysis is for educational purposes only and should not be considered as investment advice. 
          Always conduct your own research and consult with financial professionals before making investment decisions.
        </Alert>
      </Card.Body>
    </Card>
  );

  const renderBuffettPrinciples = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Warren Buffett's Key Investment Principles</h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={6}>
            <h6>🎯 Value Investing</h6>
            <p className="small">
              Buy businesses trading below their intrinsic value. Focus on the business, not the stock price.
            </p>
            
            <h6>🛡️ Margin of Safety</h6>
            <p className="small">
              Only invest when you can buy at a significant discount to intrinsic value (typically 20-30%).
            </p>
            
            <h6>📈 Quality Business</h6>
            <p className="small">
              Look for businesses with consistent earnings growth, high return on equity, and competitive advantages.
            </p>
          </Col>
          <Col md={6}>
            <h6>💰 Cash Flow Focus</h6>
            <p className="small">
              Prioritize businesses that generate strong and growing free cash flows.
            </p>
            
            <h6>🏰 Economic Moats</h6>
            <p className="small">
              Invest in companies with sustainable competitive advantages that protect their market position.
            </p>
            
            <h6>⏰ Long-term Perspective</h6>
            <p className="small">
              Hold quality businesses for years or decades, not months or weeks.
            </p>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  if (loading) {
    return (
      <Card>
        <Card.Body className="text-center p-4">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Analyzing {symbol} using Warren Buffett's methods...</p>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <Card.Body>
          <Alert variant="danger">{error}</Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <div className="buffett-analysis">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4>Warren Buffett Analysis - {symbol}</h4>
        <Badge bg="info">Value Investment Analysis</Badge>
      </div>
      
      <Row>
        <Col lg={8}>
          {renderIntrinsicValueCard()}
          {renderQualityScoreCard()}
          {renderInvestmentRecommendation()}
        </Col>
        <Col lg={4}>
          {renderBuffettPrinciples()}
        </Col>
      </Row>
    </div>
  );
};

export default BuffettAnalysis;