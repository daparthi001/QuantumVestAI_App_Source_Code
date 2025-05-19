/**
 * Error Boundary Component
 * Created: 2025-05-19 04:58:03
 * Author: daparthi001
 */
import React, { Component, ErrorInfo } from 'react';
import { Button, Typography, Box } from '@mui/material';
import { ErrorOutline } from '@mui/icons-material';
import * as Sentry from '@sentry/react';

interface Props {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null
        };
    }

    static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null
        };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        this.setState({
            error,
            errorInfo
        });

        // Log error to Sentry
        Sentry.captureException(error, {
            extra: {
                errorInfo,
                componentStack: errorInfo.componentStack
            }
        });
    }

    handleRetry = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '400px',
                        padding: 3,
                        textAlign: 'center'
                    }}
                >
                    <ErrorOutline
                        color="error"
                        sx={{ fontSize: 64, marginBottom: 2 }}
                    />
                    <Typography variant="h5" gutterBottom>
                        Something went wrong
                    </Typography>
                    <Typography color="text.secondary" paragraph>
                        We apologize for the inconvenience. Please try again or contact support.
                    </Typography>
                    <Button
                        variant="contained"
                        onClick={this.handleRetry}
                        sx={{ marginTop: 2 }}
                    >
                        Retry
                    </Button>
                    {process.env.NODE_ENV === 'development' && (
                        <Box
                            sx={{
                                marginTop: 4,
                                textAlign: 'left',
                                width: '100%',
                                maxWidth: '800px'
                            }}
                        >
                            <Typography variant="subtitle2" color="error">
                                {this.state.error?.toString()}
                            </Typography>
                            <pre
                                style={{
                                    marginTop: '10px',
                                    padding: '10px',
                                    backgroundColor: '#f5f5f5',
                                    borderRadius: '4px',
                                    overflow: 'auto'
                                }}
                            >
                                {this.state.errorInfo?.componentStack}
                            </pre>
                        </Box>
                    )}
                </Box>
            );
        }

        return this.props.children;
    }
}