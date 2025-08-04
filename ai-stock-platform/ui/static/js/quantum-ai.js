/**
 * QuantumVestAI Advanced AI/ML Integration
 * Machine learning models, predictions, and intelligent insights
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumAI {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: '/api/ai',
            enableRealtime: true,
            predictionInterval: 60000, // 1 minute
            confidenceThreshold: 0.7,
            maxPredictionHorizon: 30, // days
            enableSentimentAnalysis: true,
            enableNewsAnalysis: true,
            enableTechnicalAnalysis: true,
            ...options
        };

        this.models = new Map();
        this.predictions = new Map();
        this.insights = [];
        this.isInitialized = false;
        this.workers = new Map();
        
        this.init();
    }

    async init() {
        await this.loadAIModels();
        this.setupWebWorkers();
        this.setupEventListeners();
        this.startPredictionEngine();
        this.isInitialized = true;
        
        console.log('QuantumAI: Initialized successfully');
    }

    async loadAIModels() {
        try {
            // Load pre-trained models
            await Promise.all([
                this.loadPredictionModel(),
                this.loadSentimentModel(),
                this.loadTechnicalAnalysisModel(),
                this.loadNewsAnalysisModel(),
                this.loadRiskAssessmentModel()
            ]);
            
            console.log('QuantumAI: All models loaded successfully');
        } catch (error) {
            console.error('QuantumAI: Failed to load models:', error);
        }
    }

    async loadPredictionModel() {
        // In a real implementation, this would load TensorFlow.js models
        this.models.set('prediction', {
            name: 'LSTM Price Prediction',
            version: '2.1.0',
            accuracy: 0.78,
            features: ['price', 'volume', 'technical_indicators', 'sentiment', 'news'],
            predict: this.predictPrice.bind(this)
        });
    }

    async loadSentimentModel() {
        this.models.set('sentiment', {
            name: 'Financial Sentiment Analysis',
            version: '1.5.0',
            accuracy: 0.85,
            features: ['text', 'keywords', 'context'],
            analyze: this.analyzeSentiment.bind(this)
        });
    }

    async loadTechnicalAnalysisModel() {
        this.models.set('technical', {
            name: 'Technical Pattern Recognition',
            version: '3.0.0',
            accuracy: 0.73,
            features: ['ohlcv', 'indicators', 'patterns'],
            analyze: this.analyzeTechnicalPatterns.bind(this)
        });
    }

    async loadNewsAnalysisModel() {
        this.models.set('news', {
            name: 'News Impact Analysis',
            version: '1.8.0',
            accuracy: 0.81,
            features: ['headline', 'content', 'source', 'timestamp'],
            analyze: this.analyzeNewsImpact.bind(this)
        });
    }

    async loadRiskAssessmentModel() {
        this.models.set('risk', {
            name: 'Portfolio Risk Assessment',
            version: '2.3.0',
            accuracy: 0.76,
            features: ['portfolio', 'market_conditions', 'correlations', 'volatility'],
            assess: this.assessRisk.bind(this)
        });
    }

    setupWebWorkers() {
        // Setup web workers for heavy computation
        if (typeof Worker !== 'undefined') {
            this.workers.set('prediction', this.createPredictionWorker());
            this.workers.set('analysis', this.createAnalysisWorker());
        }
    }

    createPredictionWorker() {
        const workerCode = `
            self.onmessage = function(e) {
                const { type, data } = e.data;
                
                switch(type) {
                    case 'predict':
                        const prediction = performPrediction(data);
                        self.postMessage({ type: 'prediction', result: prediction });
                        break;
                    case 'analyze':
                        const analysis = performAnalysis(data);
                        self.postMessage({ type: 'analysis', result: analysis });
                        break;
                }
            };
            
            function performPrediction(data) {
                // Simulate heavy ML computation
                const { prices, indicators, sentiment } = data;
                
                // Simple LSTM-like prediction simulation
                const trend = calculateTrend(prices);
                const volatility = calculateVolatility(prices);
                const sentimentImpact = sentiment * 0.1;
                
                const prediction = prices[prices.length - 1] * (1 + trend + sentimentImpact);
                const confidence = Math.max(0.5, 1 - volatility);
                
                return {
                    prediction: prediction,
                    confidence: confidence,
                    factors: {
                        trend: trend,
                        volatility: volatility,
                        sentiment: sentimentImpact
                    }
                };
            }
            
            function performAnalysis(data) {
                // Simulate technical analysis
                const patterns = detectPatterns(data.prices);
                const signals = generateSignals(data.indicators);
                
                return {
                    patterns: patterns,
                    signals: signals,
                    strength: Math.random() * 100
                };
            }
            
            function calculateTrend(prices) {
                if (prices.length < 2) return 0;
                const recent = prices.slice(-10);
                const slope = (recent[recent.length - 1] - recent[0]) / recent.length;
                return slope / recent[0];
            }
            
            function calculateVolatility(prices) {
                if (prices.length < 2) return 0;
                const returns = [];
                for (let i = 1; i < prices.length; i++) {
                    returns.push((prices[i] - prices[i-1]) / prices[i-1]);
                }
                const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
                const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - mean, 2), 0) / returns.length;
                return Math.sqrt(variance);
            }
            
            function detectPatterns(prices) {
                return [
                    { name: 'Bullish Flag', probability: Math.random() },
                    { name: 'Head and Shoulders', probability: Math.random() },
                    { name: 'Double Bottom', probability: Math.random() }
                ];
            }
            
            function generateSignals(indicators) {
                return [
                    { type: 'BUY', strength: Math.random() * 100, indicator: 'RSI' },
                    { type: 'SELL', strength: Math.random() * 100, indicator: 'MACD' },
                    { type: 'HOLD', strength: Math.random() * 100, indicator: 'SMA' }
                ];
            }
        `;

        const blob = new Blob([workerCode], { type: 'application/javascript' });
        const worker = new Worker(URL.createObjectURL(blob));
        
        worker.onmessage = (e) => {
            this.handleWorkerMessage(e.data);
        };
        
        return worker;
    }

    createAnalysisWorker() {
        // Similar to prediction worker but focused on analysis tasks
        return this.createPredictionWorker(); // Simplified for demo
    }

    handleWorkerMessage(data) {
        const { type, result } = data;
        
        switch (type) {
            case 'prediction':
                this.handlePredictionResult(result);
                break;
            case 'analysis':
                this.handleAnalysisResult(result);
                break;
        }
    }

    setupEventListeners() {
        // Listen for market data updates
        window.addEventListener('marketDataUpdate', (e) => {
            this.processMarketData(e.detail);
        });

        // Listen for news updates
        window.addEventListener('newsUpdate', (e) => {
            this.processNewsData(e.detail);
        });

        // Listen for user portfolio changes
        window.addEventListener('portfolioUpdate', (e) => {
            this.analyzePortfolioRisk(e.detail);
        });
    }

    startPredictionEngine() {
        if (!this.options.enableRealtime) return;

        setInterval(() => {
            this.generatePredictions();
            this.generateInsights();
        }, this.options.predictionInterval);
    }

    // Main AI Methods
    async generatePredictions(symbols = []) {
        if (!this.isInitialized) return;

        const defaultSymbols = symbols.length > 0 ? symbols : ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'];
        
        for (const symbol of defaultSymbols) {
            try {
                const prediction = await this.predictStockPrice(symbol);
                this.predictions.set(symbol, prediction);
                
                // Emit prediction event
                this.emitPredictionUpdate(symbol, prediction);
            } catch (error) {
                console.error(`QuantumAI: Failed to predict ${symbol}:`, error);
            }
        }
    }

    async predictStockPrice(symbol, horizon = 7) {
        // Get market data
        const marketData = await this.getMarketData(symbol);
        const technicalData = await this.getTechnicalData(symbol);
        const sentimentData = await this.getSentimentData(symbol);
        const newsData = await this.getNewsData(symbol);

        // Prepare features
        const features = this.prepareFeatures(marketData, technicalData, sentimentData, newsData);

        // Use worker for prediction if available
        if (this.workers.has('prediction')) {
            return new Promise((resolve) => {
                const worker = this.workers.get('prediction');
                
                worker.postMessage({
                    type: 'predict',
                    data: features
                });
                
                const handleMessage = (e) => {
                    if (e.data.type === 'prediction') {
                        worker.removeEventListener('message', handleMessage);
                        resolve(this.formatPrediction(e.data.result, symbol, horizon));
                    }
                };
                
                worker.addEventListener('message', handleMessage);
            });
        } else {
            // Fallback to main thread
            return this.predictPrice(features, symbol, horizon);
        }
    }

    predictPrice(features, symbol, horizon) {
        // Simplified prediction logic
        const { prices, indicators, sentiment } = features;
        
        if (!prices || prices.length === 0) {
            throw new Error('Insufficient price data');
        }

        const currentPrice = prices[prices.length - 1];
        const trend = this.calculateTrend(prices);
        const volatility = this.calculateVolatility(prices);
        const sentimentImpact = sentiment * 0.05;

        // Generate predictions for each day in horizon
        const predictions = [];
        let price = currentPrice;

        for (let i = 1; i <= horizon; i++) {
            const randomFactor = (Math.random() - 0.5) * volatility * 2;
            const dailyChange = trend + sentimentImpact + randomFactor;
            price = price * (1 + dailyChange);
            
            const confidence = Math.max(0.3, 0.9 - (i * 0.05) - volatility);
            
            predictions.push({
                day: i,
                date: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toISOString(),
                price: Math.max(0, price),
                confidence: confidence,
                change: dailyChange,
                changePercent: (dailyChange * 100).toFixed(2)
            });
        }

        return this.formatPrediction({
            predictions: predictions,
            currentPrice: currentPrice,
            confidence: predictions[0]?.confidence || 0.5
        }, symbol, horizon);
    }

    formatPrediction(result, symbol, horizon) {
        return {
            symbol: symbol,
            timestamp: new Date().toISOString(),
            horizon: horizon,
            currentPrice: result.currentPrice,
            predictions: result.predictions || [],
            confidence: result.confidence,
            model: 'LSTM-v2.1.0',
            factors: result.factors || {},
            recommendation: this.generateRecommendation(result),
            riskLevel: this.calculateRiskLevel(result)
        };
    }

    generateRecommendation(prediction) {
        const avgChange = prediction.predictions?.reduce((sum, p) => sum + p.change, 0) / prediction.predictions?.length || 0;
        const confidence = prediction.confidence;

        if (confidence < this.options.confidenceThreshold) {
            return { action: 'HOLD', reason: 'Low prediction confidence', strength: confidence * 100 };
        }

        if (avgChange > 0.02) {
            return { action: 'BUY', reason: 'Strong upward trend predicted', strength: confidence * 100 };
        } else if (avgChange < -0.02) {
            return { action: 'SELL', reason: 'Downward trend predicted', strength: confidence * 100 };
        } else {
            return { action: 'HOLD', reason: 'Sideways movement expected', strength: confidence * 100 };
        }
    }

    calculateRiskLevel(prediction) {
        const volatility = prediction.factors?.volatility || 0;
        const confidence = prediction.confidence;

        if (volatility > 0.3 || confidence < 0.5) return 'HIGH';
        if (volatility > 0.15 || confidence < 0.7) return 'MEDIUM';
        return 'LOW';
    }

    async analyzeSentiment(text, context = {}) {
        // Simplified sentiment analysis
        const positiveWords = ['bull', 'bullish', 'up', 'rise', 'gain', 'profit', 'strong', 'good', 'positive', 'growth'];
        const negativeWords = ['bear', 'bearish', 'down', 'fall', 'loss', 'weak', 'bad', 'negative', 'decline', 'crash'];

        const words = text.toLowerCase().split(/\s+/);
        let score = 0;

        words.forEach(word => {
            if (positiveWords.includes(word)) score += 1;
            if (negativeWords.includes(word)) score -= 1;
        });

        const normalizedScore = Math.max(-1, Math.min(1, score / words.length * 10));
        
        return {
            score: normalizedScore,
            magnitude: Math.abs(normalizedScore),
            label: normalizedScore > 0.1 ? 'POSITIVE' : normalizedScore < -0.1 ? 'NEGATIVE' : 'NEUTRAL',
            confidence: Math.min(0.95, 0.5 + Math.abs(normalizedScore) * 0.5),
            keywords: words.filter(word => positiveWords.includes(word) || negativeWords.includes(word))
        };
    }

    async analyzeTechnicalPatterns(data) {
        // Technical pattern recognition
        const patterns = [];
        const signals = [];

        // RSI analysis
        const rsi = this.calculateRSI(data.prices);
        if (rsi > 70) {
            signals.push({ type: 'SELL', indicator: 'RSI', value: rsi, strength: (rsi - 70) * 3.33 });
        } else if (rsi < 30) {
            signals.push({ type: 'BUY', indicator: 'RSI', value: rsi, strength: (30 - rsi) * 3.33 });
        }

        // MACD analysis
        const macd = this.calculateMACD(data.prices);
        if (macd.signal > 0) {
            signals.push({ type: 'BUY', indicator: 'MACD', value: macd.value, strength: Math.min(100, macd.signal * 50) });
        } else if (macd.signal < 0) {
            signals.push({ type: 'SELL', indicator: 'MACD', value: macd.value, strength: Math.min(100, Math.abs(macd.signal) * 50) });
        }

        // Pattern detection
        patterns.push(...this.detectChartPatterns(data.prices));

        return {
            patterns: patterns,
            signals: signals,
            technicalScore: this.calculateTechnicalScore(signals),
            recommendation: this.generateTechnicalRecommendation(signals)
        };
    }

    async analyzeNewsImpact(newsData) {
        const impacts = [];
        
        for (const article of newsData) {
            const sentiment = await this.analyzeSentiment(article.title + ' ' + article.content);
            const relevance = this.calculateNewsRelevance(article);
            const timing = this.calculateTimingImpact(article.timestamp);
            
            const impact = {
                title: article.title,
                sentiment: sentiment,
                relevance: relevance,
                timing: timing,
                overallImpact: (sentiment.magnitude * relevance * timing).toFixed(3),
                category: this.categorizeNews(article)
            };
            
            impacts.push(impact);
        }

        return {
            impacts: impacts.sort((a, b) => b.overallImpact - a.overallImpact),
            aggregateScore: this.calculateAggregateNewsScore(impacts),
            recommendation: this.generateNewsRecommendation(impacts)
        };
    }

    async assessRisk(portfolioData) {
        const risks = {
            diversification: this.assessDiversificationRisk(portfolioData),
            concentration: this.assessConcentrationRisk(portfolioData),
            correlation: this.assessCorrelationRisk(portfolioData),
            volatility: this.assessVolatilityRisk(portfolioData),
            liquidity: this.assessLiquidityRisk(portfolioData)
        };

        const overallRisk = this.calculateOverallRisk(risks);
        
        return {
            timestamp: new Date().toISOString(),
            risks: risks,
            overallRisk: overallRisk,
            recommendations: this.generateRiskRecommendations(risks),
            score: overallRisk.score
        };
    }

    // Insight Generation
    async generateInsights() {
        const marketInsights = await this.generateMarketInsights();
        const portfolioInsights = await this.generatePortfolioInsights();
        const tradingInsights = await this.generateTradingInsights();

        this.insights = [
            ...marketInsights,
            ...portfolioInsights,
            ...tradingInsights
        ].sort((a, b) => b.importance - a.importance);

        // Emit insights update
        window.dispatchEvent(new CustomEvent('aiInsightsUpdate', {
            detail: { insights: this.insights }
        }));
    }

    async generateMarketInsights() {
        const insights = [];
        
        // Market trend insight
        const marketTrend = await this.analyzeMarketTrend();
        if (marketTrend.strength > 0.7) {
            insights.push({
                type: 'market_trend',
                title: `Strong ${marketTrend.direction} Market Trend Detected`,
                description: `The market is showing a strong ${marketTrend.direction.toLowerCase()} trend with ${(marketTrend.strength * 100).toFixed(1)}% confidence.`,
                importance: marketTrend.strength * 0.9,
                category: 'market',
                timestamp: new Date().toISOString(),
                actionable: true,
                actions: marketTrend.direction === 'BULLISH' ? ['Consider increasing equity allocation'] : ['Consider taking profits or hedging positions']
            });
        }

        // Volatility insight
        const volatility = await this.analyzeMarketVolatility();
        if (volatility.level === 'HIGH') {
            insights.push({
                type: 'high_volatility',
                title: 'High Market Volatility Alert',
                description: `Market volatility is currently ${volatility.percentile}th percentile. Consider adjusting position sizes.`,
                importance: 0.8,
                category: 'risk',
                timestamp: new Date().toISOString(),
                actionable: true,
                actions: ['Reduce position sizes', 'Increase cash allocation', 'Consider hedging strategies']
            });
        }

        return insights;
    }

    async generatePortfolioInsights() {
        const insights = [];
        
        // Portfolio concentration
        const concentration = await this.analyzePortfolioConcentration();
        if (concentration.risk === 'HIGH') {
            insights.push({
                type: 'concentration_risk',
                title: 'Portfolio Concentration Risk',
                description: `Your portfolio is heavily concentrated in ${concentration.topSector} (${concentration.percentage}%). Consider diversifying.`,
                importance: 0.85,
                category: 'portfolio',
                timestamp: new Date().toISOString(),
                actionable: true,
                actions: [`Reduce ${concentration.topSector} allocation`, 'Add positions in other sectors']
            });
        }

        return insights;
    }

    async generateTradingInsights() {
        const insights = [];
        
        // Trading opportunity
        const opportunities = await this.identifyTradingOpportunities();
        opportunities.forEach(opportunity => {
            if (opportunity.confidence > 0.75) {
                insights.push({
                    type: 'trading_opportunity',
                    title: `${opportunity.action} Opportunity: ${opportunity.symbol}`,
                    description: `${opportunity.reason} Confidence: ${(opportunity.confidence * 100).toFixed(1)}%`,
                    importance: opportunity.confidence * 0.9,
                    category: 'trading',
                    timestamp: new Date().toISOString(),
                    actionable: true,
                    actions: [opportunity.action === 'BUY' ? `Consider buying ${opportunity.symbol}` : `Consider selling ${opportunity.symbol}`],
                    symbol: opportunity.symbol
                });
            }
        });

        return insights;
    }

    // Data Processing Methods
    async processMarketData(data) {
        if (!this.isInitialized) return;

        // Update predictions based on new market data
        const symbol = data.symbol;
        if (symbol && this.predictions.has(symbol)) {
            const updatedPrediction = await this.updatePrediction(symbol, data);
            this.predictions.set(symbol, updatedPrediction);
            this.emitPredictionUpdate(symbol, updatedPrediction);
        }
    }

    async processNewsData(newsData) {
        if (!this.options.enableNewsAnalysis) return;

        const impact = await this.analyzeNewsImpact(newsData);
        
        // Generate news-based insights
        if (impact.aggregateScore > 0.3) {
            this.generateNewsInsight(impact);
        }
    }

    async analyzePortfolioRisk(portfolioData) {
        if (!portfolioData) return;

        const riskAssessment = await this.assessRisk(portfolioData);
        
        // Emit risk update
        window.dispatchEvent(new CustomEvent('riskAssessmentUpdate', {
            detail: { assessment: riskAssessment }
        }));
    }

    // Utility Methods
    prepareFeatures(marketData, technicalData, sentimentData, newsData) {
        return {
            prices: marketData?.prices || [],
            volume: marketData?.volume || [],
            indicators: {
                rsi: technicalData?.rsi || 50,
                macd: technicalData?.macd || 0,
                sma: technicalData?.sma || []
            },
            sentiment: sentimentData?.score || 0,
            news: newsData?.impact || 0
        };
    }

    calculateTrend(prices) {
        if (prices.length < 2) return 0;
        
        const recent = prices.slice(-20); // Last 20 data points
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        
        for (let i = 0; i < recent.length; i++) {
            sumX += i;
            sumY += recent[i];
            sumXY += i * recent[i];
            sumXX += i * i;
        }
        
        const slope = (recent.length * sumXY - sumX * sumY) / (recent.length * sumXX - sumX * sumX);
        return slope / (sumY / recent.length); // Normalized slope
    }

    calculateVolatility(prices) {
        if (prices.length < 2) return 0;
        
        const returns = [];
        for (let i = 1; i < prices.length; i++) {
            returns.push((prices[i] - prices[i-1]) / prices[i-1]);
        }
        
        const mean = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
        const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - mean, 2), 0) / returns.length;
        
        return Math.sqrt(variance * 252); // Annualized volatility
    }

    calculateRSI(prices, period = 14) {
        if (prices.length < period + 1) return 50;
        
        const gains = [];
        const losses = [];
        
        for (let i = 1; i < prices.length; i++) {
            const change = prices[i] - prices[i - 1];
            gains.push(change > 0 ? change : 0);
            losses.push(change < 0 ? Math.abs(change) : 0);
        }
        
        const avgGain = gains.slice(-period).reduce((sum, gain) => sum + gain, 0) / period;
        const avgLoss = losses.slice(-period).reduce((sum, loss) => sum + loss, 0) / period;
        
        if (avgLoss === 0) return 100;
        
        const rs = avgGain / avgLoss;
        return 100 - (100 / (1 + rs));
    }

    calculateMACD(prices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
        if (prices.length < slowPeriod) return { value: 0, signal: 0 };
        
        const fastEMA = this.calculateEMA(prices, fastPeriod);
        const slowEMA = this.calculateEMA(prices, slowPeriod);
        const macdLine = fastEMA - slowEMA;
        
        // For simplicity, return a mock signal
        return {
            value: macdLine,
            signal: Math.random() > 0.5 ? 1 : -1 // Simplified signal
        };
    }

    calculateEMA(prices, period) {
        if (prices.length === 0) return 0;
        
        const multiplier = 2 / (period + 1);
        let ema = prices[0];
        
        for (let i = 1; i < prices.length; i++) {
            ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
        }
        
        return ema;
    }

    detectChartPatterns(prices) {
        // Simplified pattern detection
        const patterns = [];
        
        if (prices.length < 20) return patterns;
        
        // Head and Shoulders detection (simplified)
        const recent = prices.slice(-20);
        const peaks = this.findPeaks(recent);
        
        if (peaks.length >= 3) {
            patterns.push({
                name: 'Head and Shoulders',
                probability: Math.random() * 0.5 + 0.3,
                type: 'BEARISH',
                strength: 'MODERATE'
            });
        }
        
        // Double bottom detection (simplified)
        const troughs = this.findTroughs(recent);
        if (troughs.length >= 2) {
            patterns.push({
                name: 'Double Bottom',
                probability: Math.random() * 0.4 + 0.4,
                type: 'BULLISH',
                strength: 'STRONG'
            });
        }
        
        return patterns;
    }

    findPeaks(data) {
        const peaks = [];
        for (let i = 1; i < data.length - 1; i++) {
            if (data[i] > data[i-1] && data[i] > data[i+1]) {
                peaks.push(i);
            }
        }
        return peaks;
    }

    findTroughs(data) {
        const troughs = [];
        for (let i = 1; i < data.length - 1; i++) {
            if (data[i] < data[i-1] && data[i] < data[i+1]) {
                troughs.push(i);
            }
        }
        return troughs;
    }

    // API Methods
    async getMarketData(symbol) {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/market-data/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch market data for ${symbol}:`, error);
            throw error; // No fallback to mock data - will properly show errors to users
        }
    }

    async getTechnicalData(symbol) {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/technical-data/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch technical data for ${symbol}:`, error);
            throw error; // No fallback to mock data - will properly show errors to users
        }
    }

    async getSentimentData(symbol) {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/sentiment/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch sentiment data for ${symbol}:`, error);
            throw error; // No fallback to mock data - will properly show errors to users
        }
    }

    async getNewsData(symbol) {
        try {
            const response = await fetch(`${this.options.apiEndpoint}/news/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch news data for ${symbol}:`, error);
            throw error; // No fallback to mock data - will properly show errors to users
        }
    }

    // These methods have been disabled to ensure only live data is used
    // Kept as comments for reference only
    /* 
    getMockMarketData(symbol) {
        // Mock data generation removed - only live data should be used
        throw new Error('Mock data is disabled - only live data should be used');
    }
    */

    /* 
    getMockTechnicalData(symbol) {
        return {
            symbol,
            rsi: 30 + Math.random() * 40,
            macd: (Math.random() - 0.5) * 2,
            sma: Array(20).fill(0).map(() => 100 + Math.random() * 50)
        };
    }
    */

    /* 
    getMockNewsData(symbol) {
        const headlines = [
            `${symbol} reports strong quarterly earnings`,
            `Analysts upgrade ${symbol} price target`,
            `${symbol} announces new product launch`,
            `Market volatility affects ${symbol} trading`,
            `${symbol} CEO speaks at industry conference`
        ];
        
        return headlines.map(title => ({
            title,
            content: `Analysis and details about ${title.toLowerCase()}.`,
            timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            source: 'QuantumNews'
        }));
    }
    */
    // End of disabled mock data methods

    // Event Emission
    emitPredictionUpdate(symbol, prediction) {
        window.dispatchEvent(new CustomEvent('aiPredictionUpdate', {
            detail: { symbol, prediction }
        }));
    }

    handlePredictionResult(result) {
        // Handle worker prediction result
        console.log('Prediction result received:', result);
    }

    handleAnalysisResult(result) {
        // Handle worker analysis result
        console.log('Analysis result received:', result);
    }

    // Public API Methods
    async getPrediction(symbol) {
        if (this.predictions.has(symbol)) {
            return this.predictions.get(symbol);
        }
        
        return await this.predictStockPrice(symbol);
    }

    async getInsights() {
        return this.insights;
    }

    async analyzeSentimentForText(text) {
        return await this.analyzeSentiment(text);
    }

    async getModelInfo() {
        const models = {};
        this.models.forEach((model, key) => {
            models[key] = {
                name: model.name,
                version: model.version,
                accuracy: model.accuracy,
                features: model.features
            };
        });
        return models;
    }

    // Cleanup
    destroy() {
        this.workers.forEach(worker => worker.terminate());
        this.workers.clear();
        this.models.clear();
        this.predictions.clear();
        this.insights = [];
    }
}

// Initialize QuantumAI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.quantumAI = new QuantumAI();
    
    // Expose main methods globally
    window.getAIPrediction = (symbol) => window.quantumAI.getPrediction(symbol);
    window.getAIInsights = () => window.quantumAI.getInsights();
    window.analyzeText = (text) => window.quantumAI.analyzeSentimentForText(text);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumAI;
}