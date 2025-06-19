/**
 * Dashboard Controller
 * Created: 2025-06-19 19:01:49
 * Author: daparthi001
 */
import apiClient from '../services/api-client';

class DashboardController {
  constructor() {
    this.init();
  }

  async init() {
    try {
      await this.loadDashboardData();
    } catch (error) {
      console.error('Failed to load dashboard data', error);
      this.showError('Failed to load dashboard data. Please try again later.');
    }
  }

  async loadDashboardData() {
    // Show loading state
    this.showLoading(true);

    try {
      // Load data in parallel
      const [marketOverview, trendingStocks] = await Promise.all([
        this.loadMarketOverview(),
        this.loadTrendingStocks()
      ]);

      // Update DOM with loaded data
      this.updateMarketOverview(marketOverview);
      this.updateTrendingStocks(trendingStocks);

      // Load watchlists if user is authenticated
      if (apiClient.isAuthenticated()) {
        const watchlists = await this.loadWatchlists();
        this.updateWatchlists(watchlists);
      }
    } finally {
      // Hide loading state
      this.showLoading(false);
    }
  }

  async loadMarketOverview() {
    try {
      const response = await apiClient.getMarketOverview();
      
      if (response.status === 'success') {
        return response.data;
      } else {
        throw new Error('Failed to load market overview');
      }
    } catch (error) {
      console.error('Failed to load market overview', error);
      // Return mock data as fallback
      return this.getMockMarketOverview();
    }
  }

  async loadTrendingStocks() {
    try {
      const response = await apiClient.getTrendingStocks();
      
      if (response.status === 'success') {
        return response.data;
      } else {
        throw new Error('Failed to load trending stocks');
      }
    } catch (error) {
      console.error('Failed to load trending stocks', error);
      // Return mock data as fallback
      return this.getMockTrendingStocks();
    }
  }

  async loadWatchlists() {
    try {
      const response = await apiClient.getWatchlists();
      
      if (response.status === 'success') {
        return response.data;
      } else {
        throw new Error('Failed to load watchlists');
      }
    } catch (error) {
      console.error('Failed to load watchlists', error);
      return [];
    }
  }

  updateMarketOverview(marketData) {
    // Get DOM elements
    const marketStatusElement = document.getElementById('market-status');
    const indicesContainer = document.getElementById('market-indices');
    const sectorsContainer = document.getElementById('market-sectors');
    
    if (!marketData) return;
    
    // Update market status
    if (marketStatusElement && marketData.market_sentiment) {
      marketStatusElement.textContent = marketData.market_sentiment.toUpperCase();
      marketStatusElement.className = `badge badge-${this.getSentimentClass(marketData.market_sentiment)}`;
    }
    
    // Update indices
    if (indicesContainer && marketData.indices) {
      indicesContainer.innerHTML = marketData.indices
        .map(index => `
          <div class="market-index">
            <div class="index-name">${index.name}</div>
            <div class="index-value">${index.value.toLocaleString()}</div>
            <div class="index-change ${index.change_percent >= 0 ? 'positive' : 'negative'}">
              ${index.change_percent >= 0 ? '+' : ''}${index.change_percent.toFixed(2)}%
            </div>
          </div>
        `)
        .join('');
    }
    
    // Update sectors
    if (sectorsContainer && marketData.sectors) {
      sectorsContainer.innerHTML = marketData.sectors
        .map(sector => `
          <div class="sector-item">
            <div class="sector-name">${sector.name}</div>
            <div class="sector-bar-container">
              <div class="sector-bar ${sector.change_percent >= 0 ? 'positive' : 'negative'}" 
                  style="width: ${Math.abs(sector.change_percent * 10)}%"></div>
            </div>
            <div class="sector-change ${sector.change_percent >= 0 ? 'positive' : 'negative'}">
              ${sector.change_percent >= 0 ? '+' : ''}${sector.change_percent.toFixed(2)}%
            </div>
          </div>
        `)
        .join('');
    }
    
    // Update last updated timestamp
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement && marketData.date) {
      const date = new Date(marketData.date);
      lastUpdatedElement.textContent = `Last updated: ${date.toLocaleString()}`;
    }
  }

  updateTrendingStocks(stocks) {
    const trendingStocksContainer = document.getElementById('trending-stocks');
    
    if (!trendingStocksContainer || !stocks) return;
    
    trendingStocksContainer.innerHTML = stocks
      .map(stock => `
        <div class="stock-card">
          <div class="stock-header">
            <div class="stock-symbol">${stock.symbol}</div>
            <div class="stock-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}">
              ${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%
            </div>
          </div>
          <div class="stock-name">${stock.name}</div>
          <div class="stock-price">$${stock.price.toLocaleString()}</div>
          <div class="stock-actions">
            <button class="btn btn-sm btn-outline stock-action-btn" onclick="window.location.href='/stocks/${stock.symbol}'">
              <i class="fa fa-chart-line"></i> View
            </button>
            <button class="btn btn-sm btn-outline stock-action-btn add-to-watchlist" data-symbol="${stock.symbol}">
              <i class="fa fa-plus"></i> Add
            </button>
          </div>
        </div>
      `)
      .join('');
    
    // Add event listeners to watchlist buttons
    const addButtons = document.querySelectorAll('.add-to-watchlist');
    addButtons.forEach(button => {
      button.addEventListener('click', () => {
        const symbol = button.getAttribute('data-symbol');
        this.addToWatchlist(symbol);
      });
    });
  }

  updateWatchlists(watchlists) {
    const watchlistsContainer = document.getElementById('watchlists');
    
    if (!watchlistsContainer || !watchlists || watchlists.length === 0) {
      // No watchlists, show empty state
      if (watchlistsContainer) {
        watchlistsContainer.innerHTML = `
          <div class="empty-state">
            <i class="fa fa-star"></i>
            <p>You don't have any watchlists yet</p>
            <button class="btn btn-primary" onclick="window.location.href='/watchlist/create'">
              Create Watchlist
            </button>
          </div>
        `;
      }
      return;
    }
    
    // Show first watchlist
    const watchlist = watchlists[0];
    
    watchlistsContainer.innerHTML = `
      <div class="watchlist-header">
        <h3>${watchlist.name}</h3>
        <a href="/watchlist/${watchlist.id}" class="btn btn-sm btn-link">View All</a>
      </div>
      <div class="watchlist-stocks">
        ${watchlist.stocks.length > 0 
          ? watchlist.stocks.map(stock => `
            <div class="watchlist-stock">
              <div class="stock-info">
                <div class="stock-symbol">${stock.symbol}</div>
                <div class="stock-name">${stock.name}</div>
              </div>
              <div class="stock-price">$${stock.price.toLocaleString()}</div>
              <div class="stock-change ${stock.change_percent >= 0 ? 'positive' : 'negative'}">
                ${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%
              </div>
            </div>
          `).join('')
          : '<div class="empty-state">No stocks in this watchlist</div>'
        }
      </div>
    `;
  }

  async addToWatchlist(symbol) {
    try {
      // If user is not authenticated, redirect to login
      if (!apiClient.isAuthenticated()) {
        window.location.href = `/login?redirect=/stocks/${symbol}`;
        return;
      }
      
      // Get user watchlists
      const response = await apiClient.getWatchlists();
      
      if (response.status === 'success' && response.data.length > 0) {
        // Add to first watchlist
        const watchlistId = response.data[0].id;
        await apiClient.post(`/api/v1/watchlists/${watchlistId}/add`, { symbol });
        
        // Show success notification
        this.showNotification('Stock added to watchlist', 'success');
        
        // Reload watchlists
        const watchlists = await this.loadWatchlists();
        this.updateWatchlists(watchlists);
      } else {
        // No watchlists, create one first
        const createResponse = await apiClient.post('/api/v1/watchlists', { name: 'My Watchlist' });
        
        if (createResponse.status === 'success') {
          const watchlistId = createResponse.data.id;
          await apiClient.post(`/api/v1/watchlists/${watchlistId}/add`, { symbol });
          
          // Show success notification
          this.showNotification('Watchlist created and stock added', 'success');
          
          // Reload watchlists
          const watchlists = await this.loadWatchlists();
          this.updateWatchlists(watchlists);
        } else {
          throw new Error('Failed to create watchlist');
        }
      }
    } catch (error) {
      console.error('Failed to add stock to watchlist', error);
      this.showNotification('Failed to add stock to watchlist', 'error');
    }
  }

  showLoading(isLoading) {
    const loadingElement = document.getElementById('dashboard-loading');
    const contentElement = document.getElementById('dashboard-content');
    
    if (loadingElement) {
      loadingElement.style.display = isLoading ? 'flex' : 'none';
    }
    
    if (contentElement) {
      contentElement.style.display = isLoading ? 'none' : 'block';
    }
  }

  showError(message) {
    const errorElement = document.getElementById('dashboard-error');
    
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
    }
  }

  showNotification(message, type = 'info') {
    const notificationElement = document.createElement('div');
    notificationElement.className = `notification notification-${type}`;
    notificationElement.textContent = message;
    
    document.body.appendChild(notificationElement);
    
    // Show notification
    setTimeout(() => {
      notificationElement.classList.add('show');
    }, 100);
    
    // Hide and remove notification after 3 seconds
    setTimeout(() => {
      notificationElement.classList.remove('show');
      
      // Remove from DOM after animation
      setTimeout(() => {
        document.body.removeChild(notificationElement);
      }, 300);
    }, 3000);
  }

  getSentimentClass(sentiment) {
    switch (sentiment.toLowerCase()) {
      case 'bullish':
        return 'success';
      case 'bearish':
        return 'danger';
      case 'neutral':
        return 'warning';
      default:
        return 'secondary';
    }
  }

  // Mock data for fallbacks
  getMockMarketOverview() {
    return {
      date: new Date().toISOString(),
      market_sentiment: "bullish",
      volatility_index: 15.3,
      indices: [
        { name: "S&P 500", value: 5421.53, change_percent: 0.8 },
        { name: "Nasdaq", value: 17658.23, change_percent: 1.2 },
        { name: "Dow Jones", value: 39875.12, change_percent: 0.5 }
      ],
      sectors: [
        { name: "Technology", change_percent: 1.4 },
        { name: "Healthcare", change_percent: 0.3 },
        { name: "Finance", change_percent: 0.7 },
        { name: "Energy", change_percent: -0.2 },
        { name: "Consumer Staples", change_percent: 0.1 }
      ]
    };
  }

  getMockTrendingStocks() {
    return [
      { symbol: "AAPL", name: "Apple Inc.", price: 198.45, change_percent: 2.1 },
      { symbol: "MSFT", name: "Microsoft Corporation", price: 425.63, change_percent: 1.8 },
      { symbol: "AMZN", name: "Amazon.com Inc.", price: 187.12, change_percent: 1.5 },
      { symbol: "GOOGL", name: "Alphabet Inc.", price: 176.89, change_percent: 1.2 },
      { symbol: "NVDA", name: "NVIDIA Corporation", price: 1024.78, change_percent: 3.2 }
    ];
  }
}

// Initialize controller when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new DashboardController();
});