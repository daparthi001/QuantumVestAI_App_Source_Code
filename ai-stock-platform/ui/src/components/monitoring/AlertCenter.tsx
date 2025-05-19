/**
 * Alert Center Component
 * Created: 2025-05-19 05:05:29
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import {
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Badge,
    IconButton,
    Typography,
    Chip,
    Divider,
    Box,
    Alert,
    Collapse
} from '@mui/material';
import {
    Notifications as NotificationsIcon,
    Error as ErrorIcon,
    Warning as WarningIcon,
    Info as InfoIcon,
    CheckCircle as SuccessIcon
} from '@mui/icons-material';
import { RealTimeMonitor } from '../../services/monitoring/RealTimeMonitor';
import { TransitionGroup } from 'react-transition-group';

interface AlertItem {
    id: string;
    type: 'error' | 'warning' | 'info' | 'success';
    message: string;
    timestamp: number;
    details?: any;
    acknowledged: boolean;
}

export const AlertCenter: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [alerts, setAlerts] = useState<AlertItem[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);

    useEffect(() => {
        const monitor = RealTimeMonitor.getInstance();
        const unsubscribe = monitor.subscribe((data) => {
            if (data.alerts) {
                handleNewAlerts(data.alerts);
            }
        });

        return () => unsubscribe();
    }, []);

    const handleNewAlerts = (newAlerts: any[]) => {
        const formattedAlerts = newAlerts.map(alert => ({
            id: `alert-${Date.now()}-${Math.random()}`,
            type: getAlertType(alert),
            message: alert.message,
            timestamp: Date.now(),
            details: alert.details,
            acknowledged: false
        }));

        setAlerts(prev => [...formattedAlerts, ...prev].slice(0, 100));
        setUnreadCount(prev => prev + formattedAlerts.length);
    };

    const handleAcknowledge = (alertId: string) => {
        setAlerts(prev =>
            prev.map(alert =>
                alert.id === alertId
                    ? { ...alert, acknowledged: true }
                    : alert
            )
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
    };

    const handleClearAll = () => {
        setAlerts([]);
        setUnreadCount(0);
    };

    return (
        <>
            <IconButton
                color="inherit"
                onClick={() => setIsOpen(true)}
                sx={{ position: 'fixed', right: 20, top: 20 }}
            >
                <Badge badgeContent={unreadCount} color="error">
                    <NotificationsIcon />
                </Badge>
            </IconButton>

            <Drawer
                anchor="right"
                open={isOpen}
                onClose={() => setIsOpen(false)}
                PaperProps={{
                    sx: { width: 400 }
                }}
            >
                <Box sx={{ p: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">Alert Center</Typography>
                        <Chip
                            label={`${unreadCount} unread`}
                            color="primary"
                            size="small"
                        />
                    </Box>
                    <Divider sx={{ my: 2 }} />
                    <TransitionGroup>
                        {alerts.map(alert => (
                            <Collapse key={alert.id}>
                                <AlertItem
                                    alert={alert}
                                    onAcknowledge={handleAcknowledge}
                                />
                            </Collapse>
                        ))}
                    </TransitionGroup>
                </Box>
            </Drawer>
        </>
    );
};

const AlertItem: React.FC<{
    alert: AlertItem;
    onAcknowledge: (id: string) => void;
}> = ({ alert, onAcknowledge }) => {
    const [expanded, setExpanded] = useState(false);

    const getAlertIcon = (type: AlertItem['type']) => {
        switch (type) {
            case 'error':
                return <ErrorIcon color="error" />;
            case 'warning':
                return <WarningIcon color="warning" />;
            case 'success':
                return <SuccessIcon color="success" />;
            default:
                return <InfoIcon color="info" />;
        }
    };

    return (
        <Alert
            severity={alert.type}
            icon={getAlertIcon(alert.type)}
            sx={{
                mb: 1,
                opacity: alert.acknowledged ? 0.7 : 1,
                cursor: 'pointer'
            }}
            onClick={() => setExpanded(!expanded)}
        >
            <AlertTitle>
                {alert.message}
                {!alert.acknowledged && (
                    <Chip
                        label="New"
                        size="small"
                        color="primary"
                        sx={{ ml: 1 }}
                        onClick={(e) => {
                            e.stopPropagation();
                            onAcknowledge(alert.id);
                        }}
                    />
                )}
            </AlertTitle>
            <Collapse in={expanded}>
                <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" display="block">
                        Time: {new Date(alert.timestamp).toLocaleString()}
                    </Typography>
                    {alert.details && (
                        <pre>
                            {JSON.stringify(alert.details, null, 2)}
                        </pre>
                    )}
                </Box>
            </Collapse>
        </Alert>
    );
};

const getAlertType = (alert: any): AlertItem['type'] => {
    if (alert.level === 'critical') return 'error';
    if (alert.level === 'warning') return 'warning';
    if (alert.level === 'success') return 'success';
    return 'info';
};