/**
 * Real-time Dashboard JavaScript
 * Handles WebSocket connections and live data updates
 */

class RealtimeDashboard {
    constructor() {
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.socket = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.startDataSimulation();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // Period selector
        const periodSelect = document.getElementById('period-select');
        if (periodSelect) {
            periodSelect.addEventListener('change', (e) => {
                this.updatePeriod(e.target.value);
            });
        }
    }

    connectWebSocket() {
        // For demo purposes, simulate WebSocket connection
        console.log('Connecting to WebSocket...');
        
        setTimeout(() => {
            this.isConnected = true;
            this.updateConnectionStatus('connected');
            console.log('WebSocket connected (simulated)');
        }, 1000);
    }

    startDataSimulation() {
        // Simulate real-time price updates every 2 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.simulateMarketData();
            }
        }, 2000);

        // Update portfolio data every 5 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.simulatePortfolioUpdate();
            }
        }, 5000);

        // Update last update timestamp
        setInterval(() => {
            this.updateLastUpdateTime();
        }, 1000);
    }

    simulateMarketData() {
        const symbols = ['SPY', 'QQQ', 'DIA', 'VIX'];
        
        symbols.forEach(symbol => {
            const cards = document.querySelectorAll(`.quantum-card h4:contains('${symbol}')`);
            if (cards.length === 0) return;

            // Find the card containing this symbol
            const symbolElement = Array.from(document.querySelectorAll('h4')).find(el => el.textContent === symbol);
            if (!symbolElement) return;

            const card = symbolElement.closest('.quantum-card');
            if (!card) return;

            const priceElement = card.querySelector('.price-display');
            const changeElement = card.querySelector('.fw-bold');
            
            if (priceElement && changeElement) {
                // Simulate price changes
                const currentPrice = parseFloat(priceElement.textContent.replace('$', ''));
                const changePercent = (Math.random() - 0.5) * 2; // -1% to +1%
                const newPrice = currentPrice * (1 + changePercent / 100);
                const change = newPrice - currentPrice;

                // Update price
                priceElement.textContent = `$${newPrice.toFixed(2)}`;

                // Update change display
                const isPositive = change >= 0;
                changeElement.className = `fw-bold ${isPositive ? 'text-success' : 'text-danger'}`;
                changeElement.textContent = `${isPositive ? '+' : ''}$${change.toFixed(2)} (${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`;

                // Update badge
                const badge = card.querySelector('.quantum-badge');
                if (badge) {
                    badge.textContent = isPositive ? '📈' : '📉';
                }

                // Add animation effect
                card.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    card.style.transform = 'scale(1)';
                }, 200);
            }
        });
    }

    simulatePortfolioUpdate() {
        const portfolioCard = document.querySelector('.quantum-particles .metric-value');
        if (!portfolioCard) return;

        // Get current portfolio value
        const currentValueText = portfolioCard.textContent.replace(/[$,]/g, '');
        const currentValue = parseFloat(currentValueText);

        if (!isNaN(currentValue)) {
            // Simulate small portfolio change
            const changePercent = (Math.random() - 0.5) * 0.5; // -0.25% to +0.25%
            const newValue = currentValue * (1 + changePercent / 100);

            portfolioCard.textContent = `$${newValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

            // Add glow effect for updates
            portfolioCard.style.boxShadow = '0 0 20px rgba(0, 210, 255, 0.5)';
            setTimeout(() => {
                portfolioCard.style.boxShadow = '';
            }, 1000);
        }
    }

    simulateTopMovers() {
        const topMovers = [
            { symbol: 'NVDA', price: 789.23, change: 6.14 },
            { symbol: 'TSLA', price: 245.67, change: -4.78 },
            { symbol: 'AAPL', price: 189.45, change: 2.31 },
            { symbol: 'MSFT', price: 378.92, change: -1.45 }
        ];

        topMovers.forEach(stock => {
            // Simulate price fluctuations
            stock.change += (Math.random() - 0.5) * 0.5;
            stock.price *= (1 + stock.change / 100);
        });

        // Update UI if top movers section exists
        const topMoversContainer = document.querySelector('.top-movers-list');
        if (topMoversContainer) {
            this.updateTopMoversDisplay(topMovers.slice(0, 2));
        }
    }

    updateTopMoversDisplay(movers) {
        const items = document.querySelectorAll('.top-mover-item');
        items.forEach((item, index) => {
            if (index < movers.length) {
                const mover = movers[index];
                const symbolEl = item.querySelector('.fw-bold');
                const priceEl = item.querySelector('.text-muted.small');
                const changeEl = item.querySelector('.text-end .fw-bold');
                
                if (symbolEl) symbolEl.textContent = mover.symbol;
                if (priceEl) priceEl.textContent = `$${mover.price.toFixed(2)}`;
                if (changeEl) {
                    const isPositive = mover.change >= 0;
                    changeEl.textContent = `${isPositive ? '+' : ''}${mover.change.toFixed(2)}%`;
                    changeEl.parentElement.className = `text-end ${isPositive ? 'text-success' : 'text-danger'}`;
                }
            }
        });
    }

    updateConnectionStatus(status) {
        const indicator = document.querySelector('.live-indicator');
        if (indicator) {
            switch (status) {
                case 'connected':
                    indicator.innerHTML = '🔴 LIVE';
                    indicator.style.color = '#10b981';
                    break;
                case 'connecting':
                    indicator.innerHTML = '🟡 CONNECTING';
                    indicator.style.color = '#f59e0b';
                    break;
                case 'disconnected':
                    indicator.innerHTML = '⚫ OFFLINE';
                    indicator.style.color = '#ef4444';
                    break;
            }
        }
    }

    updateLastUpdateTime() {
        const timeElements = document.querySelectorAll('[data-update-time]');
        const now = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        timeElements.forEach(el => {
            el.textContent = `Last updated: ${now}`;
        });

        // Update any "Last updated" text
        const lastUpdateTexts = document.querySelectorAll('div:contains("Last updated")');
        lastUpdateTexts.forEach(el => {
            if (el.textContent.includes('Last updated')) {
                el.innerHTML = el.innerHTML.replace(/Last updated: .*$/, `Last updated: ${now}`);
            }
        });
    }

    refreshData() {
        console.log('Refreshing data...');
        
        // Show refresh animation
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise spinning"></i> Refreshing...';
            
            setTimeout(() => {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
            }, 2000);
        }

        // Simulate data refresh
        this.simulateMarketData();
        this.simulatePortfolioUpdate();
        this.simulateTopMovers();
    }

    updatePeriod(period) {
        console.log(`Updating period to: ${period}`);
        // Simulate period change
        this.refreshData();
    }
}

// CSS for spinning animation
const style = document.createElement('style');
style.textContent = `
    .spinning {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new RealtimeDashboard();
    
    // Make it globally accessible for debugging
    window.realtimeDashboard = dashboard;
});