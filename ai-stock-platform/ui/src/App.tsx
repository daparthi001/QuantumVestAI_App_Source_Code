/**
 * Main App Component
 * Created: 2025-05-19 04:07:03
 * Updated: 2025-06-19 03:06:29
 * Author: daparthi001
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ErrorProvider } from './contexts/ErrorContext';
import APIErrorBoundary from './components/common/APIErrorBoundary';
import ErrorDisplay from './components/common/ErrorDisplay';
import PrivateRoute from './components/auth/PrivateRoute';
import Login from './components/auth/Login';
import Dashboard from './components/Dashboard';
import StockDetail from './components/StockDetail';
import NotFound from './components/NotFound';

const App: React.FC = () => {
  const handleError = (error: Error) => {
    console.error('Global error caught:', error);
    // You could implement additional error logging here
  };

  return (
    <Router>
      <ErrorProvider>
        <AuthProvider>
          <APIErrorBoundary onError={handleError}>
            <ErrorDisplay />
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/stocks/:symbol"
                element={
                  <PrivateRoute>
                    <StockDetail />
                  </PrivateRoute>
                }
              />
              <Route path="/404" element={<NotFound />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </APIErrorBoundary>
        </AuthProvider>
      </ErrorProvider>
    </Router>
  );
};

export default App;