/**
 * QuantumVestAI Dynamic Content System
 * Blog, news, and content management with AI-powered insights
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumContent {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: '/api/content',
            autoRefreshInterval: 300000, // 5 minutes
            enableRealtime: true,
            maxArticlesPerPage: 20,
            enableSentimentAnalysis: true,
            enableRelatedContent: true,
            enableBookmarks: true,
            enableComments: true,
            ...options
        };

        this.articles = new Map();
        this.categories = new Map();
        this.bookmarks = new Set();
        this.readArticles = new Set();
        this.filters = {
            category: 'all',
            sentiment: 'all',
            timeframe: 'all',
            source: 'all'
        };

        this.init();
    }

    init() {
        this.loadUserPreferences();
        this.setupEventListeners();
        this.createContentInterface();
        this.loadInitialContent();
        this.setupAutoRefresh();
    }

    loadUserPreferences() {
        // Load user preferences from localStorage
        const saved = localStorage.getItem('quantum-content-preferences');
        if (saved) {
            try {
                const prefs = JSON.parse(saved);
                this.filters = { ...this.filters, ...prefs.filters };
                this.bookmarks = new Set(prefs.bookmarks || []);
                this.readArticles = new Set(prefs.readArticles || []);
            } catch (error) {
                console.error('Failed to load content preferences:', error);
            }
        }
    }

    saveUserPreferences() {
        const prefs = {
            filters: this.filters,
            bookmarks: Array.from(this.bookmarks),
            readArticles: Array.from(this.readArticles)
        };
        localStorage.setItem('quantum-content-preferences', JSON.stringify(prefs));
    }

    setupEventListeners() {
        // Listen for AI insights that might affect content relevance
        window.addEventListener('aiInsightsUpdate', (e) => {
            this.updateContentRelevance(e.detail.insights);
        });

        // Listen for portfolio changes to suggest relevant content
        window.addEventListener('portfolioUpdate', (e) => {
            this.updatePortfolioRelevantContent(e.detail);
        });

        // Listen for market data updates
        window.addEventListener('marketDataUpdate', (e) => {
            this.updateMarketRelatedContent(e.detail);
        });
    }

    createContentInterface() {
        const existingInterface = document.querySelector('.quantum-content-hub');
        if (existingInterface) return;

        // Find a suitable container
        const container = this.findContentContainer();
        if (!container) return;

        const contentHub = document.createElement('div');
        contentHub.className = 'quantum-content-hub';
        contentHub.innerHTML = this.getContentHubHTML();

        container.appendChild(contentHub);
        this.addContentStyles();
        this.setupContentEventListeners();
    }

    findContentContainer() {
        // Try to find existing content areas
        const candidates = [
            document.querySelector('#news-section'),
            document.querySelector('.news-container'),
            document.querySelector('#content'),
            document.querySelector('main'),
            document.querySelector('.main-content')
        ];

        return candidates.find(el => el !== null) || document.body;
    }

    getContentHubHTML() {
        return `
            <div class="content-header">
                <div class="content-title-section">
                    <h2 class="content-title" data-i18n="content.news_insights">News & Insights</h2>
                    <div class="content-stats">
                        <span class="article-count">Loading...</span>
                        <span class="last-updated">Just now</span>
                    </div>
                </div>
                <div class="content-actions">
                    <button class="content-refresh-btn quantum-btn quantum-btn-secondary" data-i18n="common.refresh">
                        <i class="bi bi-arrow-clockwise"></i> Refresh
                    </button>
                    <button class="content-filter-btn quantum-btn quantum-btn-secondary" data-i18n="common.filter">
                        <i class="bi bi-funnel"></i> Filter
                    </button>
                    <button class="content-search-btn quantum-btn quantum-btn-secondary" data-i18n="common.search">
                        <i class="bi bi-search"></i> Search
                    </button>
                </div>
            </div>

            <div class="content-filters" style="display: none;">
                <div class="filter-group">
                    <label data-i18n="content.category">Category</label>
                    <select class="filter-category">
                        <option value="all" data-i18n="common.all">All</option>
                        <option value="market" data-i18n="content.market_news">Market News</option>
                        <option value="earnings" data-i18n="content.earnings">Earnings</option>
                        <option value="analysis" data-i18n="content.analysis">Analysis</option>
                        <option value="crypto" data-i18n="content.crypto">Crypto</option>
                        <option value="economy" data-i18n="content.economy">Economy</option>
                        <option value="technology" data-i18n="content.technology">Technology</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label data-i18n="content.sentiment">Sentiment</label>
                    <select class="filter-sentiment">
                        <option value="all" data-i18n="common.all">All</option>
                        <option value="positive" data-i18n="content.positive">Positive</option>
                        <option value="negative" data-i18n="content.negative">Negative</option>
                        <option value="neutral" data-i18n="content.neutral">Neutral</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label data-i18n="content.timeframe">Timeframe</label>
                    <select class="filter-timeframe">
                        <option value="all" data-i18n="common.all">All</option>
                        <option value="1h" data-i18n="time.last_hour">Last Hour</option>
                        <option value="24h" data-i18n="time.last_24h">Last 24 Hours</option>
                        <option value="7d" data-i18n="time.last_week">Last Week</option>
                        <option value="30d" data-i18n="time.last_month">Last Month</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label data-i18n="content.source">Source</label>
                    <select class="filter-source">
                        <option value="all" data-i18n="common.all">All Sources</option>
                        <option value="reuters">Reuters</option>
                        <option value="bloomberg">Bloomberg</option>
                        <option value="wsj">Wall Street Journal</option>
                        <option value="cnbc">CNBC</option>
                        <option value="quantum">QuantumVestAI</option>
                    </select>
                </div>
                
                <div class="filter-actions">
                    <button class="apply-filters-btn quantum-btn quantum-btn-primary" data-i18n="common.apply">Apply</button>
                    <button class="clear-filters-btn quantum-btn quantum-btn-secondary" data-i18n="common.clear">Clear</button>
                </div>
            </div>

            <div class="content-search" style="display: none;">
                <div class="search-input-group">
                    <input type="text" class="content-search-input" placeholder="Search articles..." data-i18n-placeholder="content.search_placeholder">
                    <button class="search-execute-btn quantum-btn quantum-btn-primary" data-i18n="common.search">Search</button>
                </div>
                <div class="search-suggestions"></div>
            </div>

            <div class="content-tabs">
                <button class="content-tab active" data-tab="news" data-i18n="content.news">News</button>
                <button class="content-tab" data-tab="analysis" data-i18n="content.analysis">Analysis</button>
                <button class="content-tab" data-tab="insights" data-i18n="content.ai_insights">AI Insights</button>
                <button class="content-tab" data-tab="bookmarks" data-i18n="content.bookmarks">Bookmarks</button>
            </div>

            <div class="content-main">
                <div class="content-sidebar">
                    <div class="trending-topics">
                        <h3 data-i18n="content.trending">Trending Topics</h3>
                        <div class="trending-list"></div>
                    </div>
                    
                    <div class="market-movers">
                        <h3 data-i18n="content.market_movers">Market Movers</h3>
                        <div class="movers-list"></div>
                    </div>
                    
                    <div class="ai-recommendations">
                        <h3 data-i18n="content.ai_recommended">AI Recommended</h3>
                        <div class="recommendations-list"></div>
                    </div>
                </div>

                <div class="content-feed">
                    <div class="content-tab-panel active" data-tab="news">
                        <div class="articles-container"></div>
                        <div class="load-more-container">
                            <button class="load-more-btn quantum-btn quantum-btn-secondary rounded-lg shadow hover:bg-opacity-80" data-i18n="common.load_more">
                                Load More Articles
                            </button>
                        </div>
                    </div>
                    
                    <div class="content-tab-panel" data-tab="analysis">
                        <div class="analysis-container"></div>
                    </div>
                    
                    <div class="content-tab-panel" data-tab="insights">
                        <div class="insights-container"></div>
                    </div>
                    
                    <div class="content-tab-panel" data-tab="bookmarks">
                        <div class="bookmarks-container"></div>
                    </div>
                </div>
            </div>

            <div class="content-loading" style="display: none;">
                <div class="loading-spinner"></div>
                <span data-i18n="common.loading">Loading content...</span>
            </div>
        `;
    }

    addContentStyles() {
        const style = document.createElement('style');
        style.id = 'quantum-content-styles';
        style.textContent = `
            .quantum-content-hub {
                background: var(--glass-bg, rgba(255, 255, 255, 0.05));
                border-radius: 16px;
                padding: 24px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            }

            .content-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                flex-wrap: wrap;
                gap: 16px;
            }

            .content-title-section {
                flex: 1;
            }

            .content-title {
                color: white;
                margin: 0 0 8px 0;
                font-size: 24px;
                font-weight: 600;
                background: var(--quantum-primary, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .content-stats {
                display: flex;
                gap: 16px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 14px;
            }

            .content-actions {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }

            .content-actions button {
                padding: 8px 16px;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .content-filters,
            .content-search {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-bottom: 16px;
            }

            .filter-group label {
                color: white;
                font-weight: 500;
                font-size: 14px;
            }

            .filter-group select,
            .content-search-input {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
            }

            .filter-group select:focus,
            .content-search-input:focus {
                outline: none;
                border-color: var(--quantum-accent, #4facfe);
                box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.2);
            }

            .filter-actions {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
                margin-top: 16px;
            }

            .search-input-group {
                display: flex;
                gap: 12px;
                align-items: center;
                margin-bottom: 16px;
            }

            .content-search-input {
                flex: 1;
            }

            .search-suggestions {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            .search-suggestion {
                background: var(--quantum-accent, #4facfe);
                color: white;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
            }

            .search-suggestion:hover {
                background: var(--quantum-primary, #667eea);
                transform: translateY(-1px);
            }

            .content-tabs {
                display: flex;
                gap: 2px;
                margin-bottom: 20px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 4px;
            }

            .content-tab {
                flex: 1;
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                padding: 12px 16px;
                border-radius: 8px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                font-weight: 500;
            }

            .content-tab:hover,
            .content-tab.active {
                background: var(--quantum-accent, #4facfe);
                color: white;
            }

            .content-main {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: 24px;
            }

            .content-sidebar {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }

            .content-sidebar > div {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .content-sidebar h3 {
                color: white;
                margin: 0 0 12px 0;
                font-size: 16px;
                font-weight: 600;
            }

            .content-feed {
                position: relative;
            }

            .content-tab-panel {
                display: none;
            }

            .content-tab-panel.active {
                display: block;
            }

            .article-card {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: var(--transition-smooth, all 0.3s ease);
                cursor: pointer;
                position: relative;
            }

            .article-card:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
                box-shadow: var(--quantum-shadow-medium, 0 8px 25px rgba(0, 0, 0, 0.3));
            }

            .article-card.read {
                opacity: 0.7;
            }

            .article-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 12px;
            }

            .article-meta {
                display: flex;
                gap: 12px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
                align-items: center;
            }

            .article-source {
                font-weight: 600;
                color: var(--quantum-accent, #4facfe);
            }

            .article-time {
                position: relative;
            }

            .article-sentiment {
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }

            .article-sentiment.positive {
                background: var(--quantum-success, #43e97b);
                color: white;
            }

            .article-sentiment.negative {
                background: var(--quantum-danger, #ff6b6b);
                color: white;
            }

            .article-sentiment.neutral {
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }

            .article-actions {
                display: flex;
                gap: 8px;
            }

            .article-action-btn {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: var(--transition-smooth, all 0.2s ease);
                font-size: 14px;
            }

            .article-action-btn:hover {
                color: white;
                background: rgba(255, 255, 255, 0.1);
            }

            .article-action-btn.bookmarked {
                color: var(--quantum-warning, #feca57);
            }

            .article-title {
                color: white;
                font-size: 18px;
                font-weight: 600;
                line-height: 1.3;
                margin-bottom: 8px;
                text-decoration: none;
            }

            .article-title:hover {
                color: var(--quantum-accent, #4facfe);
            }

            .article-summary {
                color: rgba(255, 255, 255, 0.8);
                line-height: 1.5;
                margin-bottom: 12px;
                font-size: 14px;
            }

            .article-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin-bottom: 12px;
            }

            .article-tag {
                background: var(--quantum-primary, rgba(102, 126, 234, 0.3));
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 500;
            }

            .article-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }

            .article-engagement {
                display: flex;
                gap: 16px;
                align-items: center;
            }

            .engagement-item {
                display: flex;
                align-items: center;
                gap: 4px;
            }

            .trending-item,
            .mover-item,
            .recommendation-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .trending-item:last-child,
            .mover-item:last-child,
            .recommendation-item:last-child {
                border-bottom: none;
            }

            .trending-topic {
                color: white;
                font-weight: 500;
                font-size: 14px;
            }

            .trending-count {
                color: var(--quantum-accent, #4facfe);
                font-size: 12px;
                font-weight: 600;
            }

            .mover-symbol {
                color: white;
                font-weight: 600;
            }

            .mover-change {
                font-size: 12px;
                font-weight: 600;
            }

            .mover-change.positive {
                color: var(--quantum-success, #43e97b);
            }

            .mover-change.negative {
                color: var(--quantum-danger, #ff6b6b);
            }

            .recommendation-title {
                color: white;
                font-size: 14px;
            }

            .recommendation-score {
                color: var(--quantum-accent, #4facfe);
                font-size: 12px;
                font-weight: 600;
            }

            .load-more-container {
                text-align: center;
                margin-top: 20px;
            }

            .content-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                padding: 40px;
                color: rgba(255, 255, 255, 0.6);
            }

            .loading-spinner {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-left-color: var(--quantum-accent, #4facfe);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Responsive Design */
            @media (max-width: 1024px) {
                .content-main {
                    grid-template-columns: 250px 1fr;
                }
            }

            @media (max-width: 768px) {
                .content-main {
                    grid-template-columns: 1fr;
                }

                .content-sidebar {
                    order: 2;
                }

                .content-header {
                    flex-direction: column;
                    align-items: stretch;
                }

                .content-actions {
                    justify-content: center;
                }

                .filter-actions {
                    justify-content: center;
                }

                .content-tabs {
                    overflow-x: auto;
                    scrollbar-width: none;
                    -ms-overflow-style: none;
                }

                .content-tabs::-webkit-scrollbar {
                    display: none;
                }

                .content-tab {
                    min-width: 120px;
                }
            }

            @media (max-width: 480px) {
                .quantum-content-hub {
                    padding: 16px;
                    margin: 10px 0;
                }

                .article-card {
                    padding: 16px;
                }

                .article-title {
                    font-size: 16px;
                }

                .article-header {
                    flex-direction: column;
                    gap: 8px;
                }

                .search-input-group {
                    flex-direction: column;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setupContentEventListeners() {
        const hub = document.querySelector('.quantum-content-hub');
        if (!hub) return;

        // Refresh button
        const refreshBtn = hub.querySelector('.content-refresh-btn');
        refreshBtn?.addEventListener('click', () => this.refreshContent());

        // Filter button
        const filterBtn = hub.querySelector('.content-filter-btn');
        const filtersPanel = hub.querySelector('.content-filters');
        filterBtn?.addEventListener('click', () => {
            const isVisible = filtersPanel.style.display === 'block';
            filtersPanel.style.display = isVisible ? 'none' : 'block';
        });

        // Search button
        const searchBtn = hub.querySelector('.content-search-btn');
        const searchPanel = hub.querySelector('.content-search');
        searchBtn?.addEventListener('click', () => {
            const isVisible = searchPanel.style.display === 'block';
            searchPanel.style.display = isVisible ? 'none' : 'block';
        });

        // Filter controls
        this.setupFilterControls(hub);

        // Search controls
        this.setupSearchControls(hub);

        // Tab controls
        this.setupTabControls(hub);

        // Load more button
        const loadMoreBtn = hub.querySelector('.load-more-btn');
        loadMoreBtn?.addEventListener('click', () => this.loadMoreArticles());
    }

    setupFilterControls(hub) {
        const applyBtn = hub.querySelector('.apply-filters-btn');
        const clearBtn = hub.querySelector('.clear-filters-btn');

        applyBtn?.addEventListener('click', () => {
            this.applyFilters();
        });

        clearBtn?.addEventListener('click', () => {
            this.clearFilters();
        });

        // Auto-apply filters on change
        const filterSelects = hub.querySelectorAll('.content-filters select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.updateFilter(select.className.replace('filter-', ''), select.value);
            });
        });
    }

    setupSearchControls(hub) {
        const searchInput = hub.querySelector('.content-search-input');
        const searchBtn = hub.querySelector('.search-execute-btn');

        searchBtn?.addEventListener('click', () => {
            this.executeSearch(searchInput.value);
        });

        searchInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeSearch(searchInput.value);
            }
        });

        searchInput?.addEventListener('input', (e) => {
            this.updateSearchSuggestions(e.target.value);
        });
    }

    setupTabControls(hub) {
        const tabs = hub.querySelectorAll('.content-tab');
        const panels = hub.querySelectorAll('.content-tab-panel');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;

                // Update active states
                tabs.forEach(t => t.classList.remove('active'));
                panels.forEach(p => p.classList.remove('active'));

                tab.classList.add('active');
                hub.querySelector(`[data-tab="${tabName}"].content-tab-panel`)?.classList.add('active');

                // Load content for the tab
                this.loadTabContent(tabName);
            });
        });
    }

    async loadInitialContent() {
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadNews(),
                this.loadTrendingTopics(),
                this.loadMarketMovers(),
                this.loadAIRecommendations()
            ]);
            
            this.updateContentStats();
        } catch (error) {
            console.error('Failed to load initial content:', error);
            this.showError('Failed to load content. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async loadNews() {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/news`);
            const articles = response.ok ? await response.json() : this.getMockNews();
            
            this.articles.clear();
            articles.forEach(article => {
                this.articles.set(article.id, article);
            });
            
            this.renderArticles();
        } catch (error) {
            console.error('Failed to load news:', error);
            this.renderArticles(this.getMockNews());
        }
    }

    renderArticles(articles = null) {
        const container = document.querySelector('.articles-container');
        if (!container) return;

        const articlesToRender = articles || Array.from(this.articles.values());
        const filteredArticles = this.applyCurrentFilters(articlesToRender);

        container.innerHTML = '';

        if (filteredArticles.length === 0) {
            container.innerHTML = `
                <div class="no-articles">
                    <p>No articles found. Try other topics or clear filters.</p>
                    <button class="clear-filters-btn quantum-btn quantum-btn-secondary">Clear Filters</button>
                </div>
            `;
            return;
        }

        filteredArticles.slice(0, this.options.maxArticlesPerPage).forEach(article => {
            const articleElement = this.createArticleElement(article);
            container.appendChild(articleElement);
        });
    }

    createArticleElement(article) {
        const isRead = this.readArticles.has(article.id);
        const isBookmarked = this.bookmarks.has(article.id);
        
        const articleDiv = document.createElement('div');
        articleDiv.className = `article-card ${isRead ? 'read' : ''}`;
        articleDiv.dataset.articleId = article.id;

        articleDiv.innerHTML = `
            <div class="article-header">
                <div class="article-meta">
                    <span class="article-source">${article.source}</span>
                    <span class="article-time">${this.formatTimeAgo(article.timestamp)}</span>
                    ${article.sentiment ? `<span class="article-sentiment ${article.sentiment.label.toLowerCase()}">${article.sentiment.label}</span>` : ''}
                </div>
                <div class="article-actions">
                    <button class="article-action-btn bookmark-btn ${isBookmarked ? 'bookmarked' : ''}" title="Bookmark">
                        <i class="bi bi-bookmark${isBookmarked ? '-fill' : ''}"></i>
                    </button>
                    <button class="article-action-btn share-btn" title="Share">
                        <i class="bi bi-share"></i>
                    </button>
                    <button class="article-action-btn read-later-btn" title="Read Later">
                        <i class="bi bi-clock"></i>
                    </button>
                </div>
            </div>
            
            <a href="${article.url}" class="article-title" target="_blank" rel="noopener">
                ${article.title}
            </a>
            
            <p class="article-summary">${article.summary}</p>
            
            ${article.tags && article.tags.length > 0 ? `
                <div class="article-tags">
                    ${article.tags.map(tag => `<span class="article-tag">${tag}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="article-footer">
                <div class="article-engagement">
                    <div class="engagement-item">
                        <i class="bi bi-eye"></i>
                        <span>${article.views || 0}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="bi bi-chat"></i>
                        <span>${article.comments || 0}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="bi bi-heart"></i>
                        <span>${article.likes || 0}</span>
                    </div>
                </div>
                <div class="article-relevance">
                    ${article.relevanceScore ? `Relevance: ${(article.relevanceScore * 100).toFixed(0)}%` : ''}
                </div>
            </div>
        `;

        this.setupArticleEventListeners(articleDiv, article);
        return articleDiv;
    }

    setupArticleEventListeners(articleElement, article) {
        // Track article clicks
        const titleLink = articleElement.querySelector('.article-title');
        titleLink?.addEventListener('click', () => {
            this.markAsRead(article.id);
            this.trackArticleClick(article);
        });

        // Bookmark functionality
        const bookmarkBtn = articleElement.querySelector('.bookmark-btn');
        bookmarkBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleBookmark(article.id);
        });

        // Share functionality
        const shareBtn = articleElement.querySelector('.share-btn');
        shareBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.shareArticle(article);
        });

        // Read later functionality
        const readLaterBtn = articleElement.querySelector('.read-later-btn');
        readLaterBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.addToReadLater(article);
        });
    }

    async loadTrendingTopics() {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/trending`);
            const topics = response.ok ? await response.json() : this.getMockTrendingTopics();
            
            this.renderTrendingTopics(topics);
        } catch (error) {
            console.error('Failed to load trending topics:', error);
            this.renderTrendingTopics(this.getMockTrendingTopics());
        }
    }

    renderTrendingTopics(topics) {
        const container = document.querySelector('.trending-list');
        if (!container) return;

        container.innerHTML = topics.map(topic => `
            <div class="trending-item bg-blue-600 text-white rounded-full px-3 py-1" data-topic="${topic.name}">
                <span class="trending-topic">${topic.name}</span>
                <span class="trending-count">${topic.count}</span>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.trending-item').forEach(item => {
            item.addEventListener('click', () => {
                const topic = item.dataset.topic;
                this.searchByTopic(topic);
            });
        });
    }

    async loadMarketMovers() {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/market-movers`);
            const movers = response.ok ? await response.json() : this.getMockMarketMovers();
            
            this.renderMarketMovers(movers);
        } catch (error) {
            console.error('Failed to load market movers:', error);
            this.renderMarketMovers(this.getMockMarketMovers());
        }
    }

    renderMarketMovers(movers) {
        const container = document.querySelector('.movers-list');
        if (!container) return;

        container.innerHTML = movers.map(mover => `
            <div class="mover-item" data-symbol="${mover.symbol}">
                <span class="mover-symbol">${mover.symbol}</span>
                <span class="mover-change ${mover.change >= 0 ? 'positive' : 'negative'}">
                    ${mover.change >= 0 ? '+' : ''}${mover.change.toFixed(2)}%
                </span>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.mover-item').forEach(item => {
            item.addEventListener('click', () => {
                const symbol = item.dataset.symbol;
                this.searchBySymbol(symbol);
            });
        });
    }

    async loadAIRecommendations() {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/ai-recommendations`);
            const recommendations = response.ok ? await response.json() : this.getMockAIRecommendations();
            
            this.renderAIRecommendations(recommendations);
        } catch (error) {
            console.error('Failed to load AI recommendations:', error);
            this.renderAIRecommendations(this.getMockAIRecommendations());
        }
    }

    renderAIRecommendations(recommendations) {
        const container = document.querySelector('.recommendations-list');
        if (!container) return;

        container.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item" data-article-id="${rec.articleId}">
                <span class="recommendation-title">${rec.title}</span>
                <span class="recommendation-score">${(rec.score * 100).toFixed(0)}%</span>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.recommendation-item').forEach(item => {
            item.addEventListener('click', () => {
                const articleId = item.dataset.articleId;
                this.showArticle(articleId);
            });
        });
    }

    // Filter and search methods
    applyCurrentFilters(articles) {
        return articles.filter(article => {
            // Category filter
            if (this.filters.category !== 'all' && article.category !== this.filters.category) {
                return false;
            }

            // Sentiment filter
            if (this.filters.sentiment !== 'all' && article.sentiment?.label.toLowerCase() !== this.filters.sentiment) {
                return false;
            }

            // Timeframe filter
            if (this.filters.timeframe !== 'all') {
                const articleTime = new Date(article.timestamp);
                const now = new Date();
                const timeDiff = now - articleTime;

                switch (this.filters.timeframe) {
                    case '1h':
                        if (timeDiff > 60 * 60 * 1000) return false;
                        break;
                    case '24h':
                        if (timeDiff > 24 * 60 * 60 * 1000) return false;
                        break;
                    case '7d':
                        if (timeDiff > 7 * 24 * 60 * 60 * 1000) return false;
                        break;
                    case '30d':
                        if (timeDiff > 30 * 24 * 60 * 60 * 1000) return false;
                        break;
                }
            }

            // Source filter
            if (this.filters.source !== 'all' && article.source.toLowerCase() !== this.filters.source) {
                return false;
            }

            return true;
        });
    }

    updateFilter(filterType, value) {
        this.filters[filterType] = value;
        this.renderArticles();
        this.saveUserPreferences();
    }

    applyFilters() {
        const hub = document.querySelector('.quantum-content-hub');
        const selects = hub.querySelectorAll('.content-filters select');
        
        selects.forEach(select => {
            const filterType = select.className.replace('filter-', '');
            this.filters[filterType] = select.value;
        });

        this.renderArticles();
        this.saveUserPreferences();
        
        // Hide filters panel
        hub.querySelector('.content-filters').style.display = 'none';
    }

    clearFilters() {
        this.filters = {
            category: 'all',
            sentiment: 'all',
            timeframe: 'all',
            source: 'all'
        };

        // Update filter controls
        const hub = document.querySelector('.quantum-content-hub');
        const selects = hub.querySelectorAll('.content-filters select');
        selects.forEach(select => {
            select.value = 'all';
        });

        this.renderArticles();
        this.saveUserPreferences();
    }

    executeSearch(query) {
        if (!query.trim()) return;

        const articles = Array.from(this.articles.values());
        const searchResults = articles.filter(article => {
            const searchText = `${article.title} ${article.summary} ${article.tags?.join(' ') || ''}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });

        this.renderArticles(searchResults);
    }

    updateSearchSuggestions(query) {
        if (query.length < 2) return;

        const suggestions = this.generateSearchSuggestions(query);
        const container = document.querySelector('.search-suggestions');
        
        container.innerHTML = suggestions.map(suggestion => 
            `<span class="search-suggestion" data-query="${suggestion}">${suggestion}</span>`
        ).join('');

        // Add click handlers for suggestions
        container.querySelectorAll('.search-suggestion').forEach(item => {
            item.addEventListener('click', () => {
                const searchInput = document.querySelector('.content-search-input');
                searchInput.value = item.dataset.query;
                this.executeSearch(item.dataset.query);
            });
        });
    }

    generateSearchSuggestions(query) {
        // Generate search suggestions based on existing content
        const suggestions = new Set();
        
        this.articles.forEach(article => {
            // Add matching tags
            article.tags?.forEach(tag => {
                if (tag.toLowerCase().includes(query.toLowerCase())) {
                    suggestions.add(tag);
                }
            });

            // Add matching keywords from title
            const words = article.title.toLowerCase().split(' ');
            words.forEach(word => {
                if (word.includes(query.toLowerCase()) && word.length > 3) {
                    suggestions.add(word);
                }
            });
        });

        return Array.from(suggestions).slice(0, 5);
    }

    // Content interaction methods
    markAsRead(articleId) {
        this.readArticles.add(articleId);
        this.saveUserPreferences();
        
        // Update UI
        const articleElement = document.querySelector(`[data-article-id="${articleId}"]`);
        articleElement?.classList.add('read');
    }

    toggleBookmark(articleId) {
        if (this.bookmarks.has(articleId)) {
            this.bookmarks.delete(articleId);
        } else {
            this.bookmarks.add(articleId);
        }
        
        this.saveUserPreferences();
        this.updateBookmarkUI(articleId);
    }

    updateBookmarkUI(articleId) {
        const articleElement = document.querySelector(`[data-article-id="${articleId}"]`);
        const bookmarkBtn = articleElement?.querySelector('.bookmark-btn');
        const icon = bookmarkBtn?.querySelector('i');
        
        if (this.bookmarks.has(articleId)) {
            bookmarkBtn?.classList.add('bookmarked');
            if (icon) icon.className = 'bi bi-bookmark-fill';
        } else {
            bookmarkBtn?.classList.remove('bookmarked');
            if (icon) icon.className = 'bi bi-bookmark';
        }
    }

    shareArticle(article) {
        if (navigator.share) {
            navigator.share({
                title: article.title,
                text: article.summary,
                url: article.url
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(article.url).then(() => {
                this.showNotification('Article link copied to clipboard!');
            });
        }
    }

    addToReadLater(article) {
        // Add to read later list (could integrate with browser reading list)
        this.showNotification('Article added to read later list!');
    }

    trackArticleClick(article) {
        // Track article engagement for analytics
        if (window.quantumAI) {
            window.quantumAI.trackEvent('article_click', {
                articleId: article.id,
                category: article.category,
                source: article.source
            });
        }
    }

    searchByTopic(topic) {
        const searchInput = document.querySelector('.content-search-input');
        if (searchInput) searchInput.value = topic;
        this.executeSearch(topic);
    }

    searchBySymbol(symbol) {
        const searchInput = document.querySelector('.content-search-input');
        if (searchInput) searchInput.value = symbol;
        this.executeSearch(symbol);
    }

    // Tab content loading
    async loadTabContent(tabName) {
        switch (tabName) {
            case 'news':
                // Already loaded in initial content
                break;
            case 'analysis':
                await this.loadAnalysisContent();
                break;
            case 'insights':
                await this.loadInsightsContent();
                break;
            case 'bookmarks':
                this.loadBookmarksContent();
                break;
        }
    }

    async loadAnalysisContent() {
        // Load analysis articles
        const container = document.querySelector('.analysis-container');
        if (!container) return;

        const analysisArticles = Array.from(this.articles.values())
            .filter(article => article.category === 'analysis' || article.type === 'analysis');

        container.innerHTML = analysisArticles.map(article => 
            this.createArticleElement(article).outerHTML
        ).join('');
    }

    async loadInsightsContent() {
        // Load AI-generated insights
        const container = document.querySelector('.insights-container');
        if (!container) return;

        if (window.quantumAI) {
            const insights = await window.quantumAI.getInsights();
            this.renderInsights(insights, container);
        } else {
            container.innerHTML = '<p>AI insights are not available.</p>';
        }
    }

    renderInsights(insights, container) {
        container.innerHTML = insights.map(insight => `
            <div class="insight-card">
                <div class="insight-header">
                    <h3>${insight.title}</h3>
                    <span class="insight-importance">${(insight.importance * 100).toFixed(0)}%</span>
                </div>
                <p class="insight-description">${insight.description}</p>
                ${insight.actions ? `
                    <div class="insight-actions">
                        ${insight.actions.map(action => `<span class="insight-action">${action}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    loadBookmarksContent() {
        const container = document.querySelector('.bookmarks-container');
        if (!container) return;

        const bookmarkedArticles = Array.from(this.articles.values())
            .filter(article => this.bookmarks.has(article.id));

        if (bookmarkedArticles.length === 0) {
            container.innerHTML = '<p>No bookmarked articles yet.</p>';
            return;
        }

        container.innerHTML = bookmarkedArticles.map(article => 
            this.createArticleElement(article).outerHTML
        ).join('');
    }

    // Auto-refresh functionality
    setupAutoRefresh() {
        if (!this.options.enableRealtime) return;

        setInterval(() => {
            this.refreshContent(false); // Silent refresh
        }, this.options.autoRefreshInterval);
    }

    async refreshContent(showLoading = true) {
        if (showLoading) this.showLoading(true);

        try {
            await this.loadNews();
            await this.loadTrendingTopics();
            await this.loadMarketMovers();
            await this.loadAIRecommendations();
            
            this.updateContentStats();
            this.updateLastUpdatedTime();
            
            if (showLoading) this.showNotification('Content updated successfully!');
        } catch (error) {
            console.error('Failed to refresh content:', error);
            if (showLoading) this.showNotification('Failed to update content. Please try again.');
        } finally {
            if (showLoading) this.showLoading(false);
        }
    }

    // Utility methods
    updateContentStats() {
        const countElement = document.querySelector('.article-count');
        if (countElement) {
            countElement.textContent = `${this.articles.size} articles`;
        }
    }

    updateLastUpdatedTime() {
        const timeElement = document.querySelector('.last-updated');
        if (timeElement) {
            timeElement.textContent = 'Just now';
        }
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

    showLoading(show) {
        const loader = document.querySelector('.content-loading');
        if (loader) {
            loader.style.display = show ? 'flex' : 'none';
        }
    }

    showNotification(message) {
        // Create and show toast notification
        const notification = document.createElement('div');
        notification.className = 'content-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--quantum-success, #43e97b);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showError(message) {
        this.showNotification(message);
    }

    // Mock data methods (for demo purposes)
    getMockNews() {
        return [
            {
                id: '1',
                title: 'Market Rally Continues as Tech Stocks Surge',
                summary: 'Technology stocks led market gains today as investors showed renewed confidence in the sector...',
                url: '#',
                source: 'QuantumNews',
                category: 'market',
                timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
                tags: ['technology', 'stocks', 'market'],
                sentiment: { label: 'POSITIVE', score: 0.8 },
                views: 1250,
                comments: 45,
                likes: 89,
                relevanceScore: 0.95
            },
            {
                id: '2',
                title: 'Federal Reserve Signals Potential Rate Changes',
                summary: 'Federal Reserve officials hinted at possible interest rate adjustments in upcoming meetings...',
                url: '#',
                source: 'Reuters',
                category: 'economy',
                timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
                tags: ['federal-reserve', 'interest-rates', 'economy'],
                sentiment: { label: 'NEUTRAL', score: 0.1 },
                views: 2100,
                comments: 78,
                likes: 156,
                relevanceScore: 0.87
            },
            {
                id: '3',
                title: 'Cryptocurrency Market Shows Mixed Signals',
                summary: 'Bitcoin and major altcoins display divergent patterns as regulatory clarity remains uncertain...',
                url: '#',
                source: 'Bloomberg',
                category: 'crypto',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                tags: ['cryptocurrency', 'bitcoin', 'regulation'],
                sentiment: { label: 'NEGATIVE', score: -0.3 },
                views: 890,
                comments: 23,
                likes: 34,
                relevanceScore: 0.72
            }
        ];
    }

    getMockTrendingTopics() {
        return [
            { name: 'AI Stocks', count: '1.2K' },
            { name: 'Fed Policy', count: '890' },
            { name: 'Crypto Regulation', count: '654' },
            { name: 'Tech Earnings', count: '432' },
            { name: 'Green Energy', count: '289' }
        ];
    }

    getMockMarketMovers() {
        return [
            { symbol: 'NVDA', change: 5.67 },
            { symbol: 'TSLA', change: -2.34 },
            { symbol: 'AAPL', change: 1.89 },
            { symbol: 'GOOGL', change: 3.21 },
            { symbol: 'MSFT', change: -0.45 }
        ];
    }

    getMockAIRecommendations() {
        return [
            { title: 'Tech Stock Analysis Deep Dive', score: 0.95, articleId: '1' },
            { title: 'Market Volatility Ahead', score: 0.87, articleId: '2' },
            { title: 'Portfolio Rebalancing Tips', score: 0.73, articleId: '3' }
        ];
    }

    // Public API methods
    addArticle(article) {
        this.articles.set(article.id, article);
        this.renderArticles();
    }

    removeArticle(articleId) {
        this.articles.delete(articleId);
        this.renderArticles();
    }

    getBookmarkedArticles() {
        return Array.from(this.bookmarks).map(id => this.articles.get(id)).filter(Boolean);
    }

    // Cleanup
    destroy() {
        this.articles.clear();
        this.categories.clear();
        this.bookmarks.clear();
        this.readArticles.clear();
    }
}

// Initialize QuantumContent when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.quantumContent = new QuantumContent();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumContent;
}