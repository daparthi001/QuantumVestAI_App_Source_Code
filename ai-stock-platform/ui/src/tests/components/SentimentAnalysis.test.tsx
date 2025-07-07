/**
 * Sentiment Analysis Tests
 * Created: 2025-05-19 04:15:59
 * Author: daparthi001
 */
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SentimentAnalysis from '../../components/analysis/SentimentAnalysis';
import { stockService } from '../../services/api';

jest.mock('../../services/api', () => ({
    stockService: {
        getSentimentAnalysis: jest.fn()
    }
}));

// Mock Chart.js
jest.mock('react-chartjs-2', () => ({
    Line: () => null,
    Doughnut: () => null
}));

const mockSentimentData = {
    overallScore: 0.75,
    sources: {
        news: 0.8,
        social: 0.6,
        analyst: 0.7
    },
    historical: [
        { date: '2025-05-19', score: 0.75, volume: 1000 },
        { date: '2025-05-18', score: 0.72, volume: 950 }
    ],
    topMentions: [
        {
            source: 'Bloomberg',
            title: 'Company XYZ Exceeds Expectations',
            sentiment: 0.85,
            url: 'https://example.com/news/1',
            timestamp: '2025-05-19T04:15:59Z'
        }
    ]
};

describe('SentimentAnalysis Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        (stockService.getSentimentAnalysis as jest.Mock).mockResolvedValue({
            data: mockSentimentData
        });
    });

    it('renders loading state initially', () => {
        render(<SentimentAnalysis symbol="AAPL" />);
        expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('displays sentiment data after loading', async () => {
        render(<SentimentAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Market Sentiment - AAPL')).toBeInTheDocument();
            expect(screen.getByText('0.75')).toBeInTheDocument();
            expect(screen.getByText('Company XYZ Exceeds Expectations')).toBeInTheDocument();
        });
    });

    it('handles error state', async () => {
        (stockService.getSentimentAnalysis as jest.Mock).mockRejectedValue(
            new Error('Failed to load data')
        );

        render(<SentimentAnalysis symbol="AAPL" />);

        await waitFor(() => {
            expect(screen.getByText('Failed to load sentiment data')).toBeInTheDocument();
        });
    });

    it('formats sentiment scores correctly', async () => {
        render(<SentimentAnalysis symbol="AAPL" />);

        await waitFor(() => {
            const scoreElement = screen.getByText('0.75');
            expect(scoreElement).toHaveStyle({ color: '#28a745' });
        });
    });

    it('renders top mentions with correct links', async () => {
        render(<SentimentAnalysis symbol="AAPL" />);

        await waitFor(() => {
            const link = screen.getByText('Company XYZ Exceeds Expectations');
            expect(link).toHaveAttribute('href', 'https://example.com/news/1');
            expect(link).toHaveAttribute('target', '_blank');
            expect(link).toHaveAttribute('rel', 'noopener noreferrer');
        });
    });
});