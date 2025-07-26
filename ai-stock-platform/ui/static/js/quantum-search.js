/**
 * QuantumVestAI Advanced Search System
 * Intelligent search with real-time filtering and suggestions
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumSearch {
    constructor(options = {}) {
        this.options = {
            selector: '.quantum-search',
            apiEndpoint: '/api/stocks/search',
            debounceDelay: 300,
            minQueryLength: 2,
            maxResults: 20,
            enableFilters: true,
            enableSuggestions: true,
            enableHistory: true,
            categories: ['stocks', 'news', 'companies', 'analysts'],
            ...options
        };

        this.searchHistory = JSON.parse(localStorage.getItem('quantum-search-history') || '[]');
        this.searchCache = new Map();
        this.currentQuery = '';
        this.activeFilters = {};
        this.searchTimeout = null;
        
        this.init();
    }

    init() {
        this.createSearchInterface();
        this.setupEventListeners();
        this.loadSearchHistory();
    }

    createSearchInterface() {
        const container = document.querySelector(this.options.selector) || this.createSearchContainer();
        
        container.innerHTML = `
            <div class="quantum-search-container quantum-search-collapsed">
                <button class="quantum-search-toggle" aria-label="Open search">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                        <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                    </svg>
                </button>
                <div class="quantum-search-input-container">
                    <div class="quantum-search-input-wrapper">
                        <svg class="quantum-search-icon" viewBox="0 0 24 24" width="20" height="20">
                            <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                        </svg>
                        <input 
                            type="text" 
                            class="quantum-search-input" 
                            placeholder="Search stocks, companies, or news"
                            aria-label="Search QuantumVestAI"
                            autocomplete="off"
                        />
                        <button class="quantum-search-clear" aria-label="Clear search" style="display: none;">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                        <button class="quantum-search-filters-toggle" aria-label="Toggle filters">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path fill="currentColor" d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="quantum-search-voice-button" style="display: none;">
                        <button class="quantum-voice-search" aria-label="Voice search" title="Voice search">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path fill="currentColor" d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                            </svg>
                        </button>
                    </div>
                </div>

                ${this.options.enableFilters ? this.createFiltersHTML() : ''}

                <div class="quantum-search-results" style="display: none;">
                    <div class="quantum-search-suggestions"></div>
                    <div class="quantum-search-results-list"></div>
                </div>

                <div class="quantum-search-history" style="display: none;">
                    <div class="quantum-search-history-header">
                        <span>Recent Searches</span>
                        <button class="quantum-clear-history">Clear</button>
                    </div>
                    <div class="quantum-search-history-list"></div>
                </div>
            </div>
        `;

        this.addSearchStyles();
        this.setupVoiceSearch();
    }

    createSearchContainer() {
        const container = document.createElement('div');
        container.className = 'quantum-search';
        
        // Try to add to navigation first
        const nav = document.querySelector('.quantum-nav-container, .navbar');
        if (nav) {
            nav.appendChild(container);
        } else {
            // Fallback: add to header or body
            const header = document.querySelector('header');
            if (header) {
                header.appendChild(container);
            } else {
                document.body.appendChild(container);
            }
        }
        
        return container;
    }

    createFiltersHTML() {
        return `
            <div class="quantum-search-filters" style="display: none;">
                <div class="quantum-search-filters-content">
                    <div class="quantum-filter-group">
                        <label>Categories</label>
                        <div class="quantum-filter-options">
                            ${this.options.categories.map(category => `
                                <label class="quantum-filter-option">
                                    <input type="checkbox" value="${category}" data-filter="category">
                                    <span class="quantum-filter-label">${this.capitalizeFirst(category)}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="quantum-filter-group">
                        <label>Price Range</label>
                        <div class="quantum-price-range">
                            <input type="number" placeholder="Min" class="quantum-price-min" data-filter="price-min">
                            <span>to</span>
                            <input type="number" placeholder="Max" class="quantum-price-max" data-filter="price-max">
                        </div>
                    </div>
                    
                    <div class="quantum-filter-group">
                        <label>Market Cap</label>
                        <select class="quantum-market-cap-filter" data-filter="market-cap">
                            <option value="">All</option>
                            <option value="large">Large Cap (&gt;$10B)</option>
                            <option value="mid">Mid Cap ($2B-$10B)</option>
                            <option value="small">Small Cap (&lt;$2B)</option>
                        </select>
                    </div>
                    
                    <div class="quantum-filter-group">
                        <label>Time Period</label>
                        <select class="quantum-time-filter" data-filter="time">
                            <option value="">All Time</option>
                            <option value="1d">Last 24 Hours</option>
                            <option value="1w">Last Week</option>
                            <option value="1m">Last Month</option>
                            <option value="3m">Last 3 Months</option>
                            <option value="1y">Last Year</option>
                        </select>
                    </div>
                    
                    <div class="quantum-filter-actions">
                        <button class="quantum-btn quantum-btn-secondary quantum-clear-filters">Clear All</button>
                        <button class="quantum-btn quantum-btn-primary quantum-apply-filters">Apply Filters</button>
                    </div>
                </div>
            </div>
        `;
    }

    addSearchStyles() {
        const style = document.createElement('style');
        style.id = 'quantum-search-styles';
        style.textContent = `
            .quantum-search-container {
                position: relative;
                max-width: 600px;
                width: 100%;
            }

            .quantum-search-toggle {
                display: none;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                border: 1px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.15);
                color: #fff;
                cursor: pointer;
                transition: background 0.2s;
            }

            .quantum-search-toggle:hover {
                background: rgba(255, 255, 255, 0.25);
            }

            .quantum-search-collapsed .quantum-search-input-container {
                display: none;
            }

            .quantum-search-collapsed .quantum-search-toggle {
                display: flex;
            }

            .quantum-search-input-container {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .quantum-search-input-wrapper {
                position: relative;
                flex: 1;
                display: flex;
                align-items: center;
                background: rgba(240, 240, 240, 0.9);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 6px 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                transition: var(--transition-smooth, all 0.3s ease);
            }

            .quantum-search-input-wrapper:focus-within {
                border-color: var(--quantum-accent, #4facfe);
                box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.2);
                background: rgba(255, 255, 255, 0.95);
                transform: scale(1.02);
            }

            .quantum-search-icon {
                color: #666;
                margin-right: 12px;
                flex-shrink: 0;
                width: 20px;
                height: 20px;
                display: inline-block;
            }

            .quantum-search-input {
                flex: 1;
                border: none;
                background: transparent;
                color: #333;
                font-size: 16px;
                outline: none;
            }

            .quantum-search-input::placeholder {
                color: rgba(0, 0, 0, 0.5);
            }

            .quantum-search-clear,
            .quantum-search-filters-toggle {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: var(--transition-smooth, all 0.2s ease);
                margin-left: 8px;
            }

            .quantum-search-clear:hover,
            .quantum-search-filters-toggle:hover {
                color: white;
                background: rgba(255, 255, 255, 0.1);
            }

            .quantum-search-filters {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--glass-bg, rgba(0, 0, 0, 0.9));
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 16px;
                padding: 20px;
                backdrop-filter: blur(15px);
                z-index: 1000;
                margin-top: 8px;
                box-shadow: var(--quantum-shadow-medium, 0 12px 40px rgba(0, 0, 0, 0.3));
            }

            .quantum-filter-group {
                margin-bottom: 20px;
            }

            .quantum-filter-group label {
                display: block;
                color: white;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }

            .quantum-filter-options {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }

            .quantum-filter-option {
                display: flex;
                align-items: center;
                gap: 6px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                cursor: pointer;
                padding: 6px 12px;
                border-radius: 20px;
                transition: var(--transition-smooth, all 0.2s ease);
            }

            .quantum-filter-option:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .quantum-filter-option input[type="checkbox"] {
                accent-color: var(--quantum-accent, #4facfe);
            }

            .quantum-price-range {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .quantum-price-range input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 8px;
                background: var(--glass-bg, rgba(255, 255, 255, 0.1));
                color: white;
                font-size: 14px;
            }

            .quantum-price-range span {
                color: rgba(255, 255, 255, 0.6);
                font-size: 14px;
            }

            .quantum-market-cap-filter,
            .quantum-time-filter {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 8px;
                background: var(--glass-bg, rgba(255, 255, 255, 0.1));
                color: white;
                font-size: 14px;
            }

            .quantum-filter-actions {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            }

            .quantum-search-results {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--glass-bg, rgba(0, 0, 0, 0.9));
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 16px;
                backdrop-filter: blur(15px);
                z-index: 1000;
                margin-top: 8px;
                max-height: 400px;
                overflow-y: auto;
                box-shadow: var(--quantum-shadow-medium, 0 12px 40px rgba(0, 0, 0, 0.3));
            }

            .quantum-search-suggestions {
                padding: 16px;
                border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            }

            .quantum-search-suggestion {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                color: rgba(255, 255, 255, 0.8);
            }

            .quantum-search-suggestion:hover {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }

            .quantum-search-results-list {
                padding: 16px;
            }

            .quantum-search-result {
                display: flex;
                align-items: center;
                gap: 16px;
                padding: 12px;
                border-radius: 12px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.05));
            }

            .quantum-search-result:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: translateX(4px);
            }

            .quantum-search-result:last-child {
                border-bottom: none;
            }

            .quantum-result-icon {
                width: 40px;
                height: 40px;
                border-radius: 8px;
                background: var(--quantum-accent, linear-gradient(135deg, #4facfe 0%, #00f2fe 100%));
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                flex-shrink: 0;
            }

            .quantum-result-content {
                flex: 1;
            }

            .quantum-result-title {
                color: white;
                font-weight: 600;
                margin-bottom: 4px;
            }

            .quantum-result-subtitle {
                color: rgba(255, 255, 255, 0.6);
                font-size: 14px;
            }

            .quantum-result-meta {
                text-align: right;
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
            }

            .quantum-search-history {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--glass-bg, rgba(0, 0, 0, 0.9));
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 16px;
                backdrop-filter: blur(15px);
                z-index: 1000;
                margin-top: 8px;
                box-shadow: var(--quantum-shadow-medium, 0 12px 40px rgba(0, 0, 0, 0.3));
            }

            .quantum-search-history-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px;
                border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
                color: white;
                font-weight: 600;
            }

            .quantum-clear-history {
                background: none;
                border: none;
                color: var(--quantum-accent, #4facfe);
                cursor: pointer;
                font-size: 14px;
            }

            .quantum-search-history-list {
                padding: 8px;
            }

            .quantum-history-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                color: rgba(255, 255, 255, 0.8);
            }

            .quantum-history-item:hover {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }

            .quantum-voice-search {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                cursor: pointer;
                padding: 8px;
                border-radius: 50%;
                transition: var(--transition-smooth, all 0.2s ease);
            }

            .quantum-voice-search:hover {
                color: white;
                background: rgba(255, 255, 255, 0.1);
            }

            .quantum-voice-search.listening {
                color: #ff4444;
                animation: pulse 1s infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            @media (max-width: 768px) {
                .quantum-search-container {
                    max-width: 100%;
                }

                .quantum-search-filters {
                    left: -20px;
                    right: -20px;
                }

                .quantum-filter-options {
                    flex-direction: column;
                }

                .quantum-price-range {
                    flex-direction: column;
                    align-items: stretch;
                }

                .quantum-filter-actions {
                    flex-direction: column;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setupEventListeners() {
        const container = document.querySelector('.quantum-search-container');
        const input = container.querySelector('.quantum-search-input');
        const clearBtn = container.querySelector('.quantum-search-clear');
        const filtersToggle = container.querySelector('.quantum-search-filters-toggle');
        const filters = container.querySelector('.quantum-search-filters');
        const toggleBtn = container.querySelector('.quantum-search-toggle');
        const results = container.querySelector('.quantum-search-results');
        const history = container.querySelector('.quantum-search-history');

        // Input events
        input.addEventListener('input', (e) => this.handleInput(e));
        input.addEventListener('focus', () => this.handleFocus());
        input.addEventListener('blur', (e) => this.handleBlur(e));
        input.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Clear button
        clearBtn.addEventListener('click', () => this.clearSearch());

        // Toggle collapse
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                container.classList.toggle('quantum-search-collapsed');
                if (!container.classList.contains('quantum-search-collapsed')) {
                    input.focus();
                }
            });
        }

        // Filters toggle
        if (filtersToggle && filters) {
            filtersToggle.addEventListener('click', () => this.toggleFilters());
        }

        // Filter events
        if (filters) {
            this.setupFilterEvents(filters);
        }

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                this.hideResults();
                this.hideHistory();
                if (filters) filters.style.display = 'none';
            }
        });

        // History events
        if (history) {
            const clearHistory = history.querySelector('.quantum-clear-history');
            if (clearHistory) {
                clearHistory.addEventListener('click', () => this.clearHistory());
            }
        }
    }

    setupFilterEvents(filters) {
        const applyBtn = filters.querySelector('.quantum-apply-filters');
        const clearBtn = filters.querySelector('.quantum-clear-filters');
        const filterInputs = filters.querySelectorAll('[data-filter]');

        if (applyBtn) {
            applyBtn.addEventListener('click', () => this.applyFilters());
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFilters());
        }

        filterInputs.forEach(input => {
            input.addEventListener('change', () => this.updateFilters());
        });
    }

    setupVoiceSearch() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            return; // Voice search not supported
        }

        const voiceContainer = document.querySelector('.quantum-search-voice-button');
        const voiceBtn = document.querySelector('.quantum-voice-search');
        
        if (voiceContainer) {
            voiceContainer.style.display = 'block';
        }

        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.startVoiceSearch());
        }
    }

    handleInput(e) {
        const query = e.target.value;
        this.currentQuery = query;

        // Show/hide clear button
        const clearBtn = document.querySelector('.quantum-search-clear');
        if (clearBtn) {
            clearBtn.style.display = query ? 'block' : 'none';
        }

        // Debounced search
        clearTimeout(this.searchTimeout);
        
        if (query.length >= this.options.minQueryLength) {
            this.searchTimeout = setTimeout(() => {
                this.performSearch(query);
            }, this.options.debounceDelay);
        } else if (query.length === 0) {
            this.hideResults();
            this.showHistory();
        } else {
            this.hideResults();
            this.hideHistory();
        }
    }

    handleFocus() {
        const container = document.querySelector('.quantum-search-container');
        container.classList.remove('quantum-search-collapsed');
        if (this.currentQuery.length === 0) {
            this.showHistory();
        } else if (this.currentQuery.length >= this.options.minQueryLength) {
            this.showResults();
        }
    }

    handleBlur(e) {
        // Delay hiding to allow clicks on results
        setTimeout(() => {
            if (!document.querySelector('.quantum-search-container:focus-within')) {
                this.hideResults();
                this.hideHistory();
                const container = document.querySelector('.quantum-search-container');
                container.classList.add('quantum-search-collapsed');
            }
        }, 150);
    }

    handleKeydown(e) {
        const results = document.querySelector('.quantum-search-results');
        const items = results ? results.querySelectorAll('.quantum-search-result, .quantum-search-suggestion') : [];
        
        if (items.length === 0) return;

        let currentIndex = -1;
        items.forEach((item, index) => {
            if (item.classList.contains('selected')) {
                currentIndex = index;
            }
        });

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                this.selectResult(items, nextIndex);
                break;

            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                this.selectResult(items, prevIndex);
                break;

            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0) {
                    items[currentIndex].click();
                }
                break;

            case 'Escape':
                this.hideResults();
                this.hideHistory();
                break;
        }
    }

    selectResult(items, index) {
        items.forEach(item => item.classList.remove('selected'));
        if (items[index]) {
            items[index].classList.add('selected');
            items[index].scrollIntoView({ block: 'nearest' });
        }
    }

    async performSearch(query) {
        if (!query || query.trim().length === 0) {
            this.hideResults();
            return;
        }

        const trimmedQuery = query.trim();
        
        if (this.searchCache.has(trimmedQuery)) {
            this.displayResults(this.searchCache.get(trimmedQuery));
            return;
        }

        try {
            this.showLoadingState();

            // Fetch suggestions from backend with graceful fallback
            const results = await this.fetchResults(trimmedQuery);
            
            if (results && (results.suggestions || results.results)) {
                this.searchCache.set(trimmedQuery, results);
                this.displayResults(results);
                this.addToHistory(trimmedQuery);
            } else {
                this.showNoResultsState(trimmedQuery);
            }

        } catch (error) {
            console.error('Search error:', error);
            this.showErrorState();
        }
    }

    showNoResultsState(query) {
        const resultsList = document.querySelector('.quantum-search-results-list');
        if (resultsList) {
            resultsList.innerHTML = `
                <div class="quantum-search-no-results">
                    <div style="padding: 20px; text-align: center; color: rgba(255, 255, 255, 0.6);">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔍</div>
                        <div style="font-weight: 500; margin-bottom: 0.25rem;">No results found</div>
                        <small>No results for "${query}". Try a different search term.</small>
                    </div>
                </div>
            `;
        }
        this.showResults();
    }

    async simulateSearch(query) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 200));

        // Mock search results
        const mockResults = {
            suggestions: [
                `${query} stock price`,
                `${query} market analysis`,
                `${query} company profile`,
                `${query} financial reports`
            ],
            results: [
                {
                    type: 'stock',
                    symbol: query.toUpperCase(),
                    name: `${query} Corporation`,
                    price: (Math.random() * 1000 + 10).toFixed(2),
                    change: (Math.random() * 20 - 10).toFixed(2),
                    changePercent: (Math.random() * 10 - 5).toFixed(2)
                },
                {
                    type: 'news',
                    title: `Latest ${query} News`,
                    description: `Recent developments and market analysis for ${query}`,
                    timestamp: new Date().toISOString(),
                    source: 'Market News'
                },
                {
                    type: 'company',
                    name: `${query} Inc.`,
                    description: `Leading company in the ${query} sector`,
                    marketCap: (Math.random() * 100000000000).toFixed(0),
                    employees: Math.floor(Math.random() * 50000 + 1000)
                }
            ]
        };

        return mockResults;
    }

    displayResults(data) {
        const results = document.querySelector('.quantum-search-results');
        const suggestions = results.querySelector('.quantum-search-suggestions');
        const resultsList = results.querySelector('.quantum-search-results-list');

        // Clear previous results
        suggestions.innerHTML = '';
        resultsList.innerHTML = '';

        // Display suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            data.suggestions.forEach(suggestion => {
                const item = document.createElement('div');
                item.className = 'quantum-search-suggestion';
                item.innerHTML = `
                    <svg viewBox="0 0 24 24" width="16" height="16">
                        <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                    </svg>
                    <span>${suggestion}</span>
                `;
                item.addEventListener('click', () => this.selectSuggestion(suggestion));
                suggestions.appendChild(item);
            });
        }

        // Display results
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                const item = this.createResultItem(result);
                resultsList.appendChild(item);
            });
        }

        this.showResults();
    }

    createResultItem(result) {
        const item = document.createElement('div');
        item.className = 'quantum-search-result';

        let icon, title, subtitle, meta;

        switch (result.type) {
            case 'stock':
                icon = result.symbol.charAt(0);
                title = `${result.symbol} - ${result.name}`;
                subtitle = `Stock Price`;
                meta = `$${result.price} (${result.change >= 0 ? '+' : ''}${result.changePercent}%)`;
                break;

            case 'news':
                icon = '📰';
                title = result.title;
                subtitle = result.description;
                meta = this.formatTimeAgo(result.timestamp);
                break;

            case 'company':
                icon = result.name.charAt(0);
                title = result.name;
                subtitle = result.description;
                meta = `${this.formatNumber(result.employees)} employees`;
                break;

            default:
                icon = '🔍';
                title = result.title || 'Search Result';
                subtitle = result.description || '';
                meta = '';
        }

        item.innerHTML = `
            <div class="quantum-result-icon">${icon}</div>
            <div class="quantum-result-content">
                <div class="quantum-result-title">${title}</div>
                <div class="quantum-result-subtitle">${subtitle}</div>
            </div>
            <div class="quantum-result-meta">${meta}</div>
        `;

        item.addEventListener('click', () => this.selectResult(result));
        return item;
    }

    selectSuggestion(suggestion) {
        const input = document.querySelector('.quantum-search-input');
        input.value = suggestion;
        this.currentQuery = suggestion;
        this.performSearch(suggestion);
    }

    selectResult(result) {
        // Handle result selection based on type
        switch (result.type) {
            case 'stock':
                this.navigateToStock(result.symbol);
                break;
            case 'news':
                this.openNewsArticle(result);
                break;
            case 'company':
                this.navigateToCompany(result);
                break;
        }

        this.hideResults();
        this.addToHistory(this.currentQuery);
    }

    navigateToStock(symbol) {
        // Navigate to stock page
        window.location.href = `/stocks/${symbol}`;
    }

    openNewsArticle(article) {
        // Open news article
        window.open(article.url || '#', '_blank');
    }

    navigateToCompany(company) {
        // Navigate to company page
        window.location.href = `/companies/${company.name.toLowerCase().replace(/\s+/g, '-')}`;
    }

    showResults() {
        const results = document.querySelector('.quantum-search-results');
        const history = document.querySelector('.quantum-search-history');
        
        if (results) {
            results.style.display = 'block';
        }
        if (history) {
            history.style.display = 'none';
        }
    }

    async fetchResults(query) {
        try {
            const resp = await fetch(`${this.options.apiEndpoint}?query=${encodeURIComponent(query)}&limit=${this.options.maxResults}`);
            if (!resp.ok) throw new Error('Request failed');
            const data = await resp.json();
            const results = data.results || data.data || [];
            const suggestions = Array.isArray(results) ? results.slice(0, 5).map(r => {
                if (r.symbol && r.name) return `${r.symbol} - ${r.name}`;
                return r.title || r.name || '';
            }) : [];
            return { suggestions, results: Array.isArray(results) ? results : [] };
        } catch (err) {
            console.error('Fetch error:', err);
            return this.simulateSearch(query);
        }
    }

    hideResults() {
        const results = document.querySelector('.quantum-search-results');
        if (results) {
            results.style.display = 'none';
        }
    }

    showHistory() {
        if (!this.options.enableHistory || this.searchHistory.length === 0) return;

        const history = document.querySelector('.quantum-search-history');
        const results = document.querySelector('.quantum-search-results');
        const historyList = history.querySelector('.quantum-search-history-list');

        if (results) {
            results.style.display = 'none';
        }

        historyList.innerHTML = '';
        this.searchHistory.slice(0, 10).forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'quantum-history-item';
            historyItem.innerHTML = `
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M13,3A9,9 0 0,0 4,12H1L4.89,15.89L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3Z"/>
                </svg>
                <span>${item.query}</span>
            `;
            historyItem.addEventListener('click', () => {
                const input = document.querySelector('.quantum-search-input');
                input.value = item.query;
                this.currentQuery = item.query;
                this.performSearch(item.query);
            });
            historyList.appendChild(historyItem);
        });

        if (history) {
            history.style.display = 'block';
        }
    }

    hideHistory() {
        const history = document.querySelector('.quantum-search-history');
        if (history) {
            history.style.display = 'none';
        }
    }

    addToHistory(query) {
        if (!this.options.enableHistory) return;

        // Remove existing entry if present
        this.searchHistory = this.searchHistory.filter(item => item.query !== query);
        
        // Add to beginning of array
        this.searchHistory.unshift({
            query,
            timestamp: new Date().toISOString()
        });

        // Limit history size
        this.searchHistory = this.searchHistory.slice(0, 50);
        
        // Save to localStorage
        localStorage.setItem('quantum-search-history', JSON.stringify(this.searchHistory));
    }

    clearHistory() {
        this.searchHistory = [];
        localStorage.removeItem('quantum-search-history');
        this.hideHistory();
    }

    loadSearchHistory() {
        try {
            const saved = localStorage.getItem('quantum-search-history');
            if (saved) {
                this.searchHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading search history:', error);
            this.searchHistory = [];
        }
    }

    clearSearch() {
        const input = document.querySelector('.quantum-search-input');
        const clearBtn = document.querySelector('.quantum-search-clear');
        
        input.value = '';
        this.currentQuery = '';
        
        if (clearBtn) {
            clearBtn.style.display = 'none';
        }
        
        this.hideResults();
        this.showHistory();
        input.focus();
    }

    toggleFilters() {
        const filters = document.querySelector('.quantum-search-filters');
        if (filters) {
            const isVisible = filters.style.display === 'block';
            filters.style.display = isVisible ? 'none' : 'block';
        }
    }

    updateFilters() {
        const filters = document.querySelector('.quantum-search-filters');
        const filterInputs = filters.querySelectorAll('[data-filter]');
        
        this.activeFilters = {};
        
        filterInputs.forEach(input => {
            const filterType = input.dataset.filter;
            
            if (input.type === 'checkbox' && input.checked) {
                if (!this.activeFilters[filterType]) {
                    this.activeFilters[filterType] = [];
                }
                this.activeFilters[filterType].push(input.value);
            } else if (input.type !== 'checkbox' && input.value) {
                this.activeFilters[filterType] = input.value;
            }
        });
    }

    applyFilters() {
        this.updateFilters();
        
        if (this.currentQuery) {
            this.performSearch(this.currentQuery);
        }
        
        this.toggleFilters();
    }

    clearFilters() {
        const filters = document.querySelector('.quantum-search-filters');
        const filterInputs = filters.querySelectorAll('[data-filter]');
        
        filterInputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        
        this.activeFilters = {};
        
        if (this.currentQuery) {
            this.performSearch(this.currentQuery);
        }
    }

    startVoiceSearch() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        const voiceBtn = document.querySelector('.quantum-voice-search');

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        voiceBtn.classList.add('listening');

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const input = document.querySelector('.quantum-search-input');
            
            input.value = transcript;
            this.currentQuery = transcript;
            this.performSearch(transcript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };

        recognition.onend = () => {
            voiceBtn.classList.remove('listening');
        };

        recognition.start();
    }

    showLoadingState() {
        const resultsList = document.querySelector('.quantum-search-results-list');
        if (resultsList) {
            resultsList.innerHTML = `
                <div class="quantum-search-loading">
                    <div style="display: flex; align-items: center; gap: 12px; padding: 20px; color: rgba(255, 255, 255, 0.6);">
                        <div class="quantum-loading-spinner"></div>
                        <span>Searching...</span>
                    </div>
                </div>
            `;
        }
        this.showResults();
    }

    showErrorState() {
        const resultsList = document.querySelector('.quantum-search-results-list');
        if (resultsList) {
            resultsList.innerHTML = `
                <div class="quantum-search-error">
                    <div style="padding: 20px; text-align: center; color: rgba(255, 255, 255, 0.6);">
                        <span>Sorry, something went wrong. Please try again.</span>
                    </div>
                </div>
            `;
        }
        this.showResults();
    }

    // Utility methods
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        
        return time.toLocaleDateString();
    }
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const quantumSearch = new QuantumSearch();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumSearch;
}