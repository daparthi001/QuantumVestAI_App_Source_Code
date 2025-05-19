/**
 * Detailed Metrics Component
 * Created: 2025-05-19 05:04:13
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import {
    Paper,
    Typography,
    Tabs,
    Tab,
    Box,
    CircularProgress,
    Alert
} from '@mui/material';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import { PerformanceMonitor } from '../../services/monitoring/PerformanceMonitor';
import { usePerformanceTracking } from '../../hooks/usePerformanceTracking';

interface MetricDetail {
    timestamp: number;
    value: number;
    category: string;
}

interface MetricBreakdown {
    category: string;
    min: number;
    max: number;
    avg: number;
    p95: number;
    count: number;
}

export const DetailedMetrics: React.FC<{
    metricName: string;
    interval?: 'minute' | 'hour' | 'day';
}> = ({ metricName, interval = 'minute' }) => {
    const [activeTab, setActiveTab] = useState(0);
    const [timeseriesData, setTimeseriesData] = useState<MetricDetail[]>([]);
    const [breakdown, setBreakdown] = useState<MetricBreakdown[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { trackInteraction } = usePerformanceTracking('DetailedMetrics');

    useEffect(() => {
        const fetchMetricDetails = async () => {
            setLoading(true);
            setError(null);
            try {
                const monitor = PerformanceMonitor.getInstance();
                const data = await monitor.getMetricDetails(metricName, interval);
                setTimeseriesData(data.timeseries);
                setBreakdown(data.breakdown);
                trackInteraction('fetch_metric_details');
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch metric details');
            } finally {
                setLoading(false);
            }
        };

        fetchMetricDetails();
        
        // Set up real-time updates
        const updateInterval = interval === 'minute' ? 5000 : 30000;
        const intervalId = setInterval(fetchMetricDetails, updateInterval);

        return () => clearInterval(intervalId);
    }, [metricName, interval]);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ m: 2 }}>
                {error}
            </Alert>
        );
    }

    return (
        <Paper className="detailed-metrics">
            <Typography variant="h6" gutterBottom>
                {metricName} Metrics
            </Typography>

            <Tabs
                value={activeTab}
                onChange={(_, newValue) => setActiveTab(newValue)}
                sx={{ mb: 2 }}
            >
                <Tab label="Timeline" />
                <Tab label="Breakdown" />
                <Tab label="Analysis" />
            </Tabs>

            {activeTab === 0 && (
                <Box height={400}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={timeseriesData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                                dataKey="timestamp"
                                tickFormatter={(timestamp) => 
                                    new Date(timestamp).toLocaleTimeString()
                                }
                            />
                            <YAxis />
                            <Tooltip
                                labelFormatter={(timestamp) => 
                                    new Date(timestamp).toLocaleString()
                                }
                            />
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke="#8884d8"
                                fill="#8884d8"
                                fillOpacity={0.3}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </Box>
            )}

            {activeTab === 1 && (
                <MetricBreakdownTable data={breakdown} />
            )}

            {activeTab === 2 && (
                <MetricAnalysis
                    metricName={metricName}
                    timeseriesData={timeseriesData}
                    breakdown={breakdown}
                />
            )}
        </Paper>
    );
};

const MetricBreakdownTable: React.FC<{ data: MetricBreakdown[] }> = ({ data }) => (
    <Table>
        <TableHead>
            <TableRow>
                <TableCell>Category</TableCell>
                <TableCell>Min</TableCell>
                <TableCell>Max</TableCell>
                <TableCell>Average</TableCell>
                <TableCell>P95</TableCell>
                <TableCell>Count</TableCell>
            </TableRow>
        </TableHead>
        <TableBody>
            {data.map((row) => (
                <TableRow key={row.category}>
                    <TableCell>{row.category}</TableCell>
                    <TableCell>{row.min.toFixed(2)}</TableCell>
                    <TableCell>{row.max.toFixed(2)}</TableCell>
                    <TableCell>{row.avg.toFixed(2)}</TableCell>
                    <TableCell>{row.p95.toFixed(2)}</TableCell>
                    <TableCell>{row.count}</TableCell>
                </TableRow>
            ))}
        </TableBody>
    </Table>
);