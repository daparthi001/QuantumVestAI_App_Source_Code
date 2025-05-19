/**
 * Sentiment Analysis Component
 * Created: 2025-05-19 04:15:59
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, Spinner, Alert } from 'react-bootstrap';
import { Line, Doughnut } from 'react-chartjs-2';
import { stockService } from '../../services/api';
import { formatDate, formatNumber } from '../../utils/formatters';

interface SentimentData {
    overallScore: number;
    sources: {
        news: number;
        social: number;
        analyst: number;
    };
    historical: Array<{
        date: string;
        score: number;
        volume: number;
    }>;
    topMentions: Array<{
        source: string;
        title: string;
        sentiment: number;
        url: string;
        timestamp: string;
    }>;
}

interface SentimentAnalysisProps {
    symbol: string;
    timeframe?: 'day' | 'week' | 'month';
}

const SentimentAnalysis: React.FC<SentimentAnalysisProps> = ({ 
    symbol, 
    timeframe = 'week' 
}) => {
    const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSentimentData();
    }, [symbol, timeframe]);

    const fetchSentimentData = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await stockService.getSentimentAnalysis(symbol, timeframe);
            setSentimentData(response.data);
        } catch (err) {
            setError('Failed to load sentiment data');
            console.error('Error fetching sentiment data:', err);
        } finally {
            setLoading(false);
        }
    };

    const getSentimentColor = (score: number): string => {
        if (score >= 0.6) return '#28a745';
        if (score >= 0.4) return '#ffc107';
        return '#dc3545';
    };

    const renderSentimentGauge = () => {
        if (!sentimentData) return null;

        const data = {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [
                    sentimentData.sources.news,
                    sentimentData.sources.social,
                    sentimentData.sources.analyst
                ],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                borderWidth: 0
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom' as const
                }
            }
        };

        return (
            <div style={{ height: '200px' }}>
                <Doughnut data={data} options={options} />
            </div>
        );
    };

    const renderSentimentTrend = () => {
        if (!sentimentData?.historical) return null;

        const data = {
            labels: sentimentData.historical.map(h => formatDate(h.date)),
            datasets: [
                {
                    label: 'Sentiment Score',
                    data: sentimentData.historical.map(h => h.score),
                    borderColor: '#0d6efd',
                    tension: 0.1
                }
            ]
        };

        const options = {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            }
        };

        return <Line data={data} options={options} />;
    };

    return (
        <Card className="sentiment-analysis">
            <Card.Header>
                <h5 className="mb-0">Market Sentiment - {symbol}</h5>
            </Card.Header>
            <Card.Body>
                {loading ? (
                    <div className="text-center p-4">
                        <Spinner animation="border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </Spinner>
                    </div>
                ) : error ? (
                    <Alert variant="danger">{error}</Alert>
                ) : sentimentData && (
                    <Row>
                        <Col lg={4}>
                            <div className="sentiment-score-card">
                                <h6>Overall Sentiment Score</h6>
                                <div 
                                    className="score-value"
                                    style={{ color: getSentimentColor(sentimentData.overallScore) }}
                                >
                                    {formatNumber(sentimentData.overallScore)}
                                </div>
                                {renderSentimentGauge()}
                            </div>
                        </Col>
                        <Col lg={8}>
                            <div className="sentiment-trend">
                                <h6>Sentiment Trend</h6>
                                {renderSentimentTrend()}
                            </div>
                        </Col>
                        <Col xs={12} className="mt-4">
                            <h6>Top Mentions</h6>
                            <div className="mentions-container">
                                {sentimentData.topMentions.map((mention, index) => (
                                    <div key={index} className="mention-card">
                                        <div className="d-flex justify-content-between align-items-start">
                                            <h6 className="mention-title">
                                                <a 
                                                    href={mention.url} 
                                                    target="_blank" 
                                                    rel="noopener noreferrer"
                                                >
                                                    {mention.title}
                                                </a>
                                            </h6>
                                            <Badge 
                                                bg={getSentimentColor(mention.sentiment) === '#28a745' ? 'success' : 
                                                   getSentimentColor(mention.sentiment) === '#ffc107' ? 'warning' : 'danger'}
                                            >
                                                {formatNumber(mention.sentiment)}
                                            </Badge>
                                        </div>
                                        <div className="mention-meta">
                                            <span className="source">{mention.source}</span>
                                            <span className="timestamp">
                                                {formatDate(mention.timestamp)}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Col>
                    </Row>
                )}
            </Card.Body>
        </Card>
    );
};

export default SentimentAnalysis;