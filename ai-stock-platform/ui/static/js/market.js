/**
 * QuantumVestAI Market JavaScript
 * Last Updated: 2025-06-18 22:10:00
 * Author: daparthi001
 */

// Market search functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize ticker search
    const searchInput = document.getElementById('ticker-search');
    const resultsContainer = document.getElementById('search-results');
    
    if (searchInput && resultsContainer) {
        // Set up event listeners
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            
            if (query.length < 2) {
                resultsContainer.innerHTML = '';
                resultsContainer.classList.add('d-none');
                return;
            }
            
            // Use the API proxy endpoint
            fetch(`/api/v1/ticker-search?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Search request failed');
                    }
                    return response.json();
                })
                .then(data => {
                    displaySearchResults(data, resultsContainer);
                })
                .catch(error => {
                    console.error('Error searching tickers:', error);
                    resultsContainer.innerHTML = `<p class="text-danger">Error searching: ${error.message}</p>`;
                    resultsContainer.classList.remove('d-none');
                });
        }, 300));
        
        // Hide search results when clicking outside
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !resultsContainer.contains(event.target)) {
                resultsContainer.classList.add('d-none');
            }
        });
    }
    
    // Initialize market charts
    initMarketCharts();
    
    // Initialize ticker details if we're on that page
    if (document.querySelector('.ticker-detail-page')) {
        initTickerDetailPage();
    }
});

// Display search results
function displaySearchResults(data, container) {
    // Clear previous results
    container.innerHTML = '';
    
    if (!data.results || data.results.length === 0) {
        container.innerHTML = '<p class="p-2">No results found</p>';
        container.classList.remove('d-none');
        return;
    }
    
    // Create results list
    const resultsList = document.createElement('div');
    resultsList.className = 'list-group';
    
    data.results.forEach(ticker => {
        const item = document.createElement('a');
        item.className = 'list-group-item list-group-item-action';
        item.href = `/stock/${ticker.symbol}`;
        
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <strong>${ticker.symbol}</strong>
                <span class="badge bg-light text-dark">${ticker.exchange}</span>
            </div>
            <small class="text-muted">${ticker.name}</small>
        `;
        
        resultsList.appendChild(item);
    });
    
    container.appendChild(resultsList);
    container.classList.remove('d-none');
}

// Initialize market charts
function initMarketCharts() {
    const indexChartContainer = document.getElementById('index-chart');
    const sectorChartContainer = document.getElementById('sector-chart');
    
    if (indexChartContainer) {
        renderIndexChart(indexChartContainer);
    }
    
    if (sectorChartContainer) {
        renderSectorChart(sectorChartContainer);
    }
}

// Initialize ticker detail page
function initTickerDetailPage() {
    // Get ticker symbol from page
    const tickerSymbol = document.querySelector('.ticker-detail-page').dataset.symbol;
    
    if (!tickerSymbol) {
        console.error('No ticker symbol found on page');
        return;
    }
    
    // Initialize price chart
    const priceChartContainer = document.getElementById('price-chart');
    if (priceChartContainer) {
        renderPriceChart(priceChartContainer, tickerSymbol);
    }
    
    // Initialize indicator tabs
    const indicatorTabs = document.querySelectorAll('.indicator-tab');
    if (indicatorTabs.length) {
        indicatorTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all tabs
                indicatorTabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Get indicator type
                const indicatorType = this.dataset.indicator;
                
                // Update indicator chart
                updateIndicatorChart(tickerSymbol, indicatorType);
            });
        });
        
        // Initialize with first tab
        updateIndicatorChart(tickerSymbol, indicatorTabs[0].dataset.indicator);
    }
    
    // Initialize forecast toggle
    const forecastToggle = document.getElementById('show-forecast');
    if (forecastToggle) {
        forecastToggle.addEventListener('change', function() {
            toggleForecast(this.checked, tickerSymbol);
        });
    }
}

// Helper function for debouncing
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Render market index chart - placeholder
function renderIndexChart(container) {
    // Actual chart implementation would go here
    // Fetch demo index data from the new AI API
    fetch('/api/ai/market-data/SPY')
        .then(response => response.json())
        .then(data => {
            console.log('Index data:', data);
            // Chart rendering code would go here
            container.innerHTML = '<div class="chart-placeholder p-3">Market Index Chart</div>';
        })
        .catch(error => {
            console.error('Error fetching index data:', error);
            container.innerHTML = `<div class="alert alert-danger">Failed to load index data</div>`;
        });
}

// Render sector performance chart - placeholder
function renderSectorChart(container) {
    // Actual chart implementation would go here
    // Fetch demo sector data from the new AI API
    fetch('/api/ai/market-data/QQQ')
        .then(response => response.json())
        .then(data => {
            console.log('Sector data:', data);
            // Chart rendering code would go here
            container.innerHTML = '<div class="chart-placeholder p-3">Sector Performance Chart</div>';
        })
        .catch(error => {
            console.error('Error fetching sector data:', error);
            container.innerHTML = `<div class="alert alert-danger">Failed to load sector data</div>`;
        });
}

// Render price chart - placeholder
function renderPriceChart(container, symbol) {
    // Actual chart implementation would go here
    // Fetch live price data from the new AI API
    fetch(`/api/ai/market-data/${symbol}`)
        .then(response => response.json())
        .then(data => {
            console.log('Price data:', data);
            // Chart rendering code would go here
            container.innerHTML = `<div class="chart-placeholder p-3">Price Chart for ${symbol}</div>`;
        })
        .catch(error => {
            console.error(`Error fetching price data for ${symbol}:`, error);
            container.innerHTML = `<div class="alert alert-danger">Failed to load price data</div>`;
        });
}

// Update indicator chart based on selected indicator
function updateIndicatorChart(symbol, indicatorType) {
    const indicatorChartContainer = document.getElementById('indicator-chart');
    if (!indicatorChartContainer) return;
    
    indicatorChartContainer.innerHTML = '<div class="loading-spinner"></div>';
    
    // Fetch live technical indicator data from the new AI API
    fetch(`/api/ai/technical-data/${symbol}`)
        .then(response => response.json())
        .then(data => {
            console.log(`${indicatorType} data:`, data);
            // Chart rendering code would go here
            indicatorChartContainer.innerHTML = `<div class="chart-placeholder p-3">${indicatorType.toUpperCase()} Chart for ${symbol}</div>`;
        })
        .catch(error => {
            console.error(`Error fetching ${indicatorType} data for ${symbol}:`, error);
            indicatorChartContainer.innerHTML = `<div class="alert alert-danger">Failed to load indicator data</div>`;
        });
}

// Toggle forecast display
function toggleForecast(show, symbol) {
    const forecastContainer = document.getElementById('forecast-container');
    if (!forecastContainer) return;
    
    if (show) {
        forecastContainer.innerHTML = '<div class="loading-spinner"></div>';
        
        // Fetch sentiment data from the new AI API as a placeholder
        fetch(`/api/ai/sentiment/${symbol}`)
            .then(response => response.json())
            .then(data => {
                console.log('Forecast data:', data);
                // Forecast rendering code would go here
                forecastContainer.innerHTML = `<div class="forecast-placeholder p-3">Forecast Data for ${symbol}</div>`;
                forecastContainer.classList.remove('d-none');
            })
            .catch(error => {
                console.error(`Error fetching forecast data for ${symbol}:`, error);
                forecastContainer.innerHTML = `<div class="alert alert-danger">Failed to load forecast data</div>`;
                forecastContainer.classList.remove('d-none');
            });
    } else {
        forecastContainer.classList.add('d-none');
    }}