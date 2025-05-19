/**
 * Order Analytics Component
 * Created: 2025-05-19 04:53:30
 * Author: daparthi001
 */
import React, { useEffect, useState } from 'react';
import {
    Card,
    CardContent,
    Grid,
    Typography,
    Tab,
    Tabs,
    Box
} from '@mui/material';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    PieChart,
    Pie,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import { Order } from '../../types/order';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

interface OrderAnalyticsProps {
    orders: Order[];
}

export const OrderAnalytics: React.FC<OrderAnalyticsProps> = ({ orders }) => {
    const [activeTab, setActiveTab] = useState(0);
    const [analytics, setAnalytics] = useState({
        totalOrders: 0,
        fillRate: 0,
        averageExecutionTime: 0,
        orderTypeDistribution: [],
        dailyVolume: [],
        symbolBreakdown: []
    });

    useEffect(() => {
        calculateAnalytics();
    }, [orders]);

    const calculateAnalytics = () => {
        // Calculate basic metrics
        const filledOrders = orders.filter(o => o.status === 'FILLED');
        const fillRate = (filledOrders.length / orders.length) * 100;

        // Calculate order type distribution
        const typeDistribution = orders.reduce((acc, order) => {
            acc[order.orderType] = (acc[order.orderType] || 0) + 1;
            return acc;
        }, {});

        // Calculate daily volume
        const dailyVolume = orders.reduce((acc, order) => {
            const date = order.createdAt.split('T')[0];
            acc[date] = (acc[date] || 0) + (order.quantity * (order.price || 0));
            return acc;
        }, {});

        setAnalytics({
            totalOrders: orders.length,
            fillRate,
            averageExecutionTime: calculateAverageExecutionTime(orders),
            orderTypeDistribution: Object.entries(typeDistribution).map(([type, count]) => ({
                type,
                count
            })),
            dailyVolume: Object.entries(dailyVolume).map(([date, volume]) => ({
                date,
                volume
            })),
            symbolBreakdown: calculateSymbolBreakdown(orders)
        });
    };

    return (
        <div className="order-analytics">
            <Tabs
                value={activeTab}
                onChange={(_, newValue) => setActiveTab(newValue)}
                centered
            >
                <Tab label="Overview" />
                <Tab label="Performance" />
                <Tab label="Distribution" />
            </Tabs>

            {activeTab === 0 && (
                <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                        <MetricCard
                            title="Total Orders"
                            value={analytics.totalOrders}
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <MetricCard
                            title="Fill Rate"
                            value={formatPercentage(analytics.fillRate)}
                        />
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <MetricCard
                            title="Avg. Execution Time"
                            value={`${analytics.averageExecutionTime.toFixed(2)}s`}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <VolumeChart data={analytics.dailyVolume} />
                    </Grid>
                </Grid>
            )}

            {activeTab === 1 && (
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <PerformanceMetrics orders={orders} />
                    </Grid>
                </Grid>
            )}

            {activeTab === 2 && (
                <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                        <OrderTypeDistribution data={analytics.orderTypeDistribution} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <SymbolBreakdown data={analytics.symbolBreakdown} />
                    </Grid>
                </Grid>
            )}
        </div>
    );
};

// Helper components
const MetricCard: React.FC<{ title: string; value: string | number }> = ({
    title,
    value
}) => (
    <Card>
        <CardContent>
            <Typography color="textSecondary" gutterBottom>
                {title}
            </Typography>
            <Typography variant="h5">{value}</Typography>
        </CardContent>
    </Card>
);

const VolumeChart: React.FC<{ data: any[] }> = ({ data }) => (
    <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="volume" stroke="#8884d8" />
        </LineChart>
    </ResponsiveContainer>
);