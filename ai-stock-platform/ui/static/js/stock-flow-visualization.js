/**
 * Stock Flow Visualization Manager
 * Handles interactive stock flow charts, real-time updates, and user interactions
 */

class StockFlowManager {
    constructor() {
        this.selectedStocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN'];
        this.popularStocks = [
            'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 
            'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'SNAP'
        ];
        this.chart = null;
        this.isPlaying = true;
        this.updateInterval = null;
        this.currentVisualization = 'flow';
        this.flowData = new Map();
        this.colors = [
            'rgba(255, 99, 132, 0.8)',   // Red
            'rgba(54, 162, 235, 0.8)',   // Blue
            'rgba(255, 205, 86, 0.8)',   // Yellow
            'rgba(75, 192, 192, 0.8)',   // Teal
            'rgba(153, 102, 255, 0.8)',  // Purple
            'rgba(255, 159, 64, 0.8)',   // Orange
        ];
    }

    init() {
        this.setupEventListeners();
        this.renderStockChips();
        this.renderStatusChips();
        this.initializeChart();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Play/Pause button
        document.getElementById('playPause').addEventListener('click', () => {
            this.togglePlayPause();
        });

        // Refresh button
        document.getElementById('refresh').addEventListener('click', () => {
            this.refreshData();
        });

        // Fullscreen button
        document.getElementById('fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Visualization type changes
        document.querySelectorAll('input[name="vizType"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.currentVisualization = e.target.id.replace('Chart', '').replace('Plot', '');
                    this.updateVisualization();
                }
            });
        });

        // Timeframe changes
        document.getElementById('timeframe').addEventListener('change', (e) => {
            this.updateTimeframe(e.target.value);
        });

        // Auto refresh toggle
        document.getElementById('autoRefresh').addEventListener('change', (e) => {
            this.isPlaying = e.target.checked;
            if (this.isPlaying) {
                this.startRealTimeUpdates();
            } else {
                this.stopRealTimeUpdates();
            }
        });
    }

    renderStockChips() {
        const container = document.getElementById('stock-chips');
        container.innerHTML = '';

        this.popularStocks.forEach(stock => {
            const isSelected = this.selectedStocks.includes(stock);
            const chip = document.createElement('button');
            chip.className = `btn btn-sm stock-chip ${isSelected ? 'btn-primary' : 'btn-outline-secondary'}`;
            chip.textContent = stock;
            chip.onclick = () => this.toggleStock(stock);
            container.appendChild(chip);
        });

        this.updateSelectedCount();
    }

    renderStatusChips() {
        const container = document.getElementById('status-chips');
        container.innerHTML = '';

        this.selectedStocks.forEach((stock, index) => {
            const data = this.generateMockStockData(stock);
            const chip = document.createElement('span');
            chip.className = `badge stock-chip ${data.changePercent >= 0 ? 'bg-success' : 'bg-danger'}`;
            chip.style.borderColor = this.colors[index % this.colors.length];
            chip.innerHTML = `
                ${stock}: $${data.price.toFixed(2)} 
                (${data.changePercent >= 0 ? '↗' : '↘'} ${data.changePercent.toFixed(2)}%)
            `;
            container.appendChild(chip);
        });
    }

    toggleStock(stock) {
        const index = this.selectedStocks.indexOf(stock);
        if (index > -1) {
            this.selectedStocks.splice(index, 1);
        } else if (this.selectedStocks.length < 8) {
            this.selectedStocks.push(stock);
        }

        this.renderStockChips();
        this.renderStatusChips();
        this.updateVisualization();
    }

    updateSelectedCount() {
        document.getElementById('selected-count').textContent = this.selectedStocks.length;
        
        const warning = document.getElementById('no-stocks-warning');
        if (this.selectedStocks.length === 0) {
            warning.classList.remove('d-none');
        } else {
            warning.classList.add('d-none');
        }
    }

    selectStockGroup(group) {
        switch(group) {
            case 'tech':
                this.selectedStocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN'];
                break;
            case 'ev':
                this.selectedStocks = ['TSLA', 'RIVN', 'LCID', 'NIO'];
                break;
        }
        this.renderStockChips();
        this.renderStatusChips();
        this.updateVisualization();
    }

    generateMockStockData(symbol) {
        const basePrice = 100 + Math.random() * 300;
        const change = (Math.random() - 0.5) * 10;
        const changePercent = (change / basePrice) * 100;
        
        // Generate flow data (last 50 data points)
        const flow = Array.from({ length: 50 }, (_, i) => {
            const time = i / 49;
            const wave = Math.sin(time * Math.PI * 4) * 5;
            const trend = (Math.random() - 0.5) * 2;
            const noise = (Math.random() - 0.5) * 1;
            return basePrice + wave + trend + noise;
        });

        return {
            symbol,
            price: basePrice + change,
            change,
            changePercent,
            volume: Math.floor(Math.random() * 10000000) + 1000000,
            flow,
            timestamp: new Date().toISOString(),
            sector: ['Technology', 'Healthcare', 'Finance', 'Energy'][Math.floor(Math.random() * 4)]
        };
    }

    initializeChart() {
        const ctx = document.getElementById('stockFlowChart').getContext('2d');
        
        // Hide loading indicator
        document.getElementById('loadingIndicator').style.display = 'none';
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: this.getChartData(),
            options: this.getChartOptions()
        });
    }

    getChartData() {
        if (this.selectedStocks.length === 0) {
            return { labels: [], datasets: [] };
        }

        switch (this.currentVisualization) {
            case 'flow':
                return this.getFlowChartData();
            case 'scatter':
                return this.getScatterChartData();
            case 'heatmap':
                return this.getHeatmapChartData();
            default:
                return this.getFlowChartData();
        }
    }

    getFlowChartData() {
        const labels = Array.from({ length: 50 }, (_, i) => i);
        
        const datasets = this.selectedStocks.map((stock, index) => {
            const data = this.generateMockStockData(stock);
            return {
                label: stock,
                data: data.flow,
                borderColor: this.colors[index % this.colors.length],
                backgroundColor: this.colors[index % this.colors.length].replace('0.8', '0.1'),
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                tension: 0.4,
                fill: true,
            };
        });

        return { labels, datasets };
    }

    getScatterChartData() {
        const datasets = [{
            label: 'Price vs Volume',
            data: this.selectedStocks.map(stock => {
                const data = this.generateMockStockData(stock);
                return {
                    x: data.volume / 1000000, // Volume in millions
                    y: data.price,
                    symbol: stock,
                    change: data.changePercent
                };
            }),
            backgroundColor: this.selectedStocks.map(stock => {
                const data = this.generateMockStockData(stock);
                return data.changePercent >= 0 ? 'rgba(76, 175, 80, 0.6)' : 'rgba(244, 67, 54, 0.6)';
            }),
            borderColor: this.selectedStocks.map(stock => {
                const data = this.generateMockStockData(stock);
                return data.changePercent >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)';
            }),
            pointRadius: 8,
            pointHoverRadius: 12,
        }];

        return { datasets };
    }

    getHeatmapChartData() {
        const sectorData = {};
        
        this.selectedStocks.forEach(stock => {
            const data = this.generateMockStockData(stock);
            if (!sectorData[data.sector]) {
                sectorData[data.sector] = { count: 0, totalChange: 0 };
            }
            sectorData[data.sector].count++;
            sectorData[data.sector].totalChange += data.changePercent;
        });

        const labels = Object.keys(sectorData);
        const data = labels.map(sector => sectorData[sector].totalChange / sectorData[sector].count);

        return {
            labels,
            datasets: [{
                label: 'Sector Performance (%)',
                data,
                backgroundColor: data.map(value => 
                    value >= 0 ? 'rgba(76, 175, 80, 0.8)' : 'rgba(244, 67, 54, 0.8)'
                ),
                borderColor: data.map(value => 
                    value >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)'
                ),
                borderWidth: 1,
            }]
        };
    }

    getChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: (context) => {
                            if (this.currentVisualization === 'scatter') {
                                return `${context.raw.symbol}: $${context.raw.y.toFixed(2)} (${context.raw.change.toFixed(2)}%)`;
                            }
                            return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                },
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: this.currentVisualization === 'scatter' ? 'Volume (Millions)' : 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        };
    }

    updateVisualization() {
        if (!this.chart) return;

        // Update chart type based on visualization
        let newType = 'line';
        if (this.currentVisualization === 'scatter') {
            newType = 'scatter';
        } else if (this.currentVisualization === 'heatmap') {
            newType = 'bar';
        }

        this.chart.config.type = newType;
        this.chart.data = this.getChartData();
        this.chart.options = this.getChartOptions();
        this.chart.update('active');

        this.updateStats();
    }

    updateStats() {
        document.getElementById('total-stocks').textContent = this.selectedStocks.length;
        
        const gainers = this.selectedStocks.filter(stock => {
            const data = this.generateMockStockData(stock);
            return data.changePercent > 0;
        });
        
        document.getElementById('gainers-count').textContent = gainers.length;
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
    }

    togglePlayPause() {
        this.isPlaying = !this.isPlaying;
        const button = document.getElementById('playPause');
        const icon = button.querySelector('i');
        
        if (this.isPlaying) {
            icon.className = 'fas fa-pause';
            this.startRealTimeUpdates();
        } else {
            icon.className = 'fas fa-play';
            this.stopRealTimeUpdates();
        }

        // Update live indicator
        const liveIndicator = document.getElementById('live-status');
        if (this.isPlaying) {
            liveIndicator.style.display = 'block';
        } else {
            liveIndicator.style.display = 'none';
        }
    }

    refreshData() {
        const button = document.getElementById('refresh');
        const icon = button.querySelector('i');
        
        // Add spinning animation
        icon.classList.add('fa-spin');
        
        // Simulate data refresh
        setTimeout(() => {
            this.renderStatusChips();
            this.updateVisualization();
            icon.classList.remove('fa-spin');
        }, 1000);
    }

    startRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            if (this.isPlaying) {
                this.renderStatusChips();
                this.updateVisualization();
            }
        }, 2000); // Update every 2 seconds

        // Show live indicator
        document.getElementById('live-status').style.display = 'block';
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }

        // Hide live indicator
        document.getElementById('live-status').style.display = 'none';
    }

    toggleFullscreen() {
        const chartContainer = document.querySelector('.stock-flow-visualization');
        
        if (!document.fullscreenElement) {
            chartContainer.requestFullscreen().catch(err => {
                console.error('Error attempting to enable fullscreen:', err);
            });
        } else {
            document.exitFullscreen();
        }
    }

    updateTimeframe(timeframe) {
        console.log(`Updating timeframe to: ${timeframe}`);
        // In a real implementation, this would fetch new data based on timeframe
        this.refreshData();
    }
}

// Global functions for HTML onclick handlers
function selectStockGroup(group) {
    if (window.stockFlowManager) {
        window.stockFlowManager.selectStockGroup(group);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StockFlowManager;
}