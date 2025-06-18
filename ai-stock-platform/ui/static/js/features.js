/**
 * QuantumVestAI Features JavaScript
 * Last Updated: 2025-06-18 21:25:28
 * Author: daparthi001
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initFeatureCards();
    initSentimentAnalysis();
    initMultiFactorAnalysis();
    initPortfolioOptimization();
    initExtendedPredictions();
    initCustomIndicators();
});

// Initialize feature cards
function initFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');
    if (!featureCards.length) return;
    
    featureCards.forEach(card => {
        // Add animation effect on hover
        card.addEventListener('mouseenter', () => {
            card.classList.add('hover');
        });
        
        card.addEventListener('mouseleave', () => {
            card.classList.remove('hover');
        });
    });
}

// Initialize sentiment analysis feature
function initSentimentAnalysis() {
    const sentimentPage = document.querySelector('.sentiment-dashboard');
    if (!sentimentPage) return;
    
    // Initialize sentiment ticker search
    const tickerSearch = document.getElementById('ticker-search');
    if (tickerSearch) {
        tickerSearch.addEventListener('input', debounce(function() {
            searchTickers(this.value);
        }, 300));
    }
    
    // Initialize sentiment markers
    const sentimentMarkers = document.querySelectorAll('.sentiment-marker');
    if (sentimentMarkers.length) {
        sentimentMarkers.forEach(marker => {
            const value = parseFloat(marker.getAttribute('data-value'));
            // Position marker based on sentiment value (0-100)
            marker.style.left = `${value}%`;
        });
    }
    
    // Initialize sentiment period selector
    const periodSelectors = document.querySelectorAll('.period-selector .period-option');
    if (periodSelectors.length) {
        periodSelectors.forEach(option => {
            option.addEventListener('click', function() {
                // Remove active class from all options
                periodSelectors.forEach(opt => opt.classList.remove('active'));
                // Add active class to selected option
                this.classList.add('active');
                
                const period = this.getAttribute('data-period');
                const ticker = document.getElementById('ticker-search')?.value;
                
                // Update URL with new period
                const url = new URL(window.location);
                url.searchParams.set('period', period);
                if (ticker) {
                    url.searchParams.set('ticker', ticker);
                }
                window.location.href = url.toString();
            });
        });
    }
}

// Initialize multi-factor analysis feature
function initMultiFactorAnalysis() {
    const multiFactorPage = document.querySelector('.multi-factor-analysis');
    if (!multiFactorPage) return;
    
    // Initialize factor weight sliders
    const weightSliders = document.querySelectorAll('.factor-weight-slider');
    if (weightSliders.length) {
        weightSliders.forEach(slider => {
            slider.addEventListener('input', function() {
                // Update displayed value
                const valueDisplay = this.parentElement.querySelector('.weight-value');
                if (valueDisplay) {
                    valueDisplay.textContent = this.value;
                }
                
                // Update total weight calculation
                updateTotalWeight();
            });
        });
    }
    
    // Initialize factor model selection
    const modelSelect = document.getElementById('factor-model-select');
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            if (this.value) {
                loadFactorModel(this.value);
            }
        });
    }
    
    // Initialize apply model button
    const applyModelBtn = document.getElementById('apply-model-btn');
    if (applyModelBtn) {
        applyModelBtn.addEventListener('click', function() {
            const ticker = document.getElementById('ticker-search')?.value;
            if (!ticker) {
                showAlert('Please enter a ticker symbol first', 'warning');
                return;
            }
            
            applyFactorModel(ticker);
        });
    }
    
    // Initialize factor charts
    initFactorCharts();
}

// Initialize portfolio optimization feature
function initPortfolioOptimization() {
    const portfolioPage = document.querySelector('.portfolio-optimization');
    if (!portfolioPage) return;
    
    // Initialize portfolio selector
    const portfolioSelect = document.getElementById('portfolio-select');
    if (portfolioSelect) {
        portfolioSelect.addEventListener('change', function() {
            if (this.value) {
                loadPortfolio(this.value);
            }
        });
    }
    
    // Initialize optimization model selector
    const optimizationModelSelect = document.getElementById('optimization-model');
    if (optimizationModelSelect) {
        optimizationModelSelect.addEventListener('change', function() {
            const modelId = this.value;
            updateOptimizationParams(modelId);
        });
    }
    
    // Initialize run optimization button
    const runOptimizationBtn = document.getElementById('run-optimization');
    if (runOptimizationBtn) {
        runOptimizationBtn.addEventListener('click', function() {
            const portfolioId = document.getElementById('portfolio-select')?.value;
            const modelId = document.getElementById('optimization-model')?.value;
            
            if (!portfolioId || !modelId) {
                showAlert('Please select a portfolio and optimization model', 'warning');
                return;
            }
            
            runPortfolioOptimization(portfolioId, modelId);
        });
    }
    
    // Initialize optimization chart
    initOptimizationChart();
}

// Initialize extended predictions feature
function initExtendedPredictions() {
    const predictionsPage = document.querySelector('.extended-predictions');
    if (!predictionsPage) return;
    
    // Initialize prediction interval selector
    const intervalSelector = document.querySelectorAll('.interval-selector .interval-option');
    if (intervalSelector.length) {
        intervalSelector.forEach(option => {
            option.addEventListener('click', function() {
                // Remove active class from all options
                intervalSelector.forEach(opt => opt.classList.remove('active'));
                // Add active class to selected option
                this.classList.add('active');
                
                const interval = this.getAttribute('data-interval');
                const ticker = document.getElementById('ticker-search')?.value;
                
                // Update URL with new interval
                const url = new URL(window.location);
                url.searchParams.set('interval', interval);
                if (ticker) {
                    url.searchParams.set('ticker', ticker);
                }
                window.location.href = url.toString();
            });
        });
    }
    
    // Initialize prediction chart
    initPredictionChart();
}

// Initialize custom indicators feature
function initCustomIndicators() {
    const indicatorsPage = document.querySelector('.custom-indicators');
    if (!indicatorsPage) return;
    
    // Initialize component list
    const componentItems = document.querySelectorAll('.component-item');
    if (componentItems.length) {
        componentItems.forEach(item => {
            item.addEventListener('click', function() {
                const code = this.getAttribute('data-code');
                const formulaEditor = document.getElementById('formula-editor');
                
                if (formulaEditor && code) {
                    // Insert component code at cursor position
                    insertAtCursor(formulaEditor, code);
                }
            });
        });
    }
    
    // Initialize test indicator button
    const testIndicatorBtn = document.getElementById('test-indicator');
    if (testIndicatorBtn) {
        testIndicatorBtn.addEventListener('click', function() {
            const formula = document.getElementById('formula-editor')?.value;
            const ticker = document.getElementById('test-ticker')?.value;
            
            if (!formula) {
                showAlert('Please enter an indicator formula', 'warning');
                return;
            }
            
            if (!ticker) {
                showAlert('Please enter a ticker for testing', 'warning');
                return;
            }
            
            testCustomIndicator(formula, ticker);
        });
    }
    
    // Initialize save indicator button
    const saveIndicatorBtn = document.getElementById('save-indicator');
    if (saveIndicatorBtn) {
        saveIndicatorBtn.addEventListener('click', function() {
            const formula = document.getElementById('formula-editor')?.value;
            const name = document.getElementById('indicator-name')?.value;
            
            if (!formula) {
                showAlert('Please enter an indicator formula', 'warning');
                return;
            }
            
            if (!name) {
                showAlert('Please enter a name for your indicator', 'warning');
                return;
            }
            
            saveCustomIndicator(name, formula);
        });
    }
    
    // Initialize indicator result chart
    initIndicatorChart();
}

// Helper function for debouncing
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}

// Helper function to search tickers
function searchTickers(query) {
    if (!query || query.length < 2) return;
    
    fetch(`/api/v1/ticker-search?q=${query}`)
        .then(response => response.json())
        .then(data => {
            updateTickerResults(data.results);
        })
        .catch(error => {
            console.error('Error searching tickers:', error);
        });
}

// Helper function to update ticker search results
function updateTickerResults(results