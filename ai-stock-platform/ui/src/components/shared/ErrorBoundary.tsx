/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Container, Alert, Button } from 'react-bootstrap';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // Render custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Container className="mt-5">
          <Alert variant="danger">
            <Alert.Heading>Oops! Something went wrong</Alert.Heading>
            <p>
              We're sorry, but an unexpected error occurred. Please try refreshing the page
              or contact support if the problem persists.
            </p>
            <hr />
            <div className="d-flex justify-content-end">
              <Button onClick={this.handleReset} variant="outline-danger">
                Try Again
              </Button>
              <Button 
                onClick={() => window.location.reload()} 
                variant="danger" 
                className="ms-2"
              >
                Reload Page
              </Button>
            </div>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-3">
                <summary>Error Details (Development Mode)</summary>
                <pre className="mt-2 text-danger">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
          </Alert>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;