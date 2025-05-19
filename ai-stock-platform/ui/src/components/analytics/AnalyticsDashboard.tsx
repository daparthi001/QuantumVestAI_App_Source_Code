/**
 * Analytics Dashboard Component
 * Created: 2025-05-19 05:02:53
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import {
    Grid,
    Paper,
    Typography,
    Select,
    MenuItem,
    FormControl,
    InputLabel
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
import { OrderAnalytics } from '../../services/analytics/OrderAnalytics';
import { usePerformanceTracking } from '../../hooks/usePerformanceTracking';

interface MetricsData {
    orderVolume: any[];
    executionRates: any[];
    orderTypes: any[];
    performanceMetrics: any;
}

export const AnalyticsDashboard: React.FC = () => {
    const [timeframe, setTimeframe] = useState<'day' | 'week' | 'month'>('day');
    const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
    const [loading, setLoading] = useState(true);
    const analytics = OrderAnalytics.getInstance();
    const { trackInteraction } = usePerformanceTracking('AnalyticsDashboard');

    useEffect(() => {
        const fetchMetrics = async () => {
            setLoading(true);
            try {
                const data = await analytics.getOrderMetrics(timeframe);
                setMetricsData(data);
                trackInteraction('fetch_metrics');
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
    }, [timeframe]);

    if (loading || !metricsData) {
        return <div>Loading analytics...</div>;
    }

    return (
        <div className="analytics-dashboard">
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Paper className="analytics-header">
                        <Typography variant="h5">Order Analytics</Typography>
                        <FormControl>
                            <InputLabel>Timeframe</InputLabel>
                            <Select
                                value={timeframe}
                                onChange={(e) => setTimeframe(e.target.value as any)}
                            >
                                <MenuItem value="day">Last 24 Hours</MenuItem>
                                <MenuItem value="week">Last Week</MenuItem>
                                <MenuItem value="month">Last Month</MenuItem>
                            </Select>
                        </FormControl>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper className="analytics-card">
                        <Typography variant="h6">Order Volume</Typography>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={metricsData.orderVolume}>
                                <XAxis dataKey="time" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="volume"
                                    stroke="#8884d8"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper className="analytics-card">
                        <Typography variant="h6">Execution Rates</Typography>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={metricsData.executionRates}>
                                <XAxis dataKey="type" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="rate" fill="#82ca9d" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper className="analytics-card">
                        <Typography variant="h6">Order Types Distribution</Typography>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={metricsData.orderTypes}
                                    dataKey="value"
                                    nameKey="type"
                                    fill="#8884d8"
                                />
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper className="analytics-card performance-metrics">
                        <Typography variant="h6">Performance Metrics</Typography>
                        <div className="metrics-grid">
                            <MetricCard
                                title="Average Execution Time"
                                value={`${metricsData.performanceMetrics.avgExecutionTime}ms`}
                            />
                            <MetricCard
                                title="Success Rate"
                                value={`${metricsData.performanceMetrics.successRate}%`}
                            />
                            <MetricCard
                                title="Fill Rate"
                                value={`${metricsData.performanceMetrics.fillRate}%`}
                            />
                            <MetricCard
                                title="Rejection Rate"
                                value={`${metricsData.performanceMetrics.rejectionRate}%`}
                            />
                        </div>
                    </Paper>
                </Grid>
            </Grid>
        </div>
    );
};

const MetricCard: React.FC<{ title: string; value: string }> = ({
    title,
    value
}) => (
    <div className="metric-card">
        <Typography variant="subtitle2" color="textSecondary">
            {title}
        </Typography>
        <Typography variant="h4">{value}</Typography>
    </div>
);