/**
 * Fundamental Analysis Component
 * Created: 2025-05-19 04:12:20
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Nav, Spinner, Alert } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { stockService } from '../../services/api';
import { formatNumber, formatCurrency, formatPercentage } from '../../utils/formatters';
import BuffettAnalysis from './BuffettAnalysis';

interface FundamentalMetrics {
    peRatio: number;
    eps: number;
    bookValue: number;
    dividendYield: number;
    marketCap: number;
    revenue: number;
    netIncome: number;
    operatingMargin: number;
    returnOnEquity: number;
    debtToEquity: number;
    currentRatio: number;
    quickRatio: number;
    freeCashFlow: number;
}

interface HistoricalMetrics {
    date: string;
    revenue: number;
    netIncome: number;
    eps: number;
}

interface FundamentalAnalysisProps {
    symbol: string;
}

const FundamentalAnalysis: React.FC<FundamentalAnalysisProps> = ({ symbol }) => {
    const [metrics, setMetrics] = useState<FundamentalMetrics | null>(null);
    const [historicalData, setHistoricalData] = useState<HistoricalMetrics[]>([]);
    const [activeTab, setActiveTab] = useState('overview');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchFundamentalData();
    }, [symbol]);

    const fetchFundamentalData = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const [metricsResponse, historicalResponse] = await Promise.all([
                stockService.getFundamentalMetrics(symbol),
                stockService.getHistoricalFundamentals(symbol)
            ]);

            setMetrics(metricsResponse.data);
            setHistoricalData(historicalResponse.data);
        } catch (err) {
            setError('Failed to load fundamental data');
            console.error('Error fetching fundamental data:', err);
        } finally {
            setLoading(false);
        }
    };

    const renderValuationMetrics = () => (
        <Table striped bordered hover>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Industry Avg</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>P/E Ratio</td>
                    <td>{formatNumber(metrics?.peRatio ?? 0)}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>EPS</td>
                    <td>{formatCurrency(metrics?.eps ?? 0)}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Book Value</td>
                    <td>{formatCurrency(metrics?.bookValue ?? 0)}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Dividend Yield</td>
                    <td>{formatPercentage(metrics?.dividendYield ?? 0)}</td>
                    <td>-</td>
                </tr>
            </tbody>
        </Table>
    );

    const renderFinancialMetrics = () => (
        <Table striped bordered hover>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>YoY Change</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Revenue</td>
                    <td>{formatCurrency(metrics?.revenue ?? 0)}</td>
                    <td>{formatPercentage(0.15)}</td>
                </tr>
                <tr>
                    <td>Net Income</td>
                    <td>{formatCurrency(metrics?.netIncome ?? 0)}</td>
                    <td>{formatPercentage(0.08)}</td>
                </tr>
                <tr>
                    <td>Operating Margin</td>
                    <td>{formatPercentage(metrics?.operatingMargin ?? 0)}</td>
                    <td>{formatPercentage(0.02)}</td>
                </tr>
                <tr>
                    <td>Return on Equity</td>
                    <td>{formatPercentage(metrics?.returnOnEquity ?? 0)}</td>
                    <td>{formatPercentage(0.03)}</td>
                </tr>
            </tbody>
        </Table>
    );

    const renderHistoricalChart = () => (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={historicalData}>
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="revenue" fill="#8884d8" name="Revenue" />
                <Bar yAxisId="right" dataKey="netIncome" fill="#82ca9d" name="Net Income" />
            </BarChart>
        </ResponsiveContainer>
    );

    return (
        <Card className="fundamental-analysis">
            <Card.Header>
                <h5 className="mb-0">Fundamental Analysis - {symbol}</h5>
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
                ) : (
                    <>
                        <Nav variant="tabs" className="mb-3">
                            <Nav.Item>
                                <Nav.Link
                                    active={activeTab === 'overview'}
                                    onClick={() => setActiveTab('overview')}
                                >
                                    Overview
                                </Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link
                                    active={activeTab === 'financials'}
                                    onClick={() => setActiveTab('financials')}
                                >
                                    Financials
                                </Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link
                                    active={activeTab === 'historical'}
                                    onClick={() => setActiveTab('historical')}
                                >
                                    Historical
                                </Nav.Link>
                            </Nav.Item>
                            <Nav.Item>
                                <Nav.Link
                                    active={activeTab === 'buffett'}
                                    onClick={() => setActiveTab('buffett')}
                                >
                                    Buffett Analysis
                                </Nav.Link>
                            </Nav.Item>
                        </Nav>

                        <Row>
                            <Col>
                                {activeTab === 'overview' && renderValuationMetrics()}
                                {activeTab === 'financials' && renderFinancialMetrics()}
                                {activeTab === 'historical' && renderHistoricalChart()}
                                {activeTab === 'buffett' && <BuffettAnalysis symbol={symbol} />}
                            </Col>
                        </Row>
                    </>
                )}
            </Card.Body>
        </Card>
    );
};

export default FundamentalAnalysis;