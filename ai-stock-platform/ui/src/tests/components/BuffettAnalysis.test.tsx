/**
 * Warren Buffett Analysis Component Tests
 * Created: 2025-01-09
 * Author: AI Assistant
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BuffettAnalysis from '../../components/analysis/BuffettAnalysis';
import { stockService } from '../../services/api';

// Mock the services
vi.mock('../../services/api', () => ({
  stockService: {
    getFundamentalMetrics: vi.fn(),
    getStockQuote: vi.fn(),
    getBuffettAnalysis: vi.fn()
  }
}));

// Mock the formatters
vi.mock('../../utils/formatters', () => ({
  formatCurrency: vi.fn((value) => `$${value.toFixed(2)}`),
  formatPercentage: vi.fn((value) => `${value.toFixed(1)}%`),
  formatNumber: vi.fn((value) => value.toFixed(1))
}));

const mockFundamentalData = {
  marketCap: 2000000000000,
  freeCashFlow: 92000000000,
  revenue: 365000000000,
  netIncome: 94000000000,
  totalDebt: 120000000000,
  totalEquity: 180000000000,
  returnOnEquity: 0.25,
  eps: 3.75,
  bookValue: 45.67,
  dividendYield: 0.015,
  operatingMargin: 0.30,
  peRatio: 25.4,
  currentRatio: 1.5,
  quickRatio: 1.2
};

const mockQuoteData = {
  symbol: 'AAPL',
  price: 150.00,
  change: 2.50,
  changePercent: 1.67,
  volume: 50000000,
  marketCap: 2000000000000
};

const mockBuffettAnalysis = {
  intrinsicValue: 180.00,
  marginOfSafety: 20.0,
  qualityScore: 85.5,
  investmentRecommendation: 'BUY',
  reasoning: [
    'Excellent margin of safety (20.0%)',
    'High quality business (score: 85.5)',
    'Strong return on equity (>15%)',
    'Healthy operating margins'
  ],
  qualityMetrics: {
    consistentEarningsGrowth: 90,
    highROE: 85,
    lowDebtToEquity: 75,
    competitiveAdvantage: 88,
    managementEffectiveness: 80
  }
};

describe('BuffettAnalysis Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (stockService.getFundamentalMetrics as any).mockResolvedValue({ data: mockFundamentalData });
    (stockService.getStockQuote as any).mockResolvedValue(mockQuoteData);
    (stockService.getBuffettAnalysis as any).mockResolvedValue(mockBuffettAnalysis);
  });

  it('renders loading state initially', () => {
    render(<BuffettAnalysis symbol="AAPL" />);
    expect(screen.getByText('Analyzing AAPL using Warren Buffett\'s methods...')).toBeInTheDocument();
  });

  it('displays Warren Buffett analysis after loading', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Warren Buffett Analysis - AAPL')).toBeInTheDocument();
    });

    // Check if intrinsic value is displayed
    await waitFor(() => {
      expect(screen.getByText('Calculated Intrinsic Value')).toBeInTheDocument();
    });

    // Check if margin of safety is displayed
    await waitFor(() => {
      expect(screen.getByText('Margin of Safety')).toBeInTheDocument();
    });

    // Check if quality score is displayed
    await waitFor(() => {
      expect(screen.getByText('Overall Quality Score')).toBeInTheDocument();
    });

    // Check if investment recommendation is displayed
    await waitFor(() => {
      expect(screen.getByText('Investment Recommendation')).toBeInTheDocument();
    });
  });

  it('displays investment recommendation with correct styling', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      const buyBadge = screen.getByText('BUY');
      expect(buyBadge).toBeInTheDocument();
      expect(buyBadge).toHaveClass('bg-success');
    });
  });

  it('displays reasoning for investment recommendation', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Analysis Reasoning:')).toBeInTheDocument();
      expect(screen.getByText('Excellent margin of safety (20.0%)')).toBeInTheDocument();
      expect(screen.getByText('High quality business (score: 85.5)')).toBeInTheDocument();
      expect(screen.getByText('Strong return on equity (>15%)')).toBeInTheDocument();
      expect(screen.getByText('Healthy operating margins')).toBeInTheDocument();
    });
  });

  it('displays Buffett principles education section', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Warren Buffett\'s Key Investment Principles')).toBeInTheDocument();
      expect(screen.getByText('🎯 Value Investing')).toBeInTheDocument();
      expect(screen.getByText('🛡️ Margin of Safety')).toBeInTheDocument();
      expect(screen.getByText('📈 Quality Business')).toBeInTheDocument();
      expect(screen.getByText('💰 Cash Flow Focus')).toBeInTheDocument();
      expect(screen.getByText('🏰 Economic Moats')).toBeInTheDocument();
      expect(screen.getByText('⏰ Long-term Perspective')).toBeInTheDocument();
    });
  });

  it('displays quality metrics chart', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Business Quality Assessment')).toBeInTheDocument();
      expect(screen.getByText('Earnings Growth')).toBeInTheDocument();
      expect(screen.getByText('Return on Equity')).toBeInTheDocument();
      expect(screen.getByText('Debt Management')).toBeInTheDocument();
      expect(screen.getByText('Competitive Advantage')).toBeInTheDocument();
      expect(screen.getByText('Management Effectiveness')).toBeInTheDocument();
    });
  });

  it('displays investment disclaimer', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Investment Disclaimer:')).toBeInTheDocument();
      expect(screen.getByText(/This analysis is for educational purposes only/)).toBeInTheDocument();
    });
  });

  it('handles error state', async () => {
    (stockService.getFundamentalMetrics as any).mockRejectedValue(new Error('API Error'));
    
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load Buffett analysis data')).toBeInTheDocument();
    });
  });

  it('displays correct color for different recommendation types', async () => {
    // Test SELL recommendation
    const sellAnalysis = {
      ...mockBuffettAnalysis,
      investmentRecommendation: 'SELL',
      marginOfSafety: -15.0,
      qualityScore: 40.0,
      reasoning: ['Negative margin of safety (-15.0%)', 'Below average quality business (score: 40.0)']
    };

    (stockService.getBuffettAnalysis as any).mockResolvedValue(sellAnalysis);

    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      const sellBadge = screen.getByText('SELL');
      expect(sellBadge).toBeInTheDocument();
      expect(sellBadge).toHaveClass('bg-danger');
    });
  });

  it('displays quality score with appropriate color coding', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      const qualityScore = screen.getByText('85.5/100');
      expect(qualityScore).toBeInTheDocument();
      expect(qualityScore).toHaveClass('text-success'); // High score should be green
    });
  });

  it('calls API services with correct parameters', async () => {
    render(<BuffettAnalysis symbol="AAPL" />);

    await waitFor(() => {
      expect(stockService.getFundamentalMetrics).toHaveBeenCalledWith('AAPL');
      expect(stockService.getStockQuote).toHaveBeenCalledWith('AAPL');
    });
  });
});