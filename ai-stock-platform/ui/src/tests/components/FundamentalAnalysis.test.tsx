/**
 * Fundamental Analysis Tests
 * Created: 2025-05-19 04:12:20
 * Author: daparthi001
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FundamentalAnalysis from '../../components/analysis/FundamentalAnalysis';
import { stockService } from '../../services/api';

jest.mock('../../services/api', () => ({
    stockService: {
        getFundamentalMetrics: jest.fn(),
        getHistoricalFundamentals: jest.fn()
    }
}));

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
});