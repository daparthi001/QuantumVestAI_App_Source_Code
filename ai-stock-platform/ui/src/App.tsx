/**
 * Main App Component with Advanced Features
 * Updated: 2025-06-19 18:06:43
 * Author: daparthi001
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './styles/global.css';
import './styles/quantum-components.css';
import { ROUTES } from './config/constants';
import { AuthProvider } from './contexts/AuthContext';
import { FeatureProvider } from './providers/FeatureProvider';
import { ThemeProvider } from './providers/ThemeProvider';
import { NotificationProvider } from './providers/NotificationProvider';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Layout from './components/layout/Layout';
import ErrorBoundary from './components/shared/ErrorBoundary';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Lazy load components for code splitting
const Login = React.lazy(() => import('./components/auth/Login'));
const Register = React.lazy(() => import('./components/auth/Register'));
const ForgotPassword = React.lazy(() => import('./components/auth/ForgotPassword'));
const ResetPassword = React.lazy(() => import('./components/auth/ResetPassword'));
const DesignPreview = React.lazy(() => import('./components/DesignPreview'));

const Dashboard = React.lazy(() => import('./components/Dashboard'));
const Stocks = React.lazy(() => import('./components/Stocks'));
const StockDetails = React.lazy(() => import('./components/StockDetails'));
const Watchlist = React.lazy(() => import('./components/Watchlist'));
const Analytics = React.lazy(() => import('./components/Analytics'));
const Settings = React.lazy(() => import('./components/Settings'));
const Profile = React.lazy(() => import('./components/Profile'));
const Portfolio = React.lazy(() => import('./components/Portfolio'));
const Backtest = React.lazy(() => import('./components/Backtest'));
const AiAssistant = React.lazy(() => import('./components/AiAssistant'));
const Trading = React.lazy(() => import('./components/Trading'));
const News = React.lazy(() => import('./components/News'));
const Alerts = React.lazy(() => import('./components/Alerts'));
const Reports = React.lazy(() => import('./components/Reports'));
const NotFound = React.lazy(() => import('./components/NotFound'));

// Loading component
const LoadingFallback = () => (
  <div className="loading-container">
    <div className="loading-spinner"></div>
    <p>Loading...</p>
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <ThemeProvider>
            <NotificationProvider>
              <AuthProvider>
                <FeatureProvider>
                  <React.Suspense fallback={<LoadingFallback />}>
                    <Routes>
                      {/* Public routes */}
                      <Route path={ROUTES.LOGIN} element={<Login />} />
                      <Route path={ROUTES.REGISTER} element={<Register />} />
                      <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPassword />} />
                      <Route path={ROUTES.RESET_PASSWORD} element={<ResetPassword />} />
                      <Route path="/preview" element={<DesignPreview />} />
                      
                      {/* Root redirect */}
                      <Route path="/" element={<Navigate to={ROUTES.DASHBOARD} />} />
                      
                      {/* Protected routes with layout */}
                      <Route path={ROUTES.DASHBOARD} element={
                        <ProtectedRoute>
                          <Layout>
                            <Dashboard />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.STOCKS} element={
                        <ProtectedRoute>
                          <Layout>
                            <Stocks />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={`${ROUTES.STOCKS}/:symbol`} element={
                        <ProtectedRoute>
                          <Layout>
                            <StockDetails />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.WATCHLIST} element={
                        <ProtectedRoute>
                          <Layout>
                            <Watchlist />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.ANALYTICS} element={
                        <ProtectedRoute>
                          <Layout>
                            <Analytics />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.SETTINGS} element={
                        <ProtectedRoute>
                          <Layout>
                            <Settings />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.PROFILE} element={
                        <ProtectedRoute>
                          <Layout>
                            <Profile />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.PORTFOLIO} element={
                        <ProtectedRoute>
                          <Layout>
                            <Portfolio />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.BACKTEST} element={
                        <ProtectedRoute>
                          <Layout>
                            <Backtest />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      {/* Advanced feature routes */}
                      <Route path={ROUTES.AI_ASSISTANT} element={
                        <ProtectedRoute>
                          <Layout>
                            <AiAssistant />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.TRADING} element={
                        <ProtectedRoute>
                          <Layout>
                            <Trading />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.NEWS} element={
                        <ProtectedRoute>
                          <Layout>
                            <News />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.ALERTS} element={
                        <ProtectedRoute>
                          <Layout>
                            <Alerts />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      <Route path={ROUTES.REPORTS} element={
                        <ProtectedRoute>
                          <Layout>
                            <Reports />
                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      {/* Admin routes */}
                      <Route path="/admin/*" element={
                        <ProtectedRoute requiredRole="admin">
                          <Layout>
                            <div className="admin-dashboard">
                              <h1>Admin Dashboard</h1>
                              <p>Admin components would go here</p>
                            </div>

                          </Layout>
                        </ProtectedRoute>
                      } />
                      
                      {/* Not found route */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </React.Suspense>
                </FeatureProvider>
              </AuthProvider>
            </NotificationProvider>
          </ThemeProvider>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;