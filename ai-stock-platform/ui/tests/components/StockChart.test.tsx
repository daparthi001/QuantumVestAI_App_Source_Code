/**
 * Stock Chart Component Tests
 * Created: 2025-05-19 03:49:42
 * Author: daparthi001
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StockChart from '../../components/StockChart';
import { StockService } from '../../services/StockService';
import { mockHistoricalData } from '../mocks/stockData';

// Mock the stock service
jest.mock('../../services/StockService');

describe('StockChart Component', () => {
    beforeEach(() => {
        // Reset all mocks before each test
        jest.clearAllMocks();
        
        // Mock the service methods
        (StockService.getHistoricalPrices as jest.Mock).mockResolvedValue(mockHistoricalData);
    });

    it('renders chart with historical data', async () => {
        // Render component
        render(
            <StockChart 
                symbol="AAPL"
                interval="1d"
                chartType="candlestick"
            />
        );

        // Wait for data to load
        await waitFor(() => {
            expect(screen.getByTestId('stock-chart')).toBeInTheDocument();
        });

        // Verify service was called
        expect(StockService.getHistoricalPrices).toHaveBeenCalledWith(
            'AAPL',
            expect.any(String),
            expect.any(String),
            '1d'
        );
    });

    it('handles interval changes', async () => {
        // Render component
        render(
            <StockChart 
                symbol="AAPL"
                interval="1d"
                chartType="candlestick"
            />
        );

        // Change interval
        const intervalSelect = screen.getByTestId('interval-select');
        fireEvent.change(intervalSelect, { target: { value: '1wk' } });

        // Verify service was called with new interval
        await waitFor(() => {
            expect(StockService.getHistoricalPrices).toHaveBeenCalledWith(
                'AAPL',
                expect.any(String),
                expect.any(String),
                '1wk'
            );
        });
    });

    it('handles chart type changes', async () => {
        // Render component
        render(
            <StockChart 
                symbol="AAPL"
                interval="1d"
                chartType="candlestick"
            />
        );

        // Change chart type
        const typeSelect = screen.getByTestId('chart-type-select');
        fireEvent.change(typeSelect, { target: { value: 'line' } });

        // Verify chart type updated
        await waitFor(() => {
            const chart = screen.getByTestId('stock-chart');
            expect(chart).toHaveAttribute('data-chart-type', 'line');
        });
    });

    it('handles loading state', async () => {
        // Mock delayed response
        (StockService.getHistoricalPrices as jest.Mock).mockImplementation(
            () => new Promise(resolve => setTimeout(() => resolve(mockHistoricalData), 1000))
        );

        // Render component
        render(
            <StockChart 
                symbol="AAPL"
                interval="1d"
                chartType="candlestick"
            />
        );

        // Verify loading state
        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

        // Wait for data to load
        await waitFor(() => {
            expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
            expect(screen.getByTestId('stock-chart')).toBeInTheDocument();
        });
    });

    it('handles error state', async () => {
        // Mock error response
        (StockService.getHistoricalPrices as jest.Mock).mockRejectedValue(
            new Error('Failed to fetch data')
        );

        // Render component
        render(
            <StockChart 
                symbol="AAPL"
                interval="1d"
                chartType="candlestick"
            />
        );

        // Verify error state
        await waitFor(() => {
            expect(screen.getByTestId('error-message')).toBeInTheDocument();
            expect(screen.getByText('Failed to fetch data')).toBeInTheDocument();
        });
    });
});