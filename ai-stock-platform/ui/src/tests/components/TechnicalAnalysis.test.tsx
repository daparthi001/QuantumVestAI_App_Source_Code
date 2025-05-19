/**
 * Technical Analysis Component Tests
 * Created: 2025-05-19 04:09:47
 * Author: daparthi001
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TechnicalAnalysis from '../../components/analysis/TechnicalAnalysis';
import { stockService } from '../../services/api';

// Mock the stock service
jest.mock('../../services/api', () => ({
    stockService: {
        getTechnicalIndicators: jest.fn()
    }
}));

const mockData = {
    data: [
        {
            date: '2025-05-19T04:09:47Z',
            sma20: 150.5,
            sma50: 148.3,
            sma200: 145.7,
            rsi: 65.4,
            macd: 2.3,
            macdSignal: 1.8,
            macdHistogram: 0.5,
            bollingerUpper: 152.5,
            bollingerMiddle: 150.0,
            bollingerLower: 147.5
        }
    ]
};

describe('TechnicalAnalysis Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders loading state initially', () => {
        render(<TechnicalAnalysis symbol="AAPL" />);
        expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('displays technical indicators after loading', async () => {
        (stockService.getTechnicalIndicators as jest.Mock).mockResolvedValue(mockData);

        render(<TechnicalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Technical Analysis - AAPL')).toBeInTheDocument();
        });

        expect(screen.getByText('RSI (14)')).toBeInTheDocument();
        expect(screen.getByText('MACD')).toBeInTheDocument();
        expect(screen.getByText('SMA Crossovers')).toBeInTheDocument();
    });

    it('handles error state', async () => {
        (stockService.getTechnicalIndicators as jest.Mock).mockRejectedValue(
            new Error('Failed to load data')
        );

        render(<TechnicalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Failed to load technical indicators')).toBeInTheDocument();
        });
    });

    it('updates selected indicator on click', async () => {
        (stockService.getTechnicalIndicators as jest.Mock).mockResolvedValue(mockData);

        render(<TechnicalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('MACD')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('MACD'));

        expect(screen.getByText('Signal')).toBeInTheDocument();
    });

    it('calculates signal strength correctly', async () => {
        (stockService.getTechnicalIndicators as jest.Mock).mockResolvedValue({
            data: [
                {
                    ...mockData.data[0],
                    rsi: 75, // Overbought
                    macd: -1.5 // Bearish
                }
            ]
        });

        render(<TechnicalAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Overbought')).toBeInTheDocument();
            expect(screen.getByText('Bearish')).toBeInTheDocument();
        });
    });
});