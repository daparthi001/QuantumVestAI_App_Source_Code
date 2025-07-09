/**
 * Stock Ticker Component
 * Created: 2025-05-19 04:08:26
 * Author: daparthi001
 */
import React, { useEffect, useState } from 'react';
import { Card, Table, Badge } from 'react-bootstrap';
import wsService from '../services/websocket.service';
import { formatPrice, formatChange } from '../utils/formatters';

interface StockPrice {
    symbol: string;
    price: number;
    change: number;
    changePercent: number;
    timestamp: string;
}

interface StockTickerProps {
    symbols: string[];
    onSelect?: (symbol: string) => void;
}

const StockTicker: React.FC<StockTickerProps> = ({ symbols, onSelect }) => {
    const [prices, setPrices] = useState<Map<string, StockPrice>>(new Map());
    const [updates, setUpdates] = useState<Map<string, boolean>>(new Map());

    useEffect(() => {
        // Subscribe to symbols
        symbols.forEach(symbol => {
            wsService.subscribeSymbol(symbol);
        });

        // Handle real-time updates
        const subscription = wsService.onMessage().subscribe(message => {
            if (message.type === 'price_update') {
                setPrices(prev => {
                    const newPrices = new Map(prev);
                    newPrices.set(message.data.symbol, message.data);
                    return newPrices;
                });

                // Flash animation trigger
                setUpdates(prev => {
                    const newUpdates = new Map(prev);
                    newUpdates.set(message.data.symbol, true);
                    setTimeout(() => {
                        setUpdates(prev => {
                            const latest = new Map(prev);
                            latest.delete(message.data.symbol);
                            return latest;
                        });
                    }, 1000);
                    return newUpdates;
                });
            }
        });

        // Cleanup
        return () => {
            subscription.unsubscribe();
            symbols.forEach(symbol => {
                wsService.unsubscribeSymbol(symbol);
            });
        };
    }, [symbols]);

    return (
        <Card className="stock-ticker">
            <Card.Header>
                <h5 className="mb-0">Market Watch</h5>
            </Card.Header>
            <Card.Body className="p-0">
                <Table hover className="mb-0">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Price</th>
                            <th>Change</th>
                            <th>% Change</th>
                        </tr>
                    </thead>
                    <tbody>
                        {symbols.map(symbol => {
                            const data = prices.get(symbol);
                            const isUpdating = updates.get(symbol);
                            
                            return (
                                <tr
                                    key={symbol}
                                    className={`${isUpdating ? 'price-update' : ''}`}
                                    onClick={() => onSelect?.(symbol)}
                                    style={{ cursor: onSelect ? 'pointer' : 'default' }}
                                >
                                    <td>{symbol}</td>
                                    <td>{data ? formatPrice(data.price) : '-'}</td>
                                    <td>
                                        {data && (
                                            <Badge bg={data.change >= 0 ? 'success' : 'danger'}>
                                                {formatChange(data.change)}
                                            </Badge>
                                        )}
                                    </td>
                                    <td>
                                        {data && (
                                            <Badge bg={data.changePercent >= 0 ? 'success' : 'danger'}>
                                                {formatChange(data.changePercent)}%
                                            </Badge>
                                        )}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </Table>
            </Card.Body>
        </Card>
    );
};

export default StockTicker;