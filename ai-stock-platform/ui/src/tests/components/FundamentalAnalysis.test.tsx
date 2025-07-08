/**
 * Fundamental Analysis Tests
 * Created: 2025-05-19 04:12:20
 * Author: daparthi001
 * Updated: 2025-01-09 (AI Assistant) - Added Buffett analysis tab tests
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FundamentalAnalysis from '../../components/analysis/FundamentalAnalysis';
import { stockService } from '../../services/api';

jest.mock('../../services/api', () => ({
    stockService: {
        getFundamentalMetrics: jest.fn(),
        getHistoricalFundamentals: jest.fn(),
        getStockQuote: jest.fn()
    }
}));

// Mock the BuffettAnalysis component
jest.mock('../../components/analysis/BuffettAnalysis', () => {
    return function MockBuffettAnalysis({ symbol }: { symbol: string }) {
        return <div data-testid="buffett-analysis">Buffett Analysis for {symbol}</div>;
    };
});

const mockMetrics = {
    peRatio: 25.4,
    eps: 3.75,
    bookValue: 45.67,
    dividendYield: 0.015,
    marketCap: 2000000000000,
    revenue: 365000000000,
    netIncome: 94000000000,
    operatingMargin: 0.30,
    returnOnEquity: 0.35,
    debtToEquity: 1.2,
    currentRatio: 1.5,
    quickRatio: 1.2,
    freeCashFlow: 92000000000
};

const mockHistoricalData = [
    {
        date: '2024',
        revenue: 365000000000,
        netIncome: 94000000000,
        eps: 3.75
    },
    {
        date: '2023',
        revenue: 320000000000,
        netIncome: 85000000000,
        eps: 3.25
    }
];

describe('FundamentalAnalysis Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        (stockService.getFundamentalMetrics as jest.Mock).mockResolvedValue({ data: mockMetrics });
        (stockService.getHistoricalFundamentals as jest.Mock).mockResolvedValue({ data: mockHistoricalData });
        (stockService.getStockQuote as jest.Mock).mockResolvedValue({ 
            symbol: 'AAPL', 
            price: 150.00, 
            change: 2.50, 
            changePercent: 1.67 
        });
    });

    it('renders loading state initially', () => {
        render(<FundamentalAnalysis symbol="AAPL" />);
        expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('displays fundamental metrics after loading', async () => {
        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('P/E Ratio')).toBeInTheDocument();
            expect(screen.getByText('25.4')).toBeInTheDocument();
        });
    });

    it('switches between tabs correctly', async () => {
        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Overview')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('Financials'));
        expect(screen.getByText('Operating Margin')).toBeInTheDocument();

        fireEvent.click(screen.getByText('Historical'));
        expect(screen.getByText('Revenue')).toBeInTheDocument();
    });

    it('handles error state', async () => {
        (stockService.getFundamentalMetrics as jest.Mock).mockRejectedValue(
            new Error('Failed to load data')
        );

        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Failed to load fundamental data')).toBeInTheDocument();
        });
    });

    it('formats numbers correctly', async () => {
        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('1.50%')).toBeInTheDocument(); // Dividend Yield
            expect(screen.getByText('$3.75')).toBeInTheDocument(); // EPS
        });
    });

    it('displays Buffett Analysis tab', async () => {
        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Buffett Analysis')).toBeInTheDocument();
        });
    });

    it('switches to Buffett Analysis tab when clicked', async () => {
        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            const buffettTab = screen.getByText('Buffett Analysis');
            fireEvent.click(buffettTab);
        });

        await waitFor(() => {
            expect(screen.getByTestId('buffett-analysis')).toBeInTheDocument();
            expect(screen.getByText('Buffett Analysis for AAPL')).toBeInTheDocument();
        });
    });

    it('displays all four navigation tabs', async () => {
        render(<FundamentalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Overview')).toBeInTheDocument();
            expect(screen.getByText('Financials')).toBeInTheDocument();
            expect(screen.getByText('Historical')).toBeInTheDocument();
            expect(screen.getByText('Buffett Analysis')).toBeInTheDocument();
        });
    });
});