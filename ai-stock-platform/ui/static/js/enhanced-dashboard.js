/**
 * Enhanced Dashboard Controller with Loading States and Error Handling
 * Created: 2025-01-09
 * Author: AI Assistant
 */

class DashboardController {
    constructor() {
        this.apiClient = window.APIClient;
        this.uiErrorHandler = window.UIErrorHandler;
        this.loadingManager = window.LoadingManager;
        this.refreshInterval = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.setupAutoRefresh();
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDashboardData(true);
            });
        }
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.setupAutoRefresh();
                } else {
                    this.clearAutoRefresh();
                }
            });
        }
        
        // Stock search
        const stockSearchInput = document.getElementById('stockSearch');
        if (stockSearchInput) {
            let searchTimeout;
            stockSearchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchStocks(e.target.value);
                }, 300);
            });
        }
        
        // Watchlist management
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="add-to-watchlist"]')) {
                e.preventDefault();
                const symbol = e.target.dataset.symbol;
                this.addToWatchlist(symbol);
            }
            
            if (e.target.matches('[data-action="remove-from-watchlist"]')) {
                e.preventDefault();
                const symbol = e.target.dataset.symbol;
                this.removeFromWatchlist(symbol);
            }
        });
    }
    
    async loadDashboardData(showLoading = false) {
        try {
            if (showLoading) {
                this.loadingManager.showGlobalLoading('Refreshing dashboard...');
            }
            
            // Load all dashboard components
            await Promise.all([
                this.loadMarketOverview(),
                this.loadTrendingStocks(),
                this.loadWatchlist(),
                this.loadPortfolioSummary(),
                this.loadRecentAlerts()
            ]);
            
            this.uiErrorHandler.showSuccess('Dashboard updated successfully', { 
                duration: 2000,
                position: 'top-right'
            });
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.uiErrorHandler.handleAPIError(error, {
                title: 'Dashboard Error',
                duration: 5000
            });
        } finally {
            if (showLoading) {
                this.loadingManager.hideGlobalLoading();
            }
        }
    }
    
    async loadMarketOverview() {
        const container = document.getElementById('marketOverview');
        if (!container) return;
        
        try {
            this.loadingManager.showLoading(container, {
                message: 'Loading market data...',
                size: 'small'
            });
            
            const response = await this.apiClient.get('/analytics/market-overview');
            
            if (response.status === 'success') {
                this.renderMarketOverview(container, response.data);
            } else {
                throw new Error(response.message || 'Failed to load market overview');
            }
            
        } catch (error) {
            this.renderMarketOverviewError(container, error);
        } finally {
            this.loadingManager.hideLoading(container);
        }
    }
    
    async loadTrendingStocks() {
        const container = document.getElementById('trendingStocks');
        if (!container) return;
        
        try {
            this.loadingManager.showLoading(container, {
                message: 'Loading trending stocks...',
                size: 'small'
            });
            
            const response = await this.apiClient.get('/stocks/trending?limit=10');
            
            if (response.status === 'success') {
                this.renderTrendingStocks(container, response.data);
            } else {
                throw new Error(response.message || 'Failed to load trending stocks');
            }
            
        } catch (error) {
            this.renderTrendingStocksError(container, error);
        } finally {
            this.loadingManager.hideLoading(container);
        }
    }
    
    async loadWatchlist() {
        const container = document.getElementById('watchlist');
        if (!container) return;
        
        try {
            this.loadingManager.showLoading(container, {
                message: 'Loading watchlist...',
                size: 'small'
            });
            
            const response = await this.apiClient.get('/watchlists');
            
            if (response.status === 'success') {
                this.renderWatchlist(container, response.data);
            } else {
                throw new Error(response.message || 'Failed to load watchlist');
            }
            
        } catch (error) {
            this.renderWatchlistError(container, error);
        } finally {
            this.loadingManager.hideLoading(container);
        }
    }
    
    async loadPortfolioSummary() {
        const container = document.getElementById('portfolioSummary');
        if (!container) return;
        
        try {
            this.loadingManager.showLoading(container, {
                message: 'Loading portfolio...',
                size: 'small'
            });
            
            // Mock portfolio data since no endpoint exists yet
            const mockData = {
                total_value: 125670.50,
                daily_change: 2340.75,
                daily_change_percent: 1.89,
                positions: [
                    { symbol: 'AAPL', shares: 50, value: 9922.50, change_percent: 2.1 },
                    { symbol: 'MSFT', shares: 25, value: 10640.75, change_percent: 1.8 },
                    { symbol: 'GOOGL', shares: 30, value: 5306.70, change_percent: 1.2 }
                ]
            };
            
            this.renderPortfolioSummary(container, mockData);
            
        } catch (error) {
            this.renderPortfolioSummaryError(container, error);
        } finally {
            this.loadingManager.hideLoading(container);
        }
    }
    
    async loadRecentAlerts() {
        const container = document.getElementById('recentAlerts');
        if (!container) return;
        
        try {
            this.loadingManager.showLoading(container, {
                message: 'Loading alerts...',
                size: 'small'
            });
            
            // Mock alerts data since no endpoint exists yet
            const mockData = [
                {
                    id: 1,
                    type: 'price_alert',
                    message: 'AAPL reached target price of $200',
                    timestamp: new Date(Date.now() - 3600000).toISOString(),
                    severity: 'info'
                },
                {
                    id: 2,
                    type: 'portfolio_alert',
                    message: 'Portfolio gained 2.5% today',
                    timestamp: new Date(Date.now() - 7200000).toISOString(),
                    severity: 'success'
                }
            ];
            
            this.renderRecentAlerts(container, mockData);
            
        } catch (error) {
            this.renderRecentAlertsError(container, error);
        } finally {
            this.loadingManager.hideLoading(container);
        }
    }
    
    renderMarketOverview(container, data) {
        const html = `
            <div class="market-overview">
                <h3 class="section-title">Market Overview</h3>
                <div class="row">
                    ${data.indices.map(index => `
                        <div class="col-md-4 mb-3">
                            <div class="market-index-card">
                                <h4>${index.name}</h4>
                                <div class="index-value">${index.value.toLocaleString()}</div>
                                <div class="index-change ${index.change_percent >= 0 ? 'positive' : 'negative'}">
                                    <i class="bi bi-${index.change_percent >= 0 ? 'arrow-up' : 'arrow-down'}"></i>
                                    ${index.change_percent.toFixed(2)}%
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="market-sentiment mt-3">
                    <span class="sentiment-label">Market Sentiment:</span>
                    <span class="sentiment-value ${data.market_sentiment}">${data.market_sentiment.toUpperCase()}</span>
                </div>
            </div>
        `;
        container.innerHTML = html;
    }
    
    renderTrendingStocks(container, data) {
        const stocks = data.stocks || data;
        const html = `
            <div class="trending-stocks">
                <h3 class="section-title">Trending Stocks</h3>
                <div class="stocks-list">
                    ${stocks.map(stock => `
                        <div class="stock-item">
                            <div class="stock-info">
                                <span class="stock-symbol">${stock.symbol}</span>
                                <span class="stock-name">${stock.name}</span>
                            </div>
                            <div class="stock-price">
                                <span class="price">$${stock.price.toFixed(2)}</span>
                                <span class="change ${stock.change_percent >= 0 ? 'positive' : 'negative'}">
                                    ${stock.change_percent.toFixed(2)}%
                                </span>
                            </div>
                            <div class="stock-actions">
                                <button class="btn btn-sm btn-outline-primary" 
                                        data-action="add-to-watchlist" 
                                        data-symbol="${stock.symbol}">
                                    <i class="bi bi-plus"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML = html;
    }
    
    renderWatchlist(container, data) {
        const watchlists = Array.isArray(data) ? data : [data];
        const html = `
            <div class="watchlist">
                <h3 class="section-title">My Watchlist</h3>
                ${watchlists.map(watchlist => `
                    <div class="watchlist-group">
                        <h4 class="watchlist-name">${watchlist.name}</h4>
                        <div class="watchlist-stocks">
                            ${watchlist.stocks.map(stock => `
                                <div class="watchlist-stock-item">
                                    <div class="stock-info">
                                        <span class="stock-symbol">${stock.symbol}</span>
                                        <span class="stock-name">${stock.name}</span>
                                    </div>
                                    <div class="stock-price">
                                        <span class="price">$${stock.price.toFixed(2)}</span>
                                        <span class="change ${stock.change_percent >= 0 ? 'positive' : 'negative'}">
                                            ${stock.change_percent.toFixed(2)}%
                                        </span>
                                    </div>
                                    <div class="stock-actions">
                                        <button class="btn btn-sm btn-outline-danger" 
                                                data-action="remove-from-watchlist" 
                                                data-symbol="${stock.symbol}">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        container.innerHTML = html;
    }
    
    renderPortfolioSummary(container, data) {
        const html = `
            <div class="portfolio-summary">
                <h3 class="section-title">Portfolio Summary</h3>
                <div class="portfolio-value">
                    <div class="total-value">$${data.total_value.toLocaleString()}</div>
                    <div class="daily-change ${data.daily_change >= 0 ? 'positive' : 'negative'}">
                        <i class="bi bi-${data.daily_change >= 0 ? 'arrow-up' : 'arrow-down'}"></i>
                        $${Math.abs(data.daily_change).toFixed(2)} (${data.daily_change_percent.toFixed(2)}%)
                    </div>
                </div>
                <div class="portfolio-positions mt-3">
                    <h4>Top Positions</h4>
                    ${data.positions.map(position => `
                        <div class="position-item">
                            <span class="position-symbol">${position.symbol}</span>
                            <span class="position-shares">${position.shares} shares</span>
                            <span class="position-value">$${position.value.toLocaleString()}</span>
                            <span class="position-change ${position.change_percent >= 0 ? 'positive' : 'negative'}">
                                ${position.change_percent.toFixed(2)}%
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML = html;
    }
    
    renderRecentAlerts(container, data) {
        const html = `
            <div class="recent-alerts">
                <h3 class="section-title">Recent Alerts</h3>
                <div class="alerts-list">
                    ${data.map(alert => `
                        <div class="alert-item ${alert.severity}">
                            <div class="alert-icon">
                                <i class="bi bi-${this.getAlertIcon(alert.severity)}"></i>
                            </div>
                            <div class="alert-content">
                                <div class="alert-message">${alert.message}</div>
                                <div class="alert-time">${this.formatTimeAgo(alert.timestamp)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML = html;
    }
    
    // Error rendering methods
    renderMarketOverviewError(container, error) {
        container.innerHTML = `
            <div class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Failed to load market overview</p>
                <button class="btn btn-sm btn-outline-primary" onclick="dashboard.loadMarketOverview()">
                    Retry
                </button>
            </div>
        `;
    }
    
    renderTrendingStocksError(container, error) {
        container.innerHTML = `
            <div class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Failed to load trending stocks</p>
                <button class="btn btn-sm btn-outline-primary" onclick="dashboard.loadTrendingStocks()">
                    Retry
                </button>
            </div>
        `;
    }
    
    renderWatchlistError(container, error) {
        container.innerHTML = `
            <div class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Failed to load watchlist</p>
                <button class="btn btn-sm btn-outline-primary" onclick="dashboard.loadWatchlist()">
                    Retry
                </button>
            </div>
        `;
    }
    
    renderPortfolioSummaryError(container, error) {
        container.innerHTML = `
            <div class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Failed to load portfolio</p>
                <button class="btn btn-sm btn-outline-primary" onclick="dashboard.loadPortfolioSummary()">
                    Retry
                </button>
            </div>
        `;
    }
    
    renderRecentAlertsError(container, error) {
        container.innerHTML = `
            <div class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Failed to load alerts</p>
                <button class="btn btn-sm btn-outline-primary" onclick="dashboard.loadRecentAlerts()">
                    Retry
                </button>
            </div>
        `;
    }
    
    // Utility methods
    getAlertIcon(severity) {
        switch (severity) {
            case 'success': return 'check-circle';
            case 'warning': return 'exclamation-triangle';
            case 'error': return 'x-circle';
            default: return 'info-circle';
        }
    }
    
    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} day${days > 1 ? 's' : ''} ago`;
        }
    }
    
    setupAutoRefresh() {
        this.clearAutoRefresh();
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000); // Refresh every 30 seconds
    }
    
    clearAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    async addToWatchlist(symbol) {
        try {
            // Mock implementation - would call API
            this.uiErrorHandler.showSuccess(`${symbol} added to watchlist`, { duration: 2000 });
        } catch (error) {
            this.uiErrorHandler.handleAPIError(error);
        }
    }
    
    async removeFromWatchlist(symbol) {
        try {
            // Mock implementation - would call API
            this.uiErrorHandler.showSuccess(`${symbol} removed from watchlist`, { duration: 2000 });
        } catch (error) {
            this.uiErrorHandler.handleAPIError(error);
        }
    }
    
    async searchStocks(query) {
        if (!query || query.length < 2) return;
        
        try {
            // Mock search - would call API
            console.log('Searching for:', query);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('marketOverview')) {
        window.dashboard = new DashboardController();
    }
});