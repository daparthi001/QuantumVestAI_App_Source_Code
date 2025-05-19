/**
 * Performance Report Component
 * Created: 2025-05-19 05:02:53
 * Author: daparthi001
 */
import React, { useState } from 'react';
import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import { DateRangePicker } from '@mui/lab';
import { PerformanceMonitor } from '../../services/monitoring/PerformanceMonitor';
import { formatDuration, formatPercentage } from '../../utils/formatters';

interface PerformanceData {
    componentMetrics: Array<{
        name: string;
        averageRenderTime: number;
        p95RenderTime: number;
        rerenders: number;
    }>;
    operationMetrics: Array<{
        name: string;
        averageTime: number;
        errorRate: number;
        count: number;
    }>;
    apiMetrics: Array<{
        endpoint: string;
        averageResponseTime: number;
        errorRate: number;
        callCount: number;
    }>;
}

export const PerformanceReport: React.FC = () => {
    const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([
        null,
        null
    ]);
    const [performanceData, setPerformanceData] = useState<PerformanceData | null>(
        null
    );
    const [isExporting, setIsExporting] = useState(false);
    const [showDetailDialog, setShowDetailDialog] = useState(false);
    const [selectedMetric, setSelectedMetric] = useState<any>(null);

    const handleGenerateReport = async () => {
        if (!dateRange[0] || !dateRange[1]) return;

        try {
            const monitor = PerformanceMonitor.getInstance();
            const data = await monitor.generateReport(dateRange[0], dateRange[1]);
            setPerformanceData(data);
        } catch (error) {
            console.error('Failed to generate report:', error);
        }
    };

    const handleExportReport = async () => {
        if (!performanceData) return;

        setIsExporting(true);
        try {
            const csvContent = generateCSVReport(performanceData);
            downloadCSV(csvContent, `performance-report-${Date.now()}.csv`);
        } finally {
            setIsExporting(false);
        }
    };

    const handleMetricClick = (metric: any) => {
        setSelectedMetric(metric);
        setShowDetailDialog(true);
    };

    return (
        <div className="performance-report">
            <Paper className="report-controls">
                <Typography variant="h6">Performance Report</Typography>
                <DateRangePicker
                    value={dateRange}
                    onChange={(newValue) => setDateRange(newValue)}
                    renderInput={(startProps, endProps) => (
                        <>
                            <TextField {...startProps} />
                            <TextField {...endProps} />
                        </>
                    )}
                />
                <Button
                    variant="contained"
                    onClick={handleGenerateReport}
                    disabled={!dateRange[0] || !dateRange[1]}
                >
                    Generate Report
                </Button>
            </Paper>

            {performanceData && (
                <>
                    <Paper className="report-section">
                        <Typography variant="h6">Component Performance</Typography>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Component</TableCell>
                                        <TableCell>Avg Render Time</TableCell>
                                        <TableCell>P95 Render Time</TableCell>
                                        <TableCell>Rerenders</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {performanceData.componentMetrics.map((metric) => (
                                        <TableRow
                                            key={metric.name}
                                            onClick={() => handleMetricClick(metric)}
                                        >
                                            <TableCell>{metric.name}</TableCell>
                                            <TableCell>
                                                {formatDuration(metric.averageRenderTime)}
                                            </TableCell>
                                            <TableCell>
                                                {formatDuration(metric.p95RenderTime)}
                                            </TableCell>
                                            <TableCell>{metric.rerenders}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>

                    {/* Additional metrics tables */}

                    <Button
                        variant="contained"
                        onClick={handleExportReport}
                        disabled={isExporting}
                    >
                        {isExporting ? 'Exporting...' : 'Export Report'}
                    </Button>
                </>
            )}

            <Dialog
                open={showDetailDialog}
                onClose={() => setShowDetailDialog(false)}
            >
                <DialogTitle>Metric Details</DialogTitle>
                <DialogContent>
                    {selectedMetric && (
                        <MetricDetails metric={selectedMetric} />
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowDetailDialog(false)}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};