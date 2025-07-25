/**
 * QuantumVestAI Advanced Data Visualization
 * Interactive charts and graphs with AI predictions
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumCharts {
    constructor(options = {}) {
        this.options = {
            defaultTheme: 'dark',
            animations: true,
            responsive: true,
            enableRealtime: true,
            updateInterval: 5000,
            ...options
        };
        
        this.charts = new Map();
        this.realTimeSubscriptions = new Map();
        this.chartThemes = this.initializeThemes();
        
        this.init();
    }

    init() {
        this.loadChartLibraries();
        this.setupThemeIntegration();
        this.setupRealtimeUpdates();
        this.createAdvancedChartTypes();
    }

    async loadChartLibraries() {
        // Check if Chart.js is already loaded
        if (typeof Chart === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js');
        }
        
        // Load additional Chart.js plugins
        await Promise.all([
            this.loadScript('https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js'),
            this.loadScript('https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js'),
            this.loadScript('https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js')
        ]);
        
        // Register plugins
        if (typeof Chart !== 'undefined') {
            Chart.register(
                ChartjsPluginZoom,
                ChartjsPluginAnnotation
            );
        }
    }

    async loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    initializeThemes() {
        return {
            dark: {
                backgroundColor: 'rgba(26, 26, 26, 0.8)',
                textColor: '#ffffff',
                gridColor: 'rgba(255, 255, 255, 0.1)',
                borderColor: 'rgba(255, 255, 255, 0.2)',
                colors: {
                    primary: '#4facfe',
                    secondary: '#00f2fe',
                    success: '#43e97b',
                    danger: '#ff6b6b',
                    warning: '#feca57',
                    info: '#667eea'
                },
                gradients: {
                    bullish: ['#43e97b', '#38f9d7'],
                    bearish: ['#ff6b6b', '#feca57'],
                    neutral: ['#4facfe', '#00f2fe'],
                    volume: ['#667eea', '#764ba2']
                }
            },
            light: {
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                textColor: '#333333',
                gridColor: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgba(0, 0, 0, 0.2)',
                colors: {
                    primary: '#2c5aa0',
                    secondary: '#0066cc',
                    success: '#28a745',
                    danger: '#dc3545',
                    warning: '#ffc107',
                    info: '#17a2b8'
                },
                gradients: {
                    bullish: ['#28a745', '#20c997'],
                    bearish: ['#dc3545', '#fd7e14'],
                    neutral: ['#007bff', '#6610f2'],
                    volume: ['#6f42c1', '#e83e8c']
                }
            }
        };
    }

    setupThemeIntegration() {
        // Listen for theme changes
        window.addEventListener('languageChanged', () => {
            this.updateAllCharts();
        });
        
        // Listen for theme changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    const newTheme = document.documentElement.getAttribute('data-theme');
                    this.updateChartsTheme(newTheme);
                }
            });
        });
        
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    setupRealtimeUpdates() {
        if (!this.options.enableRealtime) return;
        
        // Setup WebSocket connection for real-time data
        this.setupWebSocketConnection();
        
        // Fallback to polling if WebSocket is not available
        setInterval(() => {
            this.updateRealTimeCharts();
        }, this.options.updateInterval);
    }

    setupWebSocketConnection() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const clientId = this.options.clientId || 'market-data';
            const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('QuantumCharts: WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeData(data);
            };
            
            this.websocket.onclose = () => {
                console.log('QuantumCharts: WebSocket disconnected');
                // Attempt reconnection after 5 seconds
                setTimeout(() => this.setupWebSocketConnection(), 5000);
            };
            
        } catch (error) {
            console.error('QuantumCharts: WebSocket setup failed:', error);
        }
    }

    createAdvancedChartTypes() {
        // Register custom chart types
        this.registerCandlestickChart();
        this.registerTechnicalIndicatorChart();
        this.registerCorrelationMatrix();
        this.registerSentimentChart();
        this.registerPortfolioAllocation();
    }

    // Main chart creation method
    createChart(containerId, type, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`QuantumCharts: Container ${containerId} not found`);
            return null;
        }

        // Create canvas if it doesn't exist
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            container.appendChild(canvas);
        }

        const ctx = canvas.getContext('2d');
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const theme = this.chartThemes[currentTheme];

        // Merge default options with theme and user options
        const chartOptions = this.mergeChartOptions(type, theme, options);
        
        // Create chart based on type
        let chart;
        switch (type) {
            case 'candlestick':
                chart = this.createCandlestickChart(ctx, data, chartOptions);
                break;
            case 'technical':
                chart = this.createTechnicalChart(ctx, data, chartOptions);
                break;
            case 'correlation':
                chart = this.createCorrelationChart(ctx, data, chartOptions);
                break;
            case 'sentiment':
                chart = this.createSentimentChart(ctx, data, chartOptions);
                break;
            case 'portfolio':
                chart = this.createPortfolioChart(ctx, data, chartOptions);
                break;
            case 'prediction':
                chart = this.createPredictionChart(ctx, data, chartOptions);
                break;
            default:
                chart = this.createStandardChart(ctx, type, data, chartOptions);
        }

        if (chart) {
            this.charts.set(containerId, chart);
            this.addChartInteractions(chart, containerId);
        }

        return chart;
    }

    mergeChartOptions(type, theme, userOptions) {
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: this.options.animations ? 750 : 0,
                easing: 'easeInOutQuart'
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: theme.textColor,
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: theme.backgroundColor,
                    titleColor: theme.textColor,
                    bodyColor: theme.textColor,
                    borderColor: theme.borderColor,
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: (context) => this.formatTooltipLabel(context)
                    }
                }
            },
            scales: this.getScaleOptions(type, theme)
        };

        return this.deepMerge(baseOptions, userOptions);
    }

    getScaleOptions(type, theme) {
        const scales = {
            x: {
                grid: {
                    color: theme.gridColor,
                    lineWidth: 1
                },
                ticks: {
                    color: theme.textColor,
                    maxTicksLimit: 10
                }
            },
            y: {
                grid: {
                    color: theme.gridColor,
                    lineWidth: 1
                },
                ticks: {
                    color: theme.textColor,
                    callback: (value) => this.formatYAxisLabel(value, type)
                }
            }
        };

        // Special scale configurations for different chart types
        switch (type) {
            case 'candlestick':
            case 'technical':
                scales.x.type = 'time';
                scales.x.time = {
                    displayFormats: {
                        hour: 'HH:mm',
                        day: 'MMM DD',
                        week: 'MMM DD',
                        month: 'MMM YYYY'
                    }
                };
                break;
            case 'correlation':
                scales.x.type = 'category';
                scales.y.type = 'category';
                break;
        }

        return scales;
    }

    // Specific chart creation methods
    createCandlestickChart(ctx, data, options) {
        const processedData = this.processCandlestickData(data);
        
        return new Chart(ctx, {
            type: 'line', // We'll simulate candlesticks with multiple datasets
            data: {
                labels: processedData.labels,
                datasets: [
                    {
                        label: 'Price',
                        data: processedData.close,
                        borderColor: this.getCurrentTheme().colors.primary,
                        backgroundColor: this.createGradient(ctx, this.getCurrentTheme().gradients.neutral),
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Volume',
                        data: processedData.volume,
                        type: 'bar',
                        yAxisID: 'volume',
                        backgroundColor: this.getCurrentTheme().colors.info + '40'
                    }
                ]
            },
            options: {
                ...options,
                scales: {
                    ...options.scales,
                    volume: {
                        type: 'linear',
                        position: 'right',
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: this.getCurrentTheme().textColor
                        }
                    }
                }
            }
        });
    }

    createTechnicalChart(ctx, data, options) {
        const processedData = this.processTechnicalData(data);
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: processedData.labels,
                datasets: [
                    {
                        label: 'Price',
                        data: processedData.price,
                        borderColor: this.getCurrentTheme().colors.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 2
                    },
                    {
                        label: 'SMA 20',
                        data: processedData.sma20,
                        borderColor: this.getCurrentTheme().colors.warning,
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'SMA 50',
                        data: processedData.sma50,
                        borderColor: this.getCurrentTheme().colors.info,
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        borderDash: [10, 5]
                    },
                    {
                        label: 'Bollinger Upper',
                        data: processedData.bollingerUpper,
                        borderColor: this.getCurrentTheme().colors.success + '80',
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        fill: '+1'
                    },
                    {
                        label: 'Bollinger Lower',
                        data: processedData.bollingerLower,
                        borderColor: this.getCurrentTheme().colors.success + '80',
                        backgroundColor: this.getCurrentTheme().colors.success + '20',
                        borderWidth: 1,
                        fill: false
                    }
                ]
            },
            options: {
                ...options,
                plugins: {
                    ...options.plugins,
                    annotation: {
                        annotations: this.createTechnicalAnnotations(processedData)
                    }
                }
            }
        });
    }

    createCorrelationChart(ctx, data, options) {
        const processedData = this.processCorrelationData(data);
        
        return new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Correlation Matrix',
                    data: processedData.points,
                    backgroundColor: (context) => {
                        const value = context.parsed.v;
                        return this.getCorrelationColor(value);
                    },
                    pointRadius: 15,
                    pointHoverRadius: 20
                }]
            },
            options: {
                ...options,
                scales: {
                    x: {
                        type: 'category',
                        labels: processedData.labels,
                        grid: { display: false },
                        ticks: { color: this.getCurrentTheme().textColor }
                    },
                    y: {
                        type: 'category',
                        labels: processedData.labels,
                        grid: { display: false },
                        ticks: { color: this.getCurrentTheme().textColor }
                    }
                },
                plugins: {
                    ...options.plugins,
                    tooltip: {
                        ...options.plugins.tooltip,
                        callbacks: {
                            title: () => '',
                            label: (context) => {
                                const x = processedData.labels[context.parsed.x];
                                const y = processedData.labels[context.parsed.y];
                                const correlation = context.parsed.v.toFixed(3);
                                return `${x} vs ${y}: ${correlation}`;
                            }
                        }
                    }
                }
            }
        });
    }

    createSentimentChart(ctx, data, options) {
        const processedData = this.processSentimentData(data);
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Bullish', 'Bearish', 'Neutral'],
                datasets: [{
                    data: [processedData.bullish, processedData.bearish, processedData.neutral],
                    backgroundColor: [
                        this.getCurrentTheme().colors.success,
                        this.getCurrentTheme().colors.danger,
                        this.getCurrentTheme().colors.info
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                ...options,
                cutout: '60%',
                plugins: {
                    ...options.plugins,
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: this.getCurrentTheme().textColor,
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    createPortfolioChart(ctx, data, options) {
        const processedData = this.processPortfolioData(data);
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: processedData.labels,
                datasets: [{
                    data: processedData.values,
                    backgroundColor: processedData.colors,
                    borderWidth: 2,
                    borderColor: this.getCurrentTheme().backgroundColor,
                    hoverOffset: 8
                }]
            },
            options: {
                ...options,
                cutout: '50%',
                plugins: {
                    ...options.plugins,
                    legend: {
                        position: 'right',
                        labels: {
                            color: this.getCurrentTheme().textColor,
                            padding: 15,
                            usePointStyle: true,
                            generateLabels: (chart) => {
                                const data = chart.data;
                                return data.labels.map((label, i) => ({
                                    text: `${label}: ${((data.datasets[0].data[i] / data.datasets[0].data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%`,
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    strokeStyle: data.datasets[0].backgroundColor[i],
                                    pointStyle: 'circle'
                                }));
                            }
                        }
                    },
                    tooltip: {
                        ...options.plugins.tooltip,
                        callbacks: {
                            label: (context) => {
                                const label = context.label;
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    createPredictionChart(ctx, data, options) {
        const processedData = this.processPredictionData(data);
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: processedData.labels,
                datasets: [
                    {
                        label: 'Historical Price',
                        data: processedData.historical,
                        borderColor: this.getCurrentTheme().colors.primary,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 1
                    },
                    {
                        label: 'AI Prediction',
                        data: processedData.prediction,
                        borderColor: this.getCurrentTheme().colors.warning,
                        backgroundColor: this.getCurrentTheme().colors.warning + '20',
                        borderWidth: 2,
                        borderDash: [10, 5],
                        fill: false,
                        pointRadius: 3
                    },
                    {
                        label: 'Confidence Interval',
                        data: processedData.confidenceUpper,
                        borderColor: 'transparent',
                        backgroundColor: this.getCurrentTheme().colors.warning + '10',
                        fill: '+1',
                        pointRadius: 0
                    },
                    {
                        label: 'Confidence Lower',
                        data: processedData.confidenceLower,
                        borderColor: 'transparent',
                        backgroundColor: 'transparent',
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                ...options,
                plugins: {
                    ...options.plugins,
                    annotation: {
                        annotations: {
                            predictionLine: {
                                type: 'line',
                                scaleID: 'x',
                                value: processedData.predictionStart,
                                borderColor: this.getCurrentTheme().colors.info,
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {
                                    content: 'Prediction Start',
                                    enabled: true,
                                    position: 'start'
                                }
                            }
                        }
                    }
                }
            }
        });
    }

    createStandardChart(ctx, type, data, options) {
        return new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
    }

    // Data processing methods
    processCandlestickData(data) {
        // Convert raw market data to chart format
        return {
            labels: data.map(d => new Date(d.timestamp)),
            open: data.map(d => d.open),
            high: data.map(d => d.high),
            low: data.map(d => d.low),
            close: data.map(d => d.close),
            volume: data.map(d => d.volume)
        };
    }

    processTechnicalData(data) {
        // Calculate technical indicators
        const prices = data.map(d => d.close);
        
        return {
            labels: data.map(d => new Date(d.timestamp)),
            price: prices,
            sma20: this.calculateSMA(prices, 20),
            sma50: this.calculateSMA(prices, 50),
            bollingerUpper: this.calculateBollingerBands(prices, 20).upper,
            bollingerLower: this.calculateBollingerBands(prices, 20).lower
        };
    }

    processCorrelationData(data) {
        const symbols = Object.keys(data);
        const points = [];
        
        symbols.forEach((symbol1, i) => {
            symbols.forEach((symbol2, j) => {
                points.push({
                    x: i,
                    y: j,
                    v: data[symbol1][symbol2] || 0
                });
            });
        });
        
        return { labels: symbols, points };
    }

    processSentimentData(data) {
        const total = data.bullish + data.bearish + data.neutral;
        return {
            bullish: (data.bullish / total) * 100,
            bearish: (data.bearish / total) * 100,
            neutral: (data.neutral / total) * 100
        };
    }

    processPortfolioData(data) {
        const colors = this.generateColorPalette(data.length);
        return {
            labels: data.map(d => d.symbol),
            values: data.map(d => d.value),
            colors: colors
        };
    }

    processPredictionData(data) {
        const splitIndex = Math.floor(data.historical.length * 0.8);
        const predictionStart = data.historical[splitIndex].timestamp;
        
        return {
            labels: [...data.historical.map(d => d.timestamp), ...data.prediction.map(d => d.timestamp)],
            historical: data.historical.map(d => d.price),
            prediction: [...Array(splitIndex).fill(null), ...data.prediction.map(d => d.price)],
            confidenceUpper: [...Array(splitIndex).fill(null), ...data.prediction.map(d => d.upper)],
            confidenceLower: [...Array(splitIndex).fill(null), ...data.prediction.map(d => d.lower)],
            predictionStart: predictionStart
        };
    }

    // Technical analysis calculations
    calculateSMA(prices, period) {
        const sma = [];
        for (let i = 0; i < prices.length; i++) {
            if (i < period - 1) {
                sma.push(null);
            } else {
                const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
                sma.push(sum / period);
            }
        }
        return sma;
    }

    calculateBollingerBands(prices, period, multiplier = 2) {
        const sma = this.calculateSMA(prices, period);
        const upper = [];
        const lower = [];
        
        for (let i = 0; i < prices.length; i++) {
            if (i < period - 1) {
                upper.push(null);
                lower.push(null);
            } else {
                const slice = prices.slice(i - period + 1, i + 1);
                const mean = sma[i];
                const variance = slice.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / period;
                const stdDev = Math.sqrt(variance);
                
                upper.push(mean + (stdDev * multiplier));
                lower.push(mean - (stdDev * multiplier));
            }
        }
        
        return { upper, lower };
    }

    // Helper methods
    getCurrentTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        return this.chartThemes[currentTheme];
    }

    createGradient(ctx, colors) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, colors[0] + '80');
        gradient.addColorStop(1, colors[1] + '20');
        return gradient;
    }

    getCorrelationColor(value) {
        const theme = this.getCurrentTheme();
        if (value > 0.7) return theme.colors.success;
        if (value > 0.3) return theme.colors.warning;
        if (value > -0.3) return theme.colors.info;
        if (value > -0.7) return theme.colors.warning;
        return theme.colors.danger;
    }

    generateColorPalette(count) {
        const theme = this.getCurrentTheme();
        const baseColors = Object.values(theme.colors);
        const colors = [];
        
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        
        return colors;
    }

    formatTooltipLabel(context) {
        const value = context.parsed.y;
        const datasetLabel = context.dataset.label;
        
        if (datasetLabel.includes('$') || datasetLabel.includes('Price')) {
            return `${datasetLabel}: $${value.toLocaleString()}`;
        } else if (datasetLabel.includes('%')) {
            return `${datasetLabel}: ${value.toFixed(2)}%`;
        } else if (datasetLabel.includes('Volume')) {
            return `${datasetLabel}: ${this.formatVolume(value)}`;
        }
        
        return `${datasetLabel}: ${value.toLocaleString()}`;
    }

    formatYAxisLabel(value, type) {
        switch (type) {
            case 'candlestick':
            case 'technical':
            case 'prediction':
                return '$' + value.toLocaleString();
            case 'sentiment':
            case 'correlation':
                return value.toFixed(2);
            case 'portfolio':
                return '$' + this.formatVolume(value);
            default:
                return value.toLocaleString();
        }
    }

    formatVolume(value) {
        if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';
        if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
        if (value >= 1e3) return (value / 1e3).toFixed(1) + 'K';
        return value.toString();
    }

    createTechnicalAnnotations(data) {
        return {
            support: {
                type: 'line',
                yMin: Math.min(...data.price) * 0.98,
                yMax: Math.min(...data.price) * 0.98,
                borderColor: this.getCurrentTheme().colors.success,
                borderWidth: 2,
                borderDash: [5, 5],
                label: {
                    content: 'Support',
                    enabled: true
                }
            },
            resistance: {
                type: 'line',
                yMin: Math.max(...data.price) * 1.02,
                yMax: Math.max(...data.price) * 1.02,
                borderColor: this.getCurrentTheme().colors.danger,
                borderWidth: 2,
                borderDash: [5, 5],
                label: {
                    content: 'Resistance',
                    enabled: true
                }
            }
        };
    }

    // Real-time update methods
    handleRealtimeData(data) {
        if (data.type === 'price_update') {
            this.updatePriceCharts(data);
        } else if (data.type === 'sentiment_update') {
            this.updateSentimentCharts(data);
        } else if (data.type === 'portfolio_update') {
            this.updatePortfolioCharts(data);
        }
    }

    updateRealTimeCharts() {
        // Fallback method to update charts via API polling
        this.charts.forEach((chart, containerId) => {
            if (this.realTimeSubscriptions.has(containerId)) {
                this.fetchLatestData(containerId).then(data => {
                    this.updateChartData(chart, data);
                });
            }
        });
    }

    updatePriceCharts(data) {
        this.charts.forEach((chart, containerId) => {
            if (chart.config.type === 'line' && chart.data.datasets[0].label === 'Price') {
                this.addDataPoint(chart, data.timestamp, data.price);
            }
        });
    }

    updateSentimentCharts(data) {
        this.charts.forEach((chart, containerId) => {
            if (chart.config.type === 'doughnut' && chart.data.labels.includes('Bullish')) {
                const processed = this.processSentimentData(data);
                chart.data.datasets[0].data = [processed.bullish, processed.bearish, processed.neutral];
                chart.update('none');
            }
        });
    }

    updatePortfolioCharts(data) {
        this.charts.forEach((chart, containerId) => {
            if (chart.config.type === 'doughnut' && !chart.data.labels.includes('Bullish')) {
                const processed = this.processPortfolioData(data);
                chart.data.labels = processed.labels;
                chart.data.datasets[0].data = processed.values;
                chart.update('active');
            }
        });
    }

    addDataPoint(chart, timestamp, value) {
        const maxDataPoints = 100; // Limit data points for performance
        
        chart.data.labels.push(new Date(timestamp));
        chart.data.datasets[0].data.push(value);
        
        // Remove old data points
        if (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets.forEach(dataset => dataset.data.shift());
        }
        
        chart.update('none'); // No animation for real-time updates
    }

    updateChartData(chart, newData) {
        // Update chart with new data
        chart.data = newData;
        chart.update('active');
    }

    async fetchLatestData(containerId) {
        try {
            const response = await fetch(`/api/chart-data/${containerId}`);
            return await response.json();
        } catch (error) {
            console.error('QuantumCharts: Failed to fetch latest data:', error);
            return null;
        }
    }

    // Chart interaction methods
    addChartInteractions(chart, containerId) {
        const canvas = chart.canvas;
        
        // Add zoom and pan functionality
        chart.options.plugins.zoom = {
            zoom: {
                wheel: {
                    enabled: true,
                },
                pinch: {
                    enabled: true
                },
                mode: 'x',
            },
            pan: {
                enabled: true,
                mode: 'x',
            }
        };
        
        // Add click handlers
        canvas.addEventListener('click', (event) => {
            const points = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
            if (points.length) {
                this.handleChartClick(chart, points[0], containerId);
            }
        });
        
        // Add double-click to reset zoom
        canvas.addEventListener('dblclick', () => {
            chart.resetZoom();
        });
    }

    handleChartClick(chart, point, containerId) {
        const datasetIndex = point.datasetIndex;
        const index = point.index;
        const value = chart.data.datasets[datasetIndex].data[index];
        const label = chart.data.labels[index];
        
        // Emit custom event for chart interactions
        window.dispatchEvent(new CustomEvent('chartPointClicked', {
            detail: {
                containerId,
                value,
                label,
                datasetIndex,
                index
            }
        }));
    }

    // Theme update methods
    updateChartsTheme(themeName) {
        const theme = this.chartThemes[themeName];
        
        this.charts.forEach((chart) => {
            this.updateChartTheme(chart, theme);
        });
    }

    updateChartTheme(chart, theme) {
        // Update chart colors based on theme
        if (chart.options.plugins.legend) {
            chart.options.plugins.legend.labels.color = theme.textColor;
        }
        
        if (chart.options.plugins.tooltip) {
            chart.options.plugins.tooltip.backgroundColor = theme.backgroundColor;
            chart.options.plugins.tooltip.titleColor = theme.textColor;
            chart.options.plugins.tooltip.bodyColor = theme.textColor;
            chart.options.plugins.tooltip.borderColor = theme.borderColor;
        }
        
        if (chart.options.scales) {
            Object.values(chart.options.scales).forEach(scale => {
                if (scale.grid) scale.grid.color = theme.gridColor;
                if (scale.ticks) scale.ticks.color = theme.textColor;
            });
        }
        
        chart.update('none');
    }

    updateAllCharts() {
        this.charts.forEach((chart) => {
            chart.update('active');
        });
    }

    // Subscription management
    subscribeToRealtime(containerId) {
        this.realTimeSubscriptions.set(containerId, true);
    }

    unsubscribeFromRealtime(containerId) {
        this.realTimeSubscriptions.delete(containerId);
    }

    // Chart management
    destroyChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart) {
            chart.destroy();
            this.charts.delete(containerId);
            this.unsubscribeFromRealtime(containerId);
        }
    }

    destroyAllCharts() {
        this.charts.forEach((chart, containerId) => {
            this.destroyChart(containerId);
        });
    }

    // Utility methods
    deepMerge(target, source) {
        const output = Object.assign({}, target);
        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target))
                        Object.assign(output, { [key]: source[key] });
                    else
                        output[key] = this.deepMerge(target[key], source[key]);
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        return output;
    }

    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }

    // Cleanup
    destroy() {
        this.destroyAllCharts();
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Initialize QuantumCharts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.quantumCharts = new QuantumCharts();
    
    // Expose chart creation method globally
    window.createQuantumChart = (containerId, type, data, options) => {
        return window.quantumCharts.createChart(containerId, type, data, options);
    };
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumCharts;
}