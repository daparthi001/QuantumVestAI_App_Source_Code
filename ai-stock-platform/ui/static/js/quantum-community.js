/**
 * QuantumVestAI Community Features
 * Forums, gamification, and social engagement
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumCommunity {
    constructor() {
        this.userId = this.getCurrentUserId();
        this.userLevel = this.getUserLevel();
        this.userPoints = this.getUserPoints();
        this.achievements = this.getUserAchievements();
        
        this.init();
    }

    init() {
        this.createCommunityInterface();
        this.setupEventListeners();
        this.loadUserStats();
        this.checkForNewAchievements();
    }

    createCommunityInterface() {
        // Create community hub if it doesn't exist
        const existingHub = document.querySelector('.quantum-community-hub');
        if (existingHub) return;

        const hub = document.createElement('div');
        hub.className = 'quantum-community-hub';
        hub.innerHTML = this.getCommunityHubHTML();

        // Add to navigation or create floating button
        const nav = document.querySelector('.quantum-nav-container');
        if (nav) {
            nav.appendChild(hub);
        } else {
            this.createFloatingCommunityButton();
        }

        this.addCommunityStyles();
    }

    getCommunityHubHTML() {
        return `
            <div class="community-toggle quantum-btn quantum-btn-secondary" data-i18n="community.toggle">
                <i class="bi bi-people-fill"></i>
                <span class="community-text">Community</span>
                ${this.userPoints > 0 ? `<span class="points-badge">${this.formatNumber(this.userPoints)}</span>` : ''}
            </div>
            
            <div class="community-dropdown" style="display: none;">
                <div class="community-header">
                    <div class="user-profile">
                        <div class="user-avatar">
                            <img src="${this.getUserAvatar()}" alt="User Avatar" onerror="this.style.display='none'">
                            <div class="level-badge">L${this.userLevel}</div>
                        </div>
                        <div class="user-info">
                            <div class="username">${this.getUsername()}</div>
                            <div class="user-title">${this.getUserTitle()}</div>
                        </div>
                    </div>
                    <div class="user-stats">
                        <div class="stat-item">
                            <span class="stat-value">${this.formatNumber(this.userPoints)}</span>
                            <span class="stat-label" data-i18n="community.points">Points</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${this.achievements.length}</span>
                            <span class="stat-label" data-i18n="community.achievements">Badges</span>
                        </div>
                    </div>
                </div>
                
                <div class="community-navigation">
                    <button class="community-nav-btn active" data-tab="forum">
                        <i class="bi bi-chat-square-text"></i>
                        <span data-i18n="community.forum">Forum</span>
                    </button>
                    <button class="community-nav-btn" data-tab="leaderboard">
                        <i class="bi bi-trophy"></i>
                        <span data-i18n="community.leaderboard">Leaderboard</span>
                    </button>
                    <button class="community-nav-btn" data-tab="achievements">
                        <i class="bi bi-award"></i>
                        <span data-i18n="community.achievements">Achievements</span>
                    </button>
                    <button class="community-nav-btn" data-tab="social">
                        <i class="bi bi-share"></i>
                        <span data-i18n="community.social">Social</span>
                    </button>
                </div>
                
                <div class="community-content">
                    <div class="community-tab-content active" data-tab="forum">
                        ${this.getForumHTML()}
                    </div>
                    <div class="community-tab-content" data-tab="leaderboard">
                        ${this.getLeaderboardHTML()}
                    </div>
                    <div class="community-tab-content" data-tab="achievements">
                        ${this.getAchievementsHTML()}
                    </div>
                    <div class="community-tab-content" data-tab="social">
                        ${this.getSocialHTML()}
                    </div>
                </div>
            </div>
        `;
    }

    getForumHTML() {
        return `
            <div class="forum-container">
                <div class="forum-header">
                    <h3 data-i18n="forum.discussions">Recent Discussions</h3>
                    <button class="new-topic-btn quantum-btn quantum-btn-primary" data-i18n="forum.new_topic">
                        New Topic
                    </button>
                </div>
                
                <div class="forum-categories">
                    <div class="category-tabs">
                        <button class="category-tab active" data-category="all" data-i18n="forum.all">All</button>
                        <button class="category-tab" data-category="market" data-i18n="forum.market">Market Talk</button>
                        <button class="category-tab" data-category="strategies" data-i18n="forum.strategies">Strategies</button>
                        <button class="category-tab" data-category="ai" data-i18n="forum.ai">AI Insights</button>
                        <button class="category-tab" data-category="help" data-i18n="forum.help">Help</button>
                    </div>
                </div>
                
                <div class="forum-topics" id="forum-topics">
                    ${this.getTopicsHTML()}
                </div>
                
                <div class="forum-pagination">
                    <button class="load-more-btn quantum-btn quantum-btn-secondary" data-i18n="common.load_more">
                        Load More
                    </button>
                </div>
            </div>
        `;
    }

    getTopicsHTML() {
        // Mock forum topics - in real app, fetch from API
        const topics = [
            {
                id: 1,
                title: "Q4 Market Predictions - What are your thoughts?",
                author: "TradingMaster",
                category: "market",
                replies: 23,
                lastReply: "2 hours ago",
                isPinned: true,
                hasNewReplies: true
            },
            {
                id: 2,
                title: "Best AI trading strategies for 2025",
                author: "AIInvestor",
                category: "ai",
                replies: 15,
                lastReply: "4 hours ago",
                isPinned: false,
                hasNewReplies: false
            },
            {
                id: 3,
                title: "Portfolio diversification tips",
                author: "WealthBuilder",
                category: "strategies",
                replies: 8,
                lastReply: "1 day ago",
                isPinned: false,
                hasNewReplies: true
            }
        ];

        return topics.map(topic => `
            <div class="forum-topic ${topic.isPinned ? 'pinned' : ''}" data-topic-id="${topic.id}">
                <div class="topic-info">
                    ${topic.isPinned ? '<i class="bi bi-pin-fill pin-icon"></i>' : ''}
                    <div class="topic-title">
                        <a href="/forum/topic/${topic.id}" class="topic-link">
                            ${topic.title}
                            ${topic.hasNewReplies ? '<span class="new-badge">New</span>' : ''}
                        </a>
                        <div class="topic-meta">
                            <span class="topic-author">by ${topic.author}</span>
                            <span class="topic-category">${topic.category}</span>
                        </div>
                    </div>
                </div>
                <div class="topic-stats">
                    <div class="stat">
                        <i class="bi bi-chat"></i>
                        <span>${topic.replies}</span>
                    </div>
                    <div class="last-reply">${topic.lastReply}</div>
                </div>
            </div>
        `).join('');
    }

    getLeaderboardHTML() {
        return `
            <div class="leaderboard-container">
                <div class="leaderboard-header">
                    <h3 data-i18n="leaderboard.title">Top Traders</h3>
                    <div class="leaderboard-filters">
                        <select class="leaderboard-period">
                            <option value="weekly" data-i18n="leaderboard.weekly">This Week</option>
                            <option value="monthly" data-i18n="leaderboard.monthly">This Month</option>
                            <option value="yearly" data-i18n="leaderboard.yearly">This Year</option>
                            <option value="all" data-i18n="leaderboard.all_time">All Time</option>
                        </select>
                    </div>
                </div>
                
                <div class="leaderboard-list">
                    ${this.getLeaderboardListHTML()}
                </div>
                
                <div class="user-ranking">
                    <div class="ranking-info">
                        <span data-i18n="leaderboard.your_rank">Your Rank:</span>
                        <strong>#${this.getUserRank()}</strong>
                    </div>
                </div>
            </div>
        `;
    }

    getLeaderboardListHTML() {
        // Mock leaderboard data
        const leaders = [
            { rank: 1, username: "QuantumTrader", points: 25420, level: 8, returns: "+24.5%" },
            { rank: 2, username: "AIWizard", points: 22180, level: 7, returns: "+22.1%" },
            { rank: 3, username: "MarketMaven", points: 19850, level: 6, returns: "+19.8%" },
            { rank: 4, username: "TechInvestor", points: 18200, level: 6, returns: "+18.2%" },
            { rank: 5, username: "ValueSeeker", points: 16750, level: 5, returns: "+16.7%" }
        ];

        return leaders.map(leader => `
            <div class="leaderboard-item ${leader.rank <= 3 ? 'top-three' : ''}">
                <div class="rank-badge rank-${leader.rank}">
                    ${leader.rank <= 3 ? this.getRankIcon(leader.rank) : leader.rank}
                </div>
                <div class="leader-info">
                    <div class="leader-name">${leader.username}</div>
                    <div class="leader-level">Level ${leader.level}</div>
                </div>
                <div class="leader-stats">
                    <div class="points">${this.formatNumber(leader.points)} pts</div>
                    <div class="returns ${leader.returns.startsWith('+') ? 'positive' : 'negative'}">
                        ${leader.returns}
                    </div>
                </div>
            </div>
        `).join('');
    }

    getAchievementsHTML() {
        return `
            <div class="achievements-container">
                <div class="achievements-header">
                    <h3 data-i18n="achievements.title">Achievements</h3>
                    <div class="achievement-progress">
                        <span>${this.achievements.length}/50 Unlocked</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(this.achievements.length / 50) * 100}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="achievements-categories">
                    <button class="achievement-category-tab active" data-category="all" data-i18n="achievements.all">All</button>
                    <button class="achievement-category-tab" data-category="trading" data-i18n="achievements.trading">Trading</button>
                    <button class="achievement-category-tab" data-category="social" data-i18n="achievements.social">Social</button>
                    <button class="achievement-category-tab" data-category="learning" data-i18n="achievements.learning">Learning</button>
                </div>
                
                <div class="achievements-grid">
                    ${this.getAchievementsGridHTML()}
                </div>
            </div>
        `;
    }

    getAchievementsGridHTML() {
        const allAchievements = [
            { id: 'first_trade', name: 'First Trade', description: 'Complete your first trade', icon: '💰', category: 'trading', unlocked: true },
            { id: 'profit_maker', name: 'Profit Maker', description: 'Earn your first profit', icon: '📈', category: 'trading', unlocked: true },
            { id: 'community_member', name: 'Community Member', description: 'Join the QuantumVestAI community', icon: '👥', category: 'social', unlocked: true },
            { id: 'forum_poster', name: 'Forum Contributor', description: 'Make your first forum post', icon: '💬', category: 'social', unlocked: false },
            { id: 'ai_user', name: 'AI Pioneer', description: 'Use AI predictions 10 times', icon: '🤖', category: 'trading', unlocked: true },
            { id: 'streak_keeper', name: 'Streak Keeper', description: 'Login for 7 days straight', icon: '🔥', category: 'learning', unlocked: false },
            { id: 'big_winner', name: 'Big Winner', description: 'Gain 20% or more on a trade', icon: '🏆', category: 'trading', unlocked: false },
            { id: 'diversified', name: 'Diversified Portfolio', description: 'Hold 10+ different stocks', icon: '📊', category: 'trading', unlocked: false },
            { id: 'mentor', name: 'Mentor', description: 'Help 5 community members', icon: '🎓', category: 'social', unlocked: false }
        ];

        return allAchievements.map(achievement => `
            <div class="achievement-item ${achievement.unlocked ? 'unlocked' : 'locked'}" 
                 data-achievement-id="${achievement.id}" 
                 data-category="${achievement.category}">
                <div class="achievement-icon">${achievement.icon}</div>
                <div class="achievement-content">
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-description">${achievement.description}</div>
                </div>
                ${achievement.unlocked ? '<div class="achievement-check">✓</div>' : '<div class="achievement-lock">🔒</div>'}
            </div>
        `).join('');
    }

    getSocialHTML() {
        return `
            <div class="social-container">
                <div class="social-header">
                    <h3 data-i18n="social.share_success">Share Your Success</h3>
                </div>
                
                <div class="social-stats">
                    <div class="social-stat-card">
                        <div class="stat-icon">📈</div>
                        <div class="stat-content">
                            <div class="stat-value">+${this.getUserReturns()}%</div>
                            <div class="stat-label" data-i18n="social.total_returns">Total Returns</div>
                        </div>
                        <button class="share-btn" data-share="returns">
                            <i class="bi bi-share"></i>
                        </button>
                    </div>
                    
                    <div class="social-stat-card">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-content">
                            <div class="stat-value">#${this.getUserRank()}</div>
                            <div class="stat-label" data-i18n="social.ranking">Ranking</div>
                        </div>
                        <button class="share-btn" data-share="rank">
                            <i class="bi bi-share"></i>
                        </button>
                    </div>
                    
                    <div class="social-stat-card">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-content">
                            <div class="stat-value">${this.achievements.length}</div>
                            <div class="stat-label" data-i18n="social.achievements">Achievements</div>
                        </div>
                        <button class="share-btn" data-share="achievements">
                            <i class="bi bi-share"></i>
                        </button>
                    </div>
                </div>
                
                <div class="social-platforms">
                    <h4 data-i18n="social.share_on">Share On</h4>
                    <div class="platform-buttons">
                        <button class="platform-btn twitter" data-platform="twitter">
                            <i class="bi bi-twitter"></i>
                            <span>Twitter</span>
                        </button>
                        <button class="platform-btn linkedin" data-platform="linkedin">
                            <i class="bi bi-linkedin"></i>
                            <span>LinkedIn</span>
                        </button>
                        <button class="platform-btn facebook" data-platform="facebook">
                            <i class="bi bi-facebook"></i>
                            <span>Facebook</span>
                        </button>
                        <button class="platform-btn copy" data-platform="copy">
                            <i class="bi bi-clipboard"></i>
                            <span data-i18n="social.copy_link">Copy Link</span>
                        </button>
                    </div>
                </div>
                
                <div class="social-referrals">
                    <h4 data-i18n="social.invite_friends">Invite Friends</h4>
                    <div class="referral-code">
                        <input type="text" value="${this.getReferralCode()}" readonly class="referral-input">
                        <button class="copy-referral-btn quantum-btn quantum-btn-secondary" data-i18n="common.copy">
                            Copy
                        </button>
                    </div>
                    <p class="referral-info" data-i18n="social.referral_bonus">
                        Earn 100 points for each friend who joins!
                    </p>
                </div>
            </div>
        `;
    }

    addCommunityStyles() {
        const style = document.createElement('style');
        style.id = 'quantum-community-styles';
        style.textContent = `
            .quantum-community-hub {
                position: relative;
                display: inline-block;
            }

            .community-toggle {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.3s ease);
                position: relative;
            }

            .community-toggle:hover {
                transform: translateY(-2px);
                box-shadow: var(--quantum-shadow-medium, 0 8px 25px rgba(0, 0, 0, 0.3));
            }

            .points-badge {
                background: var(--quantum-success, linear-gradient(135deg, #43e97b 0%, #38f9d7 100%));
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }

            .community-dropdown {
                position: absolute;
                top: 100%;
                right: 0;
                width: 400px;
                max-width: 90vw;
                background: var(--glass-bg, rgba(0, 0, 0, 0.9));
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 16px;
                padding: 0;
                z-index: 1000;
                margin-top: 8px;
                box-shadow: var(--quantum-shadow-strong, 0 16px 48px rgba(0, 0, 0, 0.4));
                overflow: hidden;
            }

            .community-header {
                padding: 20px;
                border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            }

            .user-profile {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
            }

            .user-avatar {
                position: relative;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: var(--quantum-primary, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }

            .user-avatar img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }

            .level-badge {
                position: absolute;
                bottom: -4px;
                right: -4px;
                background: var(--quantum-accent, #4facfe);
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
            }

            .user-info {
                flex: 1;
            }

            .username {
                font-weight: 600;
                color: white;
                margin-bottom: 4px;
            }

            .user-title {
                color: rgba(255, 255, 255, 0.6);
                font-size: 14px;
            }

            .user-stats {
                display: flex;
                gap: 20px;
            }

            .stat-item {
                text-align: center;
            }

            .stat-value {
                display: block;
                font-size: 18px;
                font-weight: 600;
                color: var(--quantum-accent, #4facfe);
            }

            .stat-label {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.6);
            }

            .community-navigation {
                display: flex;
                background: rgba(255, 255, 255, 0.05);
            }

            .community-nav-btn {
                flex: 1;
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                padding: 12px 8px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 4px;
                font-size: 12px;
            }

            .community-nav-btn:hover,
            .community-nav-btn.active {
                color: white;
                background: rgba(255, 255, 255, 0.1);
            }

            .community-nav-btn i {
                font-size: 16px;
            }

            .community-content {
                max-height: 400px;
                overflow-y: auto;
            }

            .community-tab-content {
                display: none;
                padding: 20px;
            }

            .community-tab-content.active {
                display: block;
            }

            /* Forum Styles */
            .forum-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }

            .forum-header h3 {
                color: white;
                margin: 0;
                font-size: 16px;
            }

            .new-topic-btn {
                padding: 6px 12px;
                font-size: 12px;
            }

            .category-tabs {
                display: flex;
                gap: 8px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }

            .category-tab {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                color: rgba(255, 255, 255, 0.7);
                padding: 6px 12px;
                border-radius: 16px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                font-size: 12px;
            }

            .category-tab:hover,
            .category-tab.active {
                background: var(--quantum-accent, #4facfe);
                color: white;
            }

            .forum-topic {
                display: flex;
                justify-content: space-between;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                transition: var(--transition-smooth, all 0.2s ease);
                border-left: 3px solid transparent;
            }

            .forum-topic:hover {
                background: rgba(255, 255, 255, 0.05);
            }

            .forum-topic.pinned {
                border-left-color: var(--quantum-warning, #feca57);
                background: rgba(254, 202, 87, 0.1);
            }

            .topic-info {
                flex: 1;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .pin-icon {
                color: var(--quantum-warning, #feca57);
                font-size: 12px;
            }

            .topic-link {
                color: white;
                text-decoration: none;
                font-weight: 500;
                font-size: 14px;
            }

            .topic-link:hover {
                color: var(--quantum-accent, #4facfe);
            }

            .new-badge {
                background: var(--quantum-danger, #ff6b6b);
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 10px;
                margin-left: 8px;
            }

            .topic-meta {
                color: rgba(255, 255, 255, 0.5);
                font-size: 12px;
                margin-top: 4px;
            }

            .topic-stats {
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: 4px;
            }

            .topic-stats .stat {
                display: flex;
                align-items: center;
                gap: 4px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }

            .last-reply {
                color: rgba(255, 255, 255, 0.5);
                font-size: 11px;
            }

            /* Leaderboard Styles */
            .leaderboard-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }

            .leaderboard-header h3 {
                color: white;
                margin: 0;
                font-size: 16px;
            }

            .leaderboard-period {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
            }

            .leaderboard-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                transition: var(--transition-smooth, all 0.2s ease);
            }

            .leaderboard-item:hover {
                background: rgba(255, 255, 255, 0.05);
            }

            .leaderboard-item.top-three {
                background: var(--quantum-primary, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
                background: linear-gradient(135deg, rgba(103, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
            }

            .rank-badge {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
            }

            .rank-1 { background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); color: #000; }
            .rank-2 { background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%); color: #000; }
            .rank-3 { background: linear-gradient(135deg, #cd7f32 0%, #d4943a 100%); color: #fff; }

            .leader-info {
                flex: 1;
            }

            .leader-name {
                font-weight: 600;
                color: white;
                margin-bottom: 2px;
            }

            .leader-level {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }

            .leader-stats {
                text-align: right;
            }

            .leader-stats .points {
                color: var(--quantum-accent, #4facfe);
                font-weight: 600;
                font-size: 14px;
            }

            .leader-stats .returns {
                font-size: 12px;
                font-weight: 600;
            }

            .leader-stats .returns.positive {
                color: var(--quantum-success, #43e97b);
            }

            .leader-stats .returns.negative {
                color: var(--quantum-danger, #ff6b6b);
            }

            .user-ranking {
                margin-top: 16px;
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                text-align: center;
                color: rgba(255, 255, 255, 0.8);
            }

            /* Achievements Styles */
            .achievements-header {
                margin-bottom: 16px;
            }

            .achievements-header h3 {
                color: white;
                margin: 0 0 8px 0;
                font-size: 16px;
            }

            .achievement-progress {
                display: flex;
                align-items: center;
                gap: 12px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }

            .progress-bar {
                flex: 1;
                height: 6px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                background: var(--quantum-success, linear-gradient(135deg, #43e97b 0%, #38f9d7 100%));
                transition: width 0.3s ease;
            }

            .achievements-categories {
                display: flex;
                gap: 8px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }

            .achievement-category-tab {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                color: rgba(255, 255, 255, 0.7);
                padding: 6px 12px;
                border-radius: 16px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                font-size: 12px;
            }

            .achievement-category-tab:hover,
            .achievement-category-tab.active {
                background: var(--quantum-accent, #4facfe);
                color: white;
            }

            .achievements-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 8px;
            }

            .achievement-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                border-radius: 8px;
                transition: var(--transition-smooth, all 0.2s ease);
                position: relative;
            }

            .achievement-item.unlocked {
                background: rgba(67, 233, 123, 0.1);
                border: 1px solid rgba(67, 233, 123, 0.3);
            }

            .achievement-item.locked {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                opacity: 0.6;
            }

            .achievement-icon {
                font-size: 24px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
            }

            .achievement-content {
                flex: 1;
            }

            .achievement-name {
                font-weight: 600;
                color: white;
                margin-bottom: 2px;
                font-size: 14px;
            }

            .achievement-description {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }

            .achievement-check,
            .achievement-lock {
                font-size: 16px;
            }

            .achievement-check {
                color: var(--quantum-success, #43e97b);
            }

            .achievement-lock {
                color: rgba(255, 255, 255, 0.3);
            }

            /* Social Styles */
            .social-header h3 {
                color: white;
                margin: 0 0 16px 0;
                font-size: 16px;
            }

            .social-stats {
                display: grid;
                grid-template-columns: 1fr;
                gap: 12px;
                margin-bottom: 20px;
            }

            .social-stat-card {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                transition: var(--transition-smooth, all 0.2s ease);
            }

            .social-stat-card:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .stat-icon {
                font-size: 24px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                background: var(--quantum-primary, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
            }

            .stat-content {
                flex: 1;
            }

            .stat-content .stat-value {
                font-size: 18px;
                font-weight: 600;
                color: white;
                margin-bottom: 2px;
            }

            .stat-content .stat-label {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }

            .share-btn {
                background: var(--quantum-accent, #4facfe);
                border: none;
                color: white;
                padding: 8px;
                border-radius: 6px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
            }

            .share-btn:hover {
                background: var(--quantum-primary, #667eea);
                transform: translateY(-2px);
            }

            .social-platforms h4 {
                color: white;
                margin: 0 0 12px 0;
                font-size: 14px;
            }

            .platform-buttons {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }

            .platform-btn {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                font-size: 12px;
                font-weight: 500;
            }

            .platform-btn.twitter { background: #1da1f2; color: white; }
            .platform-btn.linkedin { background: #0077b5; color: white; }
            .platform-btn.facebook { background: #1877f2; color: white; }
            .platform-btn.copy { background: rgba(255, 255, 255, 0.1); color: white; }

            .platform-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }

            .social-referrals {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }

            .social-referrals h4 {
                color: white;
                margin: 0 0 12px 0;
                font-size: 14px;
            }

            .referral-code {
                display: flex;
                gap: 8px;
                margin-bottom: 8px;
            }

            .referral-input {
                flex: 1;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
            }

            .copy-referral-btn {
                padding: 8px 12px;
                font-size: 12px;
            }

            .referral-info {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
                margin: 0;
            }

            /* Mobile Responsiveness */
            @media (max-width: 768px) {
                .community-dropdown {
                    width: 350px;
                    right: -20px;
                }

                .user-stats {
                    gap: 12px;
                }

                .platform-buttons {
                    grid-template-columns: 1fr;
                }

                .social-stats {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 480px) {
                .community-dropdown {
                    width: 90vw;
                    right: 5vw;
                    left: 5vw;
                }

                .forum-header {
                    flex-direction: column;
                    gap: 12px;
                    align-items: stretch;
                }

                .category-tabs {
                    justify-content: center;
                }

                .leaderboard-header {
                    flex-direction: column;
                    gap: 12px;
                    align-items: stretch;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setupEventListeners() {
        const toggle = document.querySelector('.community-toggle');
        const dropdown = document.querySelector('.community-dropdown');

        if (toggle && dropdown) {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = dropdown.style.display === 'block';
                dropdown.style.display = isVisible ? 'none' : 'block';
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.style.display = 'none';
                }
            });
        }

        // Tab navigation
        this.setupTabNavigation();
        
        // Forum interactions
        this.setupForumInteractions();
        
        // Social sharing
        this.setupSocialSharing();
        
        // Achievement interactions
        this.setupAchievementInteractions();
    }

    setupTabNavigation() {
        const navButtons = document.querySelectorAll('.community-nav-btn');
        const tabContents = document.querySelectorAll('.community-tab-content');

        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                
                // Update active states
                navButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                button.classList.add('active');
                document.querySelector(`[data-tab="${tab}"].community-tab-content`).classList.add('active');
            });
        });
    }

    setupForumInteractions() {
        // Category filtering
        const categoryTabs = document.querySelectorAll('.category-tab');
        categoryTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                categoryTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterTopics(tab.dataset.category);
            });
        });

        // New topic button
        const newTopicBtn = document.querySelector('.new-topic-btn');
        if (newTopicBtn) {
            newTopicBtn.addEventListener('click', () => {
                this.openNewTopicModal();
            });
        }

        // Load more
        const loadMoreBtn = document.querySelector('.load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                this.loadMoreTopics();
            });
        }
    }

    setupSocialSharing() {
        const shareButtons = document.querySelectorAll('.share-btn, .platform-btn');
        shareButtons.forEach(button => {
            button.addEventListener('click', () => {
                const shareType = button.dataset.share || button.dataset.platform;
                this.handleShare(shareType);
            });
        });

        // Copy referral code
        const copyReferralBtn = document.querySelector('.copy-referral-btn');
        if (copyReferralBtn) {
            copyReferralBtn.addEventListener('click', () => {
                const referralInput = document.querySelector('.referral-input');
                referralInput.select();
                document.execCommand('copy');
                this.showNotification('Referral code copied!');
            });
        }
    }

    setupAchievementInteractions() {
        const achievementTabs = document.querySelectorAll('.achievement-category-tab');
        achievementTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                achievementTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterAchievements(tab.dataset.category);
            });
        });

        // Achievement details
        const achievementItems = document.querySelectorAll('.achievement-item');
        achievementItems.forEach(item => {
            item.addEventListener('click', () => {
                this.showAchievementDetails(item.dataset.achievementId);
            });
        });
    }

    // Utility methods
    getCurrentUserId() {
        // Get from session/localStorage or return demo user
        return localStorage.getItem('quantum-user-id') || 'demo-user';
    }

    getUserLevel() {
        const points = this.getUserPoints();
        return Math.floor(points / 1000) + 1;
    }

    getUserPoints() {
        return parseInt(localStorage.getItem('quantum-user-points') || '2500');
    }

    getUserAchievements() {
        const stored = localStorage.getItem('quantum-user-achievements');
        return stored ? JSON.parse(stored) : ['first_trade', 'community_member', 'ai_user'];
    }

    getUserAvatar() {
        return localStorage.getItem('quantum-user-avatar') || '/static/img/default-avatar.png';
    }

    getUsername() {
        return localStorage.getItem('quantum-username') || 'QuantumTrader';
    }

    getUserTitle() {
        const level = this.getUserLevel();
        if (level >= 10) return 'Quantum Master';
        if (level >= 7) return 'AI Expert';
        if (level >= 5) return 'Market Analyst';
        if (level >= 3) return 'Rising Star';
        return 'Novice Trader';
    }

    getUserReturns() {
        return localStorage.getItem('quantum-user-returns') || '15.3';
    }

    getUserRank() {
        return parseInt(localStorage.getItem('quantum-user-rank') || '42');
    }

    getReferralCode() {
        return localStorage.getItem('quantum-referral-code') || 'QV' + this.userId.substring(0, 6).toUpperCase();
    }

    getRankIcon(rank) {
        const icons = { 1: '🥇', 2: '🥈', 3: '🥉' };
        return icons[rank] || rank;
    }

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    // Feature methods
    filterTopics(category) {
        const topics = document.querySelectorAll('.forum-topic');
        topics.forEach(topic => {
            if (category === 'all') {
                topic.style.display = 'flex';
            } else {
                const topicCategory = topic.querySelector('.topic-category').textContent;
                topic.style.display = topicCategory === category ? 'flex' : 'none';
            }
        });
    }

    filterAchievements(category) {
        const achievements = document.querySelectorAll('.achievement-item');
        achievements.forEach(achievement => {
            if (category === 'all') {
                achievement.style.display = 'flex';
            } else {
                const achievementCategory = achievement.dataset.category;
                achievement.style.display = achievementCategory === category ? 'flex' : 'none';
            }
        });
    }

    handleShare(type) {
        const url = window.location.href;
        const text = `Check out my QuantumVestAI performance! 📈 #QuantumVestAI #Trading`;

        switch (type) {
            case 'twitter':
                window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`);
                break;
            case 'linkedin':
                window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`);
                break;
            case 'facebook':
                window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`);
                break;
            case 'copy':
                navigator.clipboard.writeText(url).then(() => {
                    this.showNotification('Link copied to clipboard!');
                });
                break;
        }
    }

    loadMoreTopics() {
        // Simulate loading more topics
        this.showNotification('Loading more topics...');
        setTimeout(() => {
            this.showNotification('No more topics to load');
        }, 1000);
    }

    openNewTopicModal() {
        // Create and open new topic modal
        this.showNotification('New topic feature coming soon!');
    }

    showAchievementDetails(achievementId) {
        // Show achievement details modal
        this.showNotification(`Achievement details for ${achievementId} coming soon!`);
    }

    showNotification(message) {
        // Create and show toast notification
        const notification = document.createElement('div');
        notification.className = 'quantum-notification';
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

    checkForNewAchievements() {
        // Check if user has earned new achievements
        // This would be called after user actions
        const newAchievements = this.calculateNewAchievements();
        if (newAchievements.length > 0) {
            this.showAchievementUnlocked(newAchievements[0]);
        }
    }

    calculateNewAchievements() {
        // Mock achievement checking logic
        return []; // No new achievements for now
    }

    showAchievementUnlocked(achievement) {
        // Show achievement unlocked modal/animation
        this.showNotification(`🎉 Achievement Unlocked: ${achievement.name}!`);
    }

    loadUserStats() {
        // Load user statistics from API
        console.log('Loading user statistics...');
    }

    createFloatingCommunityButton() {
        const floatingBtn = document.createElement('button');
        floatingBtn.className = 'floating-community-btn quantum-btn quantum-btn-primary';
        floatingBtn.innerHTML = `
            <i class="bi bi-people-fill"></i>
            <span class="community-text">Community</span>
        `;
        floatingBtn.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            z-index: 1000;
            border-radius: 25px;
            box-shadow: var(--quantum-shadow-medium, 0 8px 25px rgba(0, 0, 0, 0.3));
        `;

        floatingBtn.addEventListener('click', () => {
            // Redirect to full community page
            window.location.href = '/community';
        });

        document.body.appendChild(floatingBtn);
    }
}

// Initialize community features when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const quantumCommunity = new QuantumCommunity();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumCommunity;
}