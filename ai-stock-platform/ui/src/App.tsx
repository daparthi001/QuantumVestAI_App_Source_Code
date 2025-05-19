/**
 * Main App Component
 * Created: 2025-05-19 04:07:03
 * Author: daparthi001
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/auth/PrivateRoute';
import Login from './components/auth/Login';
import Dashboard from './components/Dashboard';
import StockDetail from './components/StockDetail';
import NotFound from './components/NotFound';

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
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
      </AuthProvider>
    </Router>
  );
};

export default App;