/**
 * Order Analytics Component
 * Created: 2025-05-19 04:53:30
 * Author: daparthi001
 */
import React, { useEffect, useState } from 'react';
import {
    Card,
    CardContent,
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
import { formatPercentage } from '../../utils/formatters';

interface OrderAnalyticsProps {
    orders: Order[];
}

interface OrderDistribution {
    type: string;
    count: number;
}

interface DailyVolume {
    date: string;
    volume: number;
}

interface SymbolBreakdown {
    symbol: string;
    count: number;
    percentage: number;
}

interface AnalyticsData {
    totalOrders: number;
    fillRate: number;
    averageExecutionTime: number;
    orderTypeDistribution: OrderDistribution[];
    dailyVolume: DailyVolume[];
    symbolBreakdown: SymbolBreakdown[];
}

interface PerformanceMetricsProps {
    orders: Order[];
}

export const OrderAnalytics: React.FC<OrderAnalyticsProps> = ({ orders }) => {
    const [activeTab, setActiveTab] = useState(0);
    const [analytics, setAnalytics] = useState<AnalyticsData>({
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
        const typeDistribution = orders.reduce((acc: Record<string, number>, order) => {
            acc[order.orderType] = (acc[order.orderType] || 0) + 1;
            return acc;
        }, {});

        // Calculate daily volume
        const dailyVolume = orders.reduce((acc: Record<string, number>, order) => {
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
                    <Grid size={{ xs: 12, md: 4 }}>

                        <MetricCard
                            title="Total Orders"
                            value={analytics.totalOrders}
                        />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                        <MetricCard
                            title="Fill Rate"
                            value={formatPercentage(analytics.fillRate)}
                        />
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>

                        <MetricCard
                            title="Avg. Execution Time"
                            value={`${analytics.averageExecutionTime.toFixed(2)}s`}
                        />
                    </Grid>
                    <Grid size={{ xs: 12 }}>
                        <VolumeChart data={analytics.dailyVolume} />
                    </Grid>
                </Grid>
            )}

            {activeTab === 1 && (
                <Grid container spacing={2}>
                    <Grid size={{ xs: 12 }}>
                        <PerformanceMetrics orders={orders} />
                    </Grid>
                </Grid>
            )}

            {activeTab === 2 && (
                <Grid container spacing={2}>
                    <Grid size={{ xs: 12, md: 6 }}>
                        <OrderTypeDistribution data={analytics.orderTypeDistribution} />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6 }}>
                        <SymbolBreakdown data={analytics.symbolBreakdown} />
                    </Grid>
                </Grid>
            )}
        </div>
    );
};

// PerformanceMetrics Component
interface PerformanceMetricsProps {
    orders: Order[];
}

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ orders }) => {
    const metrics = React.useMemo(() => {
        const totalOrders = orders.length;
        const filledOrders = orders.filter(order => order.status === 'FILLED').length;
        const avgExecutionTime = orders.reduce((sum, order) => {
            return sum + (order.executionTime ? new Date(order.executionTime).getTime() - new Date(order.createdAt).getTime() : 0);
        }, 0) / totalOrders / 1000; // Convert to seconds

        return {
            totalOrders,
            fillRate: totalOrders > 0 ? filledOrders / totalOrders : 0,
            avgExecutionTime: avgExecutionTime || 0,
            successRate: totalOrders > 0 ? filledOrders / totalOrders : 0
        };
    }, [orders]);

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Performance Metrics
                </Typography>
                <Grid container spacing={2}>
                    <Grid size={{ xs: 6, md: 3 }}>
                        <Typography variant="subtitle2">Total Orders</Typography>
                        <Typography variant="h4">{metrics.totalOrders}</Typography>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                        <Typography variant="subtitle2">Fill Rate</Typography>
                        <Typography variant="h4">{(metrics.fillRate * 100).toFixed(1)}%</Typography>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                        <Typography variant="subtitle2">Avg Execution</Typography>
                        <Typography variant="h4">{metrics.avgExecutionTime.toFixed(2)}s</Typography>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                        <Typography variant="subtitle2">Success Rate</Typography>
                        <Typography variant="h4">{(metrics.successRate * 100).toFixed(1)}%</Typography>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
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

// Helper functions
function calculateAverageExecutionTime(orders: Order[]): number {
    const executedOrders = orders.filter(order => order.executedPrice && order.executionTime);
    if (executedOrders.length === 0) return 0;
    
    const totalTime = executedOrders.reduce((sum, order) => {
        const execTime = new Date(order.executionTime!).getTime();
        const createTime = new Date(order.createdAt).getTime();
        return sum + (execTime - createTime);
    }, 0);
    
    return totalTime / executedOrders.length;
}

function calculateSymbolBreakdown(orders: Order[]) {
    const breakdown: Record<string, number> = {};
    orders.forEach(order => {
        breakdown[order.symbol] = (breakdown[order.symbol] || 0) + 1;
    });
    
    return Object.entries(breakdown).map(([symbol, count]) => ({
        symbol,
        count,
        percentage: (count / orders.length) * 100
    }));
}

// Component types
const OrderTypeDistribution: React.FC<{ data: any[] }> = ({ data }) => (
    <ResponsiveContainer width="100%" height={300}>
        <PieChart>
            <Pie dataKey="count" data={data} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" />
            <Tooltip />
        </PieChart>
    </ResponsiveContainer>
);

const SymbolBreakdown: React.FC<{ data: any[] }> = ({ data }) => (
    <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
            <XAxis dataKey="symbol" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
    </ResponsiveContainer>
);

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ orders }) => {
    const performanceData = React.useMemo(() => {
        const executedOrders = orders.filter(order => order.status === 'FILLED');
        const totalLatency = executedOrders.reduce((sum, order) => {
            if (order.executionTime) {
                const execTime = new Date(order.executionTime).getTime();
                const createTime = new Date(order.createdAt).getTime();
                return sum + (execTime - createTime);
            }
            return sum;
        }, 0);

        return {
            averageLatency: executedOrders.length > 0 ? totalLatency / executedOrders.length : 0,
            executionRate: orders.length > 0 ? (executedOrders.length / orders.length) * 100 : 0,
            totalExecuted: executedOrders.length,
            totalOrders: orders.length
        };
    }, [orders]);

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Performance Metrics
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Box sx={{ flex: '1 1 250px' }}>
                        <Typography variant="body2" color="textSecondary">
                            Average Latency
                        </Typography>
                        <Typography variant="h5">
                            {performanceData.averageLatency.toFixed(2)}ms
                        </Typography>
                    </Box>
                    <Box sx={{ flex: '1 1 250px' }}>
                        <Typography variant="body2" color="textSecondary">
                            Execution Rate
                        </Typography>
                        <Typography variant="h5">
                            {performanceData.executionRate.toFixed(1)}%
                        </Typography>
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );
};