/**
 * Modern Quantum Dashboard Enhancement
 * Interactive widgets, charts, and real-time data visualization
 * Created: 2025-01-09
 * Author: AI Assistant
 */

class QuantumDashboard {
    constructor() {
        this.widgets = new Map();
        this.animations = new Map();
        this.refreshInterval = null;
        this.wsConnection = null;
        this.init();
    }

    init() {
        this.setupDashboardGrid();
        this.setupInteractiveWidgets();
        this.setupRealTimeData();
        this.setupChartIntegrations();
        this.setupDashboardCustomization();
        this.setupNotificationSystem();
        this.initializeWidgets();
    }

    setupDashboardGrid() {
        const dashboard = document.querySelector('.dashboard-container');
        if (!dashboard) return;

        // Add modern dashboard classes
        dashboard.classList.add('quantum-dashboard', 'quantum-animate-fade-in');

        // Create responsive grid for widgets
        const grid = document.createElement('div');
        grid.className = 'quantum-dashboard-grid';
        grid.innerHTML = `
            <div class="quantum-widget quantum-widget-large" data-widget="portfolio-overview">
                <div class="quantum-widget-header">
                    <h3 class="quantum-widget-title">Portfolio Overview</h3>
                    <div class="quantum-widget-actions">
                        <button class="quantum-btn-icon" data-action="refresh" data-tooltip="Refresh">
                            📊
                        </button>
                        <button class="quantum-btn-icon" data-action="expand" data-tooltip="Expand">
                            🔍
                        </button>
                    </div>
                </div>
                <div class="quantum-widget-content">
                    <div class="quantum-loading-skeleton" id="portfolio-loading">
                        <div class="quantum-skeleton quantum-skeleton-text"></div>
                        <div class="quantum-skeleton quantum-skeleton-text"></div>
                        <div class="quantum-skeleton quantum-skeleton-text"></div>
                    </div>
                    <div class="portfolio-metrics" style="display: none;">
                        <div class="metric-card">
                            <div class="metric-label">Total Value</div>
                            <div class="metric-value" id="total-value">$0.00</div>
                            <div class="metric-change" id="total-change">+0.00%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Today's Change</div>
                            <div class="metric-value" id="daily-change">$0.00</div>
                            <div class="metric-change" id="daily-change-percent">+0.00%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Total Return</div>
                            <div class="metric-value" id="total-return">$0.00</div>
                            <div class="metric-change" id="total-return-percent">+0.00%</div>
                        </div>
                    </div>
                    <canvas id="portfolio-chart" style="display: none;"></canvas>
                </div>
            </div>

            <div class="quantum-widget quantum-widget-medium" data-widget="market-overview">
                <div class="quantum-widget-header">
                    <h3 class="quantum-widget-title">Market Overview</h3>
                    <div class="quantum-widget-actions">
                        <button class="quantum-btn-icon" data-action="refresh" data-tooltip="Refresh">
                            📈
                        </button>
                    </div>
                </div>
                <div class="quantum-widget-content">
                    <div id="market-indices"></div>
                </div>
            </div>

            <div class="quantum-widget quantum-widget-medium" data-widget="watchlist">
                <div class="quantum-widget-header">
                    <h3 class="quantum-widget-title">Watchlist</h3>
                    <div class="quantum-widget-actions">
                        <button class="quantum-btn-icon" data-action="add" data-tooltip="Add Stock">
                            ➕
                        </button>
                        <button class="quantum-btn-icon" data-action="refresh" data-tooltip="Refresh">
                            🔄
                        </button>
                    </div>
                </div>
                <div class="quantum-widget-content">
                    <div id="watchlist-items"></div>
                </div>
            </div>

            <div class="quantum-widget quantum-widget-small" data-widget="news-feed">
                <div class="quantum-widget-header">
                    <h3 class="quantum-widget-title">Market News</h3>
                    <div class="quantum-widget-actions">
                        <button class="quantum-btn-icon" data-action="refresh" data-tooltip="Refresh">
                            📰
                        </button>
                    </div>
                </div>
                <div class="quantum-widget-content">
                    <div id="news-items"></div>
                </div>
            </div>

            <div class="quantum-widget quantum-widget-small" data-widget="ai-insights">
                <div class="quantum-widget-header">
                    <h3 class="quantum-widget-title">AI Insights</h3>
                    <div class="quantum-widget-actions">
                        <button class="quantum-btn-icon" data-action="refresh" data-tooltip="Refresh">
                            🤖
                        </button>
                    </div>
                </div>
                <div class="quantum-widget-content">
                    <div id="ai-recommendations"></div>
                </div>
            </div>

            <div class="quantum-widget quantum-widget-small" data-widget="performance">
                <div class="quantum-widget-header">
                    <h3 class="quantum-widget-title">Performance</h3>
                    <div class="quantum-widget-actions">
                        <button class="quantum-btn-icon" data-action="settings" data-tooltip="Settings">
                            ⚙️
                        </button>
                    </div>
                </div>
                <div class="quantum-widget-content">
                    <canvas id="performance-chart"></canvas>
                </div>
            </div>
        `;

        // Insert grid after dashboard header
        const header = dashboard.querySelector('.dashboard-header');
        if (header) {
            header.after(grid);
        } else {
            dashboard.prepend(grid);
        }
    }

    setupInteractiveWidgets() {
        const widgets = document.querySelectorAll('.quantum-widget');
        
        widgets.forEach(widget => {
            this.makeWidgetInteractive(widget);
        });

        // Setup drag and drop for dashboard customization
        this.setupDragAndDrop();
    }

    makeWidgetInteractive(widget) {
        const header = widget.querySelector('.quantum-widget-header');
        const content = widget.querySelector('.quantum-widget-content');
        
        // Add hover effects
        widget.addEventListener('mouseenter', () => {
            widget.classList.add('quantum-widget-hover');
        });

        widget.addEventListener('mouseleave', () => {
            widget.classList.remove('quantum-widget-hover');
        });

        // Setup action buttons
        const actionButtons = widget.querySelectorAll('[data-action]');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleWidgetAction(widget, button.dataset.action);
            });
        });

        // Add loading states
        this.addLoadingState(widget);
    }

    handleWidgetAction(widget, action) {
        const widgetType = widget.dataset.widget;
        
        switch (action) {
            case 'refresh':
                this.refreshWidget(widget);
                break;
            case 'expand':
                this.expandWidget(widget);
                break;
            case 'settings':
                this.showWidgetSettings(widget);
                break;
            case 'add':
                this.showAddDialog(widgetType);
                break;
            default:
                console.log(`Unknown action: ${action} for widget: ${widgetType}`);
        }
    }

    refreshWidget(widget) {
        const widgetType = widget.dataset.widget;
        
        // Add loading animation
        widget.classList.add('quantum-loading');
        
        // Simulate data refresh
        setTimeout(() => {
            widget.classList.remove('quantum-loading');
            this.loadWidgetData(widget);
            
            // Show success feedback
            this.showWidgetFeedback(widget, 'Refreshed', 'success');
        }, 1500);
    }

    loadWidgetData(widget) {
        const widgetType = widget.dataset.widget;
        
        switch (widgetType) {
            case 'portfolio-overview':
                this.loadPortfolioData(widget);
                break;
            case 'market-overview':
                this.loadMarketData(widget);
                break;
            case 'watchlist':
                this.loadWatchlistData(widget);
                break;
            case 'news-feed':
                this.loadNewsData(widget);
                break;
            case 'ai-insights':
                this.loadAIInsights(widget);
                break;
            case 'performance':
                this.loadPerformanceData(widget);
                break;
        }
    }

    loadPortfolioData(widget) {
        // Hide loading skeleton
        const loading = widget.querySelector('#portfolio-loading');
        const metrics = widget.querySelector('.portfolio-metrics');
        const chart = widget.querySelector('#portfolio-chart');
        
        if (loading) loading.style.display = 'none';
        if (metrics) metrics.style.display = 'flex';
        if (chart) chart.style.display = 'block';

        // Simulate portfolio data
        const mockData = {
            totalValue: 125000.50,
            dailyChange: 2500.75,
            dailyChangePercent: 2.04,
            totalReturn: 25000.50,
            totalReturnPercent: 25.0
        };

        // Update metrics
        this.updateElement('#total-value', this.formatCurrency(mockData.totalValue));
        this.updateElement('#daily-change', this.formatCurrency(mockData.dailyChange));
        this.updateElement('#daily-change-percent', this.formatPercent(mockData.dailyChangePercent));
        this.updateElement('#total-return', this.formatCurrency(mockData.totalReturn));
        this.updateElement('#total-return-percent', this.formatPercent(mockData.totalReturnPercent));

        // Add color coding for changes
        this.addChangeColorCoding('#daily-change', mockData.dailyChange);
        this.addChangeColorCoding('#daily-change-percent', mockData.dailyChangePercent);
        this.addChangeColorCoding('#total-return', mockData.totalReturn);
        this.addChangeColorCoding('#total-return-percent', mockData.totalReturnPercent);

        // Create portfolio chart
        this.createPortfolioChart(chart);
    }

    loadMarketData(widget) {
        const container = widget.querySelector('#market-indices');

        container.innerHTML = `
            <div class="quantum-loading-skeleton">
                <div class="quantum-skeleton quantum-skeleton-text"></div>
                <div class="quantum-skeleton quantum-skeleton-text"></div>
                <div class="quantum-skeleton quantum-skeleton-text"></div>
            </div>`;

        setTimeout(() => {
        const mockIndices = [
            { name: 'S&P 500', value: 4150.25, change: 1.25 },
            { name: 'NASDAQ', value: 12750.80, change: -0.85 },
            { name: 'DOW', value: 34200.15, change: 0.45 }
        ];

        container.innerHTML = mockIndices.map(index => `
            <div class="market-index-item quantum-animate-fade-in">
                <div class="index-name">${index.name}</div>
                <div class="index-value">${index.value.toLocaleString()}</div>
                <div class="index-change ${index.change >= 0 ? 'positive' : 'negative'}">
                    ${index.change >= 0 ? '↗' : '↘'} ${Math.abs(index.change)}%
                </div>
            </div>
        `).join('');
        }, 500);
    }

    loadWatchlistData(widget) {
        const container = widget.querySelector('#watchlist-items');

        container.innerHTML = `
            <div class="quantum-loading-skeleton">
                <div class="quantum-skeleton quantum-skeleton-text"></div>
                <div class="quantum-skeleton quantum-skeleton-text"></div>
                <div class="quantum-skeleton quantum-skeleton-text"></div>
            </div>`;

        setTimeout(() => {

        const mockStocks = [
            { symbol: 'AAPL', name: 'Apple Inc.', price: 175.25, change: 2.15 },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 2650.80, change: -1.25 },
            { symbol: 'TSLA', name: 'Tesla Inc.', price: 850.45, change: 5.75 },
            { symbol: 'MSFT', name: 'Microsoft Corp.', price: 320.15, change: 1.85 }
        ];

        container.innerHTML = mockStocks.map(stock => `
            <div class="watchlist-item quantum-animate-slide-in">
                <div class="stock-info">
                    <div class="stock-symbol">${stock.symbol}</div>
                    <div class="stock-name">${stock.name}</div>
                </div>
                <div class="stock-price">
                    <div class="price">${this.formatCurrency(stock.price)}</div>
                    <div class="change ${stock.change >= 0 ? 'positive' : 'negative'}">
                        ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
                    </div>
                </div>
            </div>
        `).join('');
        }, 500);
    }

    loadNewsData(widget) {
        const container = widget.querySelector('#news-items');
        
        const mockNews = [
            { title: 'Market Rally Continues Amid Economic Optimism', time: '2h ago' },
            { title: 'Tech Stocks Lead Monday Trading Session', time: '4h ago' },
            { title: 'Federal Reserve Signals Rate Stability', time: '6h ago' },
            { title: 'Energy Sector Shows Strong Performance', time: '8h ago' }
        ];

        container.innerHTML = mockNews.map(news => `
            <div class="news-item quantum-animate-fade-in">
                <div class="news-title">${news.title}</div>
                <div class="news-time">${news.time}</div>
            </div>
        `).join('');
    }

    loadAIInsights(widget) {
        const container = widget.querySelector('#ai-recommendations');
        
        const mockInsights = [
            { type: 'BUY', stock: 'NVDA', confidence: 85 },
            { type: 'HOLD', stock: 'AMZN', confidence: 72 },
            { type: 'SELL', stock: 'META', confidence: 68 }
        ];

        container.innerHTML = mockInsights.map(insight => `
            <div class="ai-insight-item quantum-animate-fade-in">
                <div class="insight-header">
                    <span class="insight-type ${insight.type.toLowerCase()}">${insight.type}</span>
                    <span class="insight-stock">${insight.stock}</span>
                </div>
                <div class="insight-confidence">
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${insight.confidence}%"></div>
                    </div>
                    <span class="confidence-text">${insight.confidence}% confidence</span>
                </div>
            </div>
        `).join('');
    }

    loadPerformanceData(widget) {
        const canvas = widget.querySelector('#performance-chart');
        this.createPerformanceChart(canvas);
    }

    createPortfolioChart(canvas) {
        if (!canvas || !window.Chart) return;

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Stocks', 'Bonds', 'ETFs', 'Cash'],
                datasets: [{
                    data: [60, 25, 10, 5],
                    backgroundColor: [
                        'rgba(103, 126, 234, 0.8)',
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(250, 112, 154, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            padding: 15
                        }
                    }
                }
            }
        });
    }

    createPerformanceChart(canvas) {
        if (!canvas || !window.Chart) return;

        const ctx = canvas.getContext('2d');
        const mockData = Array.from({ length: 30 }, (_, i) => ({
            x: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000),
            y: 100000 + Math.random() * 50000
        }));

        new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Portfolio Value',
                    data: mockData,
                    borderColor: 'rgba(79, 172, 254, 1)',
                    backgroundColor: 'rgba(79, 172, 254, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff',
                            callback: function(value) {
                                return '$' + (value / 1000).toFixed(0) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    setupRealTimeData() {
        // Simulate real-time updates
        this.refreshInterval = setInterval(() => {
            this.updateRealTimeData();
        }, 30000); // Update every 30 seconds
    }

    updateRealTimeData() {
        // Update live indicators
        const liveIndicators = document.querySelectorAll('.live-indicator');
        liveIndicators.forEach(indicator => {
            indicator.classList.add('pulse');
            setTimeout(() => indicator.classList.remove('pulse'), 1000);
        });

        // Update random metrics to simulate real-time changes
        this.updateRandomMetrics();
    }

    updateRandomMetrics() {
        const metrics = document.querySelectorAll('.metric-value, .index-value, .price');
        metrics.forEach(metric => {
            const currentValue = parseFloat(metric.textContent.replace(/[$,]/g, ''));
            if (currentValue && Math.random() > 0.7) { // 30% chance to update
                const change = (Math.random() - 0.5) * 0.02; // ±1% change
                const newValue = currentValue * (1 + change);
                
                if (metric.textContent.includes('$')) {
                    metric.textContent = this.formatCurrency(newValue);
                } else {
                    metric.textContent = newValue.toFixed(2);
                }
                
                // Highlight updated value
                metric.classList.add('value-updated');
                setTimeout(() => metric.classList.remove('value-updated'), 1000);
            }
        });
    }

    setupDragAndDrop() {
        // Enable drag and drop for dashboard customization
        const widgets = document.querySelectorAll('.quantum-widget');
        
        widgets.forEach(widget => {
            widget.draggable = true;
            
            widget.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', widget.dataset.widget);
                widget.classList.add('dragging');
            });
            
            widget.addEventListener('dragend', () => {
                widget.classList.remove('dragging');
            });
            
            widget.addEventListener('dragover', (e) => {
                e.preventDefault();
            });
            
            widget.addEventListener('drop', (e) => {
                e.preventDefault();
                const draggedWidgetType = e.dataTransfer.getData('text/plain');
                const draggedWidget = document.querySelector(`[data-widget="${draggedWidgetType}"]`);
                
                if (draggedWidget && draggedWidget !== widget) {
                    // Swap positions
                    const temp = document.createElement('div');
                    widget.parentNode.insertBefore(temp, widget);
                    draggedWidget.parentNode.insertBefore(widget, draggedWidget);
                    temp.parentNode.insertBefore(draggedWidget, temp);
                    temp.remove();
                    
                    // Save layout
                    this.saveDashboardLayout();
                }
            });
        });
    }

    saveDashboardLayout() {
        const widgets = Array.from(document.querySelectorAll('.quantum-widget'));
        const layout = widgets.map(widget => widget.dataset.widget);
        localStorage.setItem('dashboard-layout', JSON.stringify(layout));
    }

    restoreDashboardLayout() {
        const savedLayout = localStorage.getItem('dashboard-layout');
        if (!savedLayout) return;
        
        try {
            const layout = JSON.parse(savedLayout);
            const grid = document.querySelector('.quantum-dashboard-grid');
            const widgets = document.querySelectorAll('.quantum-widget');
            
            // Reorder widgets according to saved layout
            layout.forEach(widgetType => {
                const widget = document.querySelector(`[data-widget="${widgetType}"]`);
                if (widget) {
                    grid.appendChild(widget);
                }
            });
        } catch (error) {
            console.error('Failed to restore dashboard layout:', error);
        }
    }

    showWidgetFeedback(widget, message, type = 'info') {
        const feedback = document.createElement('div');
        feedback.className = `quantum-widget-feedback quantum-alert alert-${type}`;
        feedback.textContent = message;
        
        widget.appendChild(feedback);
        
        setTimeout(() => {
            feedback.classList.add('quantum-animate-fade-in');
        }, 10);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }

    addLoadingState(widget) {
        widget.addEventListener('load-start', () => {
            widget.classList.add('quantum-loading');
        });
        
        widget.addEventListener('load-end', () => {
            widget.classList.remove('quantum-loading');
        });
    }

    initializeWidgets() {
        // Load initial data for all widgets
        const widgets = document.querySelectorAll('.quantum-widget');
        widgets.forEach(widget => {
            setTimeout(() => {
                this.loadWidgetData(widget);
            }, Math.random() * 1000); // Stagger loading
        });

        // Restore saved layout
        this.restoreDashboardLayout();
    }

    // Utility methods
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value);
    }

    formatPercent(value) {
        return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
    }

    updateElement(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
    }

    addChangeColorCoding(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.classList.remove('positive', 'negative');
            element.classList.add(value >= 0 ? 'positive' : 'negative');
        }
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        if (this.wsConnection) {
            this.wsConnection.close();
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.dashboard-container')) {
        window.quantumDashboard = new QuantumDashboard();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.quantumDashboard) {
        window.quantumDashboard.destroy();
    }
});