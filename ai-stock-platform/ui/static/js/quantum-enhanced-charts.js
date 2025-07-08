"""
Enhanced Interactive Visualization Components
Created: 2025-01-09
Author: AI Assistant for QuantumVestAI
"""

// Enhanced Interactive Chart Component
class QuantumInteractiveChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            theme: 'quantum',
            responsive: true,
            interactive: true,
            realtime: false,
            ...options
        };
        this.chart = null;
        this.data = null;
        this.init();
    }

    init() {
        this.setupContainer();
        this.loadPlotly();
    }

    setupContainer() {
        this.container.innerHTML = `
            <div class="quantum-chart-container">
                <div class="chart-header">
                    <div class="chart-title">${this.options.title || 'Stock Analysis'}</div>
                    <div class="chart-controls">
                        <button class="chart-btn" data-action="fullscreen">⛶</button>
                        <button class="chart-btn" data-action="reset">↻</button>
                        <button class="chart-btn" data-action="export">📊</button>
                    </div>
                </div>
                <div class="chart-canvas" id="${this.container.id}-canvas"></div>
                <div class="chart-footer">
                    <div class="chart-info">
                        <span class="data-points">Data Points: <span id="data-count">0</span></span>
                        <span class="last-update">Last Update: <span id="last-update">Never</span></span>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.container.querySelectorAll('.chart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleAction(action);
            });
        });
    }

    handleAction(action) {
        switch(action) {
            case 'fullscreen':
                this.toggleFullscreen();
                break;
            case 'reset':
                this.resetZoom();
                break;
            case 'export':
                this.exportChart();
                break;
        }
    }

    loadPlotly() {
        if (typeof Plotly === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
            script.onload = () => this.initChart();
            document.head.appendChild(script);
        } else {
            this.initChart();
        }
    }

    initChart() {
        this.layout = {
            ...this.getQuantumLayout(),
            ...this.options.layout
        };
        
        this.config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
            ...this.options.config
        };
    }

    getQuantumLayout() {
        return {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                family: 'Inter, system-ui, sans-serif',
                size: 12,
                color: '#2c3e50'
            },
            xaxis: {
                showgrid: true,
                gridcolor: 'rgba(52, 152, 219, 0.1)',
                gridwidth: 1,
                zeroline: false,
                showline: true,
                linecolor: '#bdc3c7',
                linewidth: 1,
                tickcolor: '#bdc3c7',
                tickwidth: 1,
                ticklen: 5,
                ticks: 'outside'
            },
            yaxis: {
                showgrid: true,
                gridcolor: 'rgba(52, 152, 219, 0.1)',
                gridwidth: 1,
                zeroline: false,
                showline: true,
                linecolor: '#bdc3c7',
                linewidth: 1,
                tickcolor: '#bdc3c7',
                tickwidth: 1,
                ticklen: 5,
                ticks: 'outside'
            },
            hovermode: 'closest',
            showlegend: true,
            legend: {
                x: 0,
                y: 1,
                bgcolor: 'rgba(255,255,255,0.8)',
                bordercolor: '#bdc3c7',
                borderwidth: 1
            },
            margin: {
                l: 50,
                r: 20,
                t: 20,
                b: 50
            }
        };
    }

    async renderCandlestickChart(data) {
        const trace = {
            x: data.dates,
            open: data.open,
            high: data.high,
            low: data.low,
            close: data.close,
            type: 'candlestick',
            name: data.symbol || 'Stock',
            increasing: {
                line: { color: '#27ae60', width: 2 },
                fillcolor: 'rgba(39, 174, 96, 0.3)'
            },
            decreasing: {
                line: { color: '#e74c3c', width: 2 },
                fillcolor: 'rgba(231, 76, 60, 0.3)'
            }
        };

        const layout = {
            ...this.layout,
            title: `${data.symbol || 'Stock'} Price Chart`,
            xaxis: { ...this.layout.xaxis, title: 'Date' },
            yaxis: { ...this.layout.yaxis, title: 'Price ($)' }
        };

        await Plotly.newPlot(
            `${this.container.id}-canvas`,
            [trace],
            layout,
            this.config
        );

        this.updateDataInfo(data.dates.length);
    }

    async renderSentimentHeatmap(data) {
        const trace = {
            z: data.sentiment_matrix,
            x: data.dates,
            y: data.sources,
            type: 'heatmap',
            colorscale: [
                [0, '#e74c3c'],
                [0.5, '#f39c12'],
                [1, '#27ae60']
            ],
            showscale: true,
            colorbar: {
                title: 'Sentiment Score',
                titleside: 'right',
                tickmode: 'array',
                tickvals: [-1, 0, 1],
                ticktext: ['Negative', 'Neutral', 'Positive']
            }
        };

        const layout = {
            ...this.layout,
            title: 'Multi-Source Sentiment Analysis',
            xaxis: { ...this.layout.xaxis, title: 'Date' },
            yaxis: { ...this.layout.yaxis, title: 'Source' }
        };

        await Plotly.newPlot(
            `${this.container.id}-canvas`,
            [trace],
            layout,
            this.config
        );

        this.updateDataInfo(data.dates.length * data.sources.length);
    }

    async renderPredictionChart(data) {
        const traces = [
            {
                x: data.historical_dates,
                y: data.historical_prices,
                type: 'scatter',
                mode: 'lines',
                name: 'Historical',
                line: { color: '#3498db', width: 2 }
            },
            {
                x: data.prediction_dates,
                y: data.predictions,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'AI Prediction',
                line: { color: '#e74c3c', width: 2, dash: 'dash' },
                marker: { size: 6 }
            }
        ];

        // Add confidence bands
        if (data.confidence_upper && data.confidence_lower) {
            traces.push({
                x: [...data.prediction_dates, ...data.prediction_dates.reverse()],
                y: [...data.confidence_upper, ...data.confidence_lower.reverse()],
                fill: 'toself',
                fillcolor: 'rgba(231, 76, 60, 0.1)',
                line: { color: 'rgba(255,255,255,0)' },
                showlegend: false,
                name: 'Confidence Band'
            });
        }

        const layout = {
            ...this.layout,
            title: 'AI Stock Price Prediction',
            xaxis: { ...this.layout.xaxis, title: 'Date' },
            yaxis: { ...this.layout.yaxis, title: 'Price ($)' }
        };

        await Plotly.newPlot(
            `${this.container.id}-canvas`,
            traces,
            layout,
            this.config
        );

        this.updateDataInfo(data.historical_dates.length + data.prediction_dates.length);
    }

    async renderPortfolioAllocation(data) {
        const trace = {
            labels: data.symbols,
            values: data.allocations,
            type: 'pie',
            textinfo: 'label+percent',
            textposition: 'outside',
            hoverinfo: 'label+value+percent',
            marker: {
                colors: this.generateColors(data.symbols.length),
                line: {
                    color: '#ffffff',
                    width: 2
                }
            }
        };

        const layout = {
            ...this.layout,
            title: 'Portfolio Allocation',
            showlegend: true,
            legend: {
                orientation: 'v',
                x: 1.05,
                y: 0.5
            }
        };

        await Plotly.newPlot(
            `${this.container.id}-canvas`,
            [trace],
            layout,
            this.config
        );

        this.updateDataInfo(data.symbols.length);
    }

    async renderRiskMetrics(data) {
        const trace = {
            r: data.risk_scores,
            theta: data.risk_categories,
            fill: 'toself',
            type: 'scatterpolar',
            mode: 'lines+markers',
            name: 'Risk Profile',
            line: { color: '#e74c3c', width: 2 },
            marker: { size: 8, color: '#e74c3c' }
        };

        const layout = {
            ...this.layout,
            title: 'Portfolio Risk Analysis',
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 100]
                }
            },
            showlegend: false
        };

        await Plotly.newPlot(
            `${this.container.id}-canvas`,
            [trace],
            layout,
            this.config
        );

        this.updateDataInfo(data.risk_categories.length);
    }

    generateColors(count) {
        const colors = [
            '#3498db', '#e74c3c', '#2ecc71', '#f39c12',
            '#9b59b6', '#1abc9c', '#34495e', '#e67e22',
            '#95a5a6', '#16a085', '#27ae60', '#2980b9'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }

    updateDataInfo(count) {
        const dataCountElement = document.getElementById('data-count');
        const lastUpdateElement = document.getElementById('last-update');
        
        if (dataCountElement) {
            dataCountElement.textContent = count.toLocaleString();
        }
        
        if (lastUpdateElement) {
            lastUpdateElement.textContent = new Date().toLocaleString();
        }
    }

    toggleFullscreen() {
        if (this.container.requestFullscreen) {
            this.container.requestFullscreen();
        }
    }

    resetZoom() {
        if (this.chart) {
            Plotly.relayout(`${this.container.id}-canvas`, {
                'xaxis.autorange': true,
                'yaxis.autorange': true
            });
        }
    }

    exportChart() {
        if (this.chart) {
            Plotly.downloadImage(`${this.container.id}-canvas`, {
                format: 'png',
                width: 1200,
                height: 800,
                filename: `quantum-chart-${Date.now()}`
            });
        }
    }

    startRealtime(updateInterval = 5000) {
        if (this.realtimeInterval) {
            clearInterval(this.realtimeInterval);
        }
        
        this.realtimeInterval = setInterval(() => {
            this.updateRealtime();
        }, updateInterval);
    }

    stopRealtime() {
        if (this.realtimeInterval) {
            clearInterval(this.realtimeInterval);
            this.realtimeInterval = null;
        }
    }

    async updateRealtime() {
        // Placeholder for real-time data updates
        // In a real implementation, this would fetch new data
        console.log('Real-time update triggered');
    }

    destroy() {
        this.stopRealtime();
        if (this.chart) {
            Plotly.purge(`${this.container.id}-canvas`);
        }
    }
}

// Enhanced Market Heatmap Component
class QuantumMarketHeatmap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            cellSize: 80,
            margin: { top: 20, right: 20, bottom: 20, left: 20 },
            colorRange: ['#e74c3c', '#f39c12', '#27ae60'],
            ...options
        };
        this.init();
    }

    init() {
        this.setupSVG();
        this.setupTooltip();
    }

    setupSVG() {
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('class', 'quantum-heatmap');
        
        this.tooltip = d3.select(this.container)
            .append('div')
            .attr('class', 'heatmap-tooltip')
            .style('opacity', 0);
    }

    setupTooltip() {
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'quantum-tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background', 'rgba(0,0,0,0.8)')
            .style('color', 'white')
            .style('padding', '10px')
            .style('border-radius', '5px')
            .style('font-size', '12px')
            .style('z-index', '1000');
    }

    renderSectorHeatmap(data) {
        const sectors = data.sectors;
        const cols = Math.ceil(Math.sqrt(sectors.length));
        const rows = Math.ceil(sectors.length / cols);
        
        const width = cols * this.options.cellSize + this.options.margin.left + this.options.margin.right;
        const height = rows * this.options.cellSize + this.options.margin.top + this.options.margin.bottom;
        
        this.svg
            .attr('width', width)
            .attr('height', height);
        
        const colorScale = d3.scaleLinear()
            .domain([-5, 0, 5])
            .range(this.options.colorRange);
        
        const cells = this.svg.selectAll('.sector-cell')
            .data(sectors)
            .enter()
            .append('g')
            .attr('class', 'sector-cell')
            .attr('transform', (d, i) => {
                const col = i % cols;
                const row = Math.floor(i / cols);
                return `translate(${col * this.options.cellSize + this.options.margin.left}, ${row * this.options.cellSize + this.options.margin.top})`;
            });
        
        cells.append('rect')
            .attr('width', this.options.cellSize - 2)
            .attr('height', this.options.cellSize - 2)
            .attr('fill', d => colorScale(d.change))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1)
            .on('mouseover', (event, d) => {
                this.tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                this.tooltip.html(`
                    <strong>${d.name}</strong><br/>
                    Change: ${d.change.toFixed(2)}%<br/>
                    Volume: ${d.volume.toLocaleString()}
                `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                this.tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });
        
        cells.append('text')
            .attr('x', this.options.cellSize / 2)
            .attr('y', this.options.cellSize / 2 - 5)
            .attr('text-anchor', 'middle')
            .attr('font-size', '10px')
            .attr('fill', 'white')
            .text(d => d.symbol);
        
        cells.append('text')
            .attr('x', this.options.cellSize / 2)
            .attr('y', this.options.cellSize / 2 + 10)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('font-weight', 'bold')
            .attr('fill', 'white')
            .text(d => `${d.change > 0 ? '+' : ''}${d.change.toFixed(1)}%`);
    }
}

// Export classes for use in other modules
window.QuantumInteractiveChart = QuantumInteractiveChart;
window.QuantumMarketHeatmap = QuantumMarketHeatmap;