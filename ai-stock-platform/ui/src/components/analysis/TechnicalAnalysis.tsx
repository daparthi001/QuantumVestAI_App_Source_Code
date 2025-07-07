/**
 * Technical Analysis Component
 * Created: 2025-05-19 04:09:47
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Spinner } from 'react-bootstrap';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { stockService } from '../../services/api';
import { formatPrice, formatDate } from '../../utils/formatters';

interface TechnicalIndicator {
    date: string;
    sma20: number;
    sma50: number;
    sma200: number;
    rsi: number;
    macd: number;
    macdSignal: number;
    macdHistogram: number;
    bollingerUpper: number;
    bollingerMiddle: number;
    bollingerLower: number;
}

interface TechnicalAnalysisProps {
    symbol: string;
    onIndicatorClick?: (indicator: string) => void;
}

const TechnicalAnalysis: React.FC<TechnicalAnalysisProps> = ({ symbol }) => {
    const [data, setData] = useState<TechnicalIndicator[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedIndicator, setSelectedIndicator] = useState<string>('sma');

    useEffect(() => {
        fetchTechnicalData();
    }, [symbol]);

    const fetchTechnicalData = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await stockService.getTechnicalIndicators(symbol);
            setData(response.data);
        } catch (err) {
            setError('Failed to load technical indicators');
            console.error('Error fetching technical data:', err);
        } finally {
            setLoading(false);
        }
    };

    const renderIndicatorChart = () => {
        if (!data.length) return null;

        switch (selectedIndicator) {
            case 'sma':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={data}>
                            <XAxis dataKey="date" tickFormatter={formatDate} />
                            <YAxis domain={['auto', 'auto']} />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="sma20" stroke="#8884d8" name="SMA 20" />
                            <Line type="monotone" dataKey="sma50" stroke="#82ca9d" name="SMA 50" />
                            <Line type="monotone" dataKey="sma200" stroke="#ffc658" name="SMA 200" />
                        </LineChart>
                    </ResponsiveContainer>
                );
            case 'macd':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={data}>
                            <XAxis dataKey="date" tickFormatter={formatDate} />
                            <YAxis domain={['auto', 'auto']} />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="macd" stroke="#8884d8" name="MACD" />
                            <Line type="monotone" dataKey="macdSignal" stroke="#82ca9d" name="Signal" />
                        </LineChart>
                    </ResponsiveContainer>
                );
            default:
                return null;
        }
    };

    const getSignalStrength = (value: number, type: string): string => {
        switch (type) {
            case 'rsi':
                if (value > 70) return 'Overbought';
                if (value < 30) return 'Oversold';
                return 'Neutral';
            case 'macd':
                if (value > 0) return 'Bullish';
                if (value < 0) return 'Bearish';
                return 'Neutral';
            default:
                return 'Neutral';
        }
    };

    return (
        <Card className="technical-analysis">
            <Card.Header>
                <h5 className="mb-0">Technical Analysis - {symbol}</h5>
            </Card.Header>
            <Card.Body>
                {loading ? (
                    <div className="text-center p-4">
                        <Spinner animation="border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </Spinner>
                    </div>
                ) : error ? (
                    <div className="alert alert-danger" role="alert">
                        {error}
                    </div>
                ) : (
                    <Row>
                        <Col lg={8}>
                            {renderIndicatorChart()}
                        </Col>
                        <Col lg={4}>
                            <Table striped bordered hover>
                                <thead>
                                    <tr>
                                        <th>Indicator</th>
                                        <th>Value</th>
                                        <th>Signal</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr onClick={() => setSelectedIndicator('rsi')}>
                                        <td>RSI (14)</td>
                                        <td>{formatPrice(data[data.length - 1]?.rsi)}</td>
                                        <td>{getSignalStrength(data[data.length - 1]?.rsi, 'rsi')}</td>
                                    </tr>
                                    <tr onClick={() => setSelectedIndicator('macd')}>
                                        <td>MACD</td>
                                        <td>{formatPrice(data[data.length - 1]?.macd)}</td>
                                        <td>{getSignalStrength(data[data.length - 1]?.macd, 'macd')}</td>
                                    </tr>
                                    <tr onClick={() => setSelectedIndicator('sma')}>
                                        <td>SMA Crossovers</td>
                                        <td>
                                            {data[data.length - 1]?.sma20 > data[data.length - 1]?.sma50 
                                                ? 'Golden Cross' 
                                                : 'Death Cross'}
                                        </td>
                                        <td>
                                            {data[data.length - 1]?.sma20 > data[data.length - 1]?.sma50 
                                                ? 'Bullish' 
                                                : 'Bearish'}
                                        </td>
                                    </tr>
                                </tbody>
                            </Table>
                        </Col>
                    </Row>
                )}
            </Card.Body>
        </Card>
    );
};

export default TechnicalAnalysis;