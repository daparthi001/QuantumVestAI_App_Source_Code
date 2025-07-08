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
        return localStorage.getItem('quantum-user-avatar') || '/static/img/avatars/default.png';
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
        // Enhanced topic loading with actual content
        this.showNotification('Loading more topics...');
        
        const forumContainer = document.querySelector('.forum-topics');
        if (!forumContainer) return;
        
        // Simulate API call to load more topics
        setTimeout(() => {
            const newTopics = this.generateAdditionalTopics();
            newTopics.forEach(topic => {
                const topicElement = this.createTopicElement(topic);
                forumContainer.appendChild(topicElement);
            });
            this.showNotification(`Loaded ${newTopics.length} new topics`);
        }, 1000);
    }

    generateAdditionalTopics() {
        const additionalTopics = [
            {
                id: 'topic-extra-1',
                title: 'AI vs Traditional Analysis: Performance Comparison',
                category: 'AI Insights',
                author: 'QuantumTrader',
                replies: 23,
                views: 189,
                lastActivity: '2 hours ago',
                isHot: true
            },
            {
                id: 'topic-extra-2',
                title: 'Risk Management in Volatile Markets',
                category: 'Strategies',
                author: 'RiskManager',
                replies: 15,
                views: 156,
                lastActivity: '4 hours ago',
                isHot: false
            },
            {
                id: 'topic-extra-3',
                title: 'Sentiment Analysis Success Stories',
                category: 'Market Talk',
                author: 'SentimentGuru',
                replies: 31,
                views: 245,
                lastActivity: '1 hour ago',
                isHot: true
            }
        ];
        return additionalTopics;
    }

    createTopicElement(topic) {
        const topicEl = document.createElement('div');
        topicEl.className = `forum-topic ${topic.isHot ? 'hot-topic' : ''}`;
        topicEl.innerHTML = `
            <div class="topic-content">
                <div class="topic-header">
                    <h4 class="topic-title">${topic.title}</h4>
                    <span class="topic-category">${topic.category}</span>
                    ${topic.isHot ? '<span class="hot-badge">🔥 Hot</span>' : ''}
                </div>
                <div class="topic-meta">
                    <span class="topic-author">by ${topic.author}</span>
                    <span class="topic-stats">${topic.replies} replies • ${topic.views} views</span>
                    <span class="topic-time">${topic.lastActivity}</span>
                </div>
            </div>
            <div class="topic-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="communityManager.viewTopic('${topic.id}')">
                    View Discussion
                </button>
            </div>
        `;
        return topicEl;
    }

    openNewTopicModal() {
        // Enhanced new topic modal with form
        const modal = document.createElement('div');
        modal.className = 'quantum-modal';
        modal.innerHTML = `
            <div class="modal-backdrop" onclick="this.parentElement.remove()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create New Discussion Topic</h3>
                    <button class="modal-close" onclick="this.closest('.quantum-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <form id="new-topic-form">
                        <div class="form-group">
                            <label for="topic-title">Topic Title</label>
                            <input type="text" id="topic-title" class="form-control" 
                                   placeholder="Enter a descriptive title..." required>
                        </div>
                        <div class="form-group">
                            <label for="topic-category">Category</label>
                            <select id="topic-category" class="form-control" required>
                                <option value="">Select a category</option>
                                <option value="market">Market Talk</option>
                                <option value="strategies">Investment Strategies</option>
                                <option value="ai">AI Insights</option>
                                <option value="education">Education</option>
                                <option value="general">General Discussion</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="topic-content">Content</label>
                            <textarea id="topic-content" class="form-control" rows="6" 
                                      placeholder="Share your thoughts, questions, or insights..." required></textarea>
                        </div>
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="topic-notify"> 
                                Notify me of replies
                            </label>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.quantum-modal').remove()">
                        Cancel
                    </button>
                    <button type="button" class="btn btn-primary" onclick="communityManager.submitNewTopic()">
                        Create Topic
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.getElementById('topic-title').focus();
    }

    submitNewTopic() {
        const form = document.getElementById('new-topic-form');
        const formData = new FormData(form);
        
        const title = document.getElementById('topic-title').value;
        const category = document.getElementById('topic-category').value;
        const content = document.getElementById('topic-content').value;
        const notify = document.getElementById('topic-notify').checked;
        
        if (!title || !category || !content) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        // Simulate API call
        this.showNotification('Creating topic...', 'info');
        
        setTimeout(() => {
            const newTopic = {
                id: 'topic-' + Date.now(),
                title: title,
                category: category,
                author: 'You',
                replies: 0,
                views: 1,
                lastActivity: 'Just now',
                isHot: false
            };
            
            // Add to topic list
            const forumContainer = document.querySelector('.forum-topics');
            if (forumContainer) {
                const topicElement = this.createTopicElement(newTopic);
                forumContainer.insertBefore(topicElement, forumContainer.firstChild);
            }
            
            // Update user points
            this.userPoints += 10;
            this.updatePointsDisplay();
            
            // Close modal
            document.querySelector('.quantum-modal').remove();
            
            this.showNotification('Topic created successfully! +10 points', 'success');
        }, 1500);
    }

    viewTopic(topicId) {
        // Enhanced topic viewing with detailed discussion
        const topic = this.getTopicDetails(topicId);
        
        const modal = document.createElement('div');
        modal.className = 'quantum-modal topic-modal';
        modal.innerHTML = `
            <div class="modal-backdrop" onclick="this.parentElement.remove()"></div>
            <div class="modal-content large">
                <div class="modal-header">
                    <div class="topic-header-info">
                        <h3>${topic.title}</h3>
                        <div class="topic-meta">
                            <span class="category-badge">${topic.category}</span>
                            <span class="author">by ${topic.author}</span>
                            <span class="stats">${topic.replies} replies • ${topic.views} views</span>
                        </div>
                    </div>
                    <button class="modal-close" onclick="this.closest('.quantum-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="topic-content">
                        <div class="original-post">
                            <div class="post-author">
                                <img src="/static/images/avatars/default.png" alt="${topic.author}" class="avatar">
                                <div class="author-info">
                                    <strong>${topic.author}</strong>
                                    <span class="post-time">${topic.lastActivity}</span>
                                </div>
                            </div>
                            <div class="post-content">
                                ${topic.content}
                            </div>
                            <div class="post-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="communityManager.likeTopic('${topicId}')">
                                    👍 Like (${topic.likes || 0})
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="communityManager.shareTopic('${topicId}')">
                                    📤 Share
                                </button>
                            </div>
                        </div>
                        
                        <div class="replies-section">
                            <h4>Replies (${topic.replies})</h4>
                            <div class="replies-list">
                                ${this.generateRepliesHTML(topic.replies)}
                            </div>
                        </div>
                        
                        <div class="reply-form">
                            <h5>Add Your Reply</h5>
                            <textarea id="reply-content" class="form-control" rows="4" 
                                      placeholder="Share your thoughts..."></textarea>
                            <div class="reply-actions">
                                <button class="btn btn-primary" onclick="communityManager.submitReply('${topicId}')">
                                    Post Reply
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    getTopicDetails(topicId) {
        // Simulated topic details - in real app, this would come from API
        const topics = {
            'topic-1': {
                title: 'Tesla Stock Analysis Discussion',
                category: 'Market Talk',
                author: 'ElonFan2024',
                content: 'What are your thoughts on Tesla\'s recent performance? The AI predictions show strong bullish sentiment.',
                replies: 12,
                views: 89,
                likes: 5,
                lastActivity: '2 hours ago'
            },
            'topic-2': {
                title: 'Best AI Trading Strategies for 2024',
                category: 'Strategies',
                author: 'AITrader',
                content: 'Looking to share and discuss the most effective AI trading strategies. What has worked for you?',
                replies: 8,
                views: 67,
                likes: 3,
                lastActivity: '4 hours ago'
            }
        };
        
        return topics[topicId] || {
            title: 'Discussion Topic',
            category: 'General',
            author: 'Unknown',
            content: 'Topic content not available.',
            replies: 0,
            views: 0,
            likes: 0,
            lastActivity: 'Unknown'
        };
    }

    generateRepliesHTML(replyCount) {
        if (replyCount === 0) {
            return '<p class="no-replies">No replies yet. Be the first to join the discussion!</p>';
        }
        
        let repliesHTML = '';
        for (let i = 0; i < Math.min(replyCount, 3); i++) {
            repliesHTML += `
                <div class="reply">
                    <div class="reply-author">
                        <img src="/static/images/avatars/user${i + 1}.png" alt="User" class="avatar-sm">
                        <div class="author-info">
                            <strong>Investor${i + 1}</strong>
                            <span class="reply-time">${Math.floor(Math.random() * 24)} hours ago</span>
                        </div>
                    </div>
                    <div class="reply-content">
                        ${this.generateSampleReply(i)}
                    </div>
                    <div class="reply-actions">
                        <button class="btn btn-sm btn-link">👍 ${Math.floor(Math.random() * 10)}</button>
                        <button class="btn btn-sm btn-link">Reply</button>
                    </div>
                </div>
            `;
        }
        
        if (replyCount > 3) {
            repliesHTML += `
                <div class="load-more-replies">
                    <button class="btn btn-outline-primary btn-sm" onclick="communityManager.loadMoreReplies()">
                        Load ${replyCount - 3} more replies
                    </button>
                </div>
            `;
        }
        
        return repliesHTML;
    }

    generateSampleReply(index) {
        const replies = [
            "Great analysis! I've been following this stock too and the AI predictions have been quite accurate.",
            "Thanks for sharing. I'm curious about the risk factors you've considered in this strategy.",
            "Interesting perspective. Have you backtested this approach over different market conditions?"
        ];
        return replies[index] || "Thanks for the discussion!";
    }

    submitReply(topicId) {
        const replyContent = document.getElementById('reply-content').value;
        if (!replyContent.trim()) {
            this.showNotification('Please enter a reply', 'error');
            return;
        }
        
        // Simulate API call
        this.showNotification('Posting reply...', 'info');
        
        setTimeout(() => {
            // Add reply to the list
            const repliesList = document.querySelector('.replies-list');
            if (repliesList) {
                const newReply = document.createElement('div');
                newReply.className = 'reply';
                newReply.innerHTML = `
                    <div class="reply-author">
                        <img src="/static/images/avatars/default.png" alt="You" class="avatar-sm">
                        <div class="author-info">
                            <strong>You</strong>
                            <span class="reply-time">Just now</span>
                        </div>
                    </div>
                    <div class="reply-content">
                        ${replyContent}
                    </div>
                    <div class="reply-actions">
                        <button class="btn btn-sm btn-link">👍 0</button>
                        <button class="btn btn-sm btn-link">Edit</button>
                    </div>
                `;
                repliesList.appendChild(newReply);
            }
            
            // Clear form
            document.getElementById('reply-content').value = '';
            
            // Update user points
            this.userPoints += 5;
            this.updatePointsDisplay();
            
            this.showNotification('Reply posted successfully! +5 points', 'success');
        }, 1000);
    }

    likeTopic(topicId) {
        // Enhanced like functionality
        this.showNotification('Topic liked! +2 points', 'success');
        this.userPoints += 2;
        this.updatePointsDisplay();
        
        // Update like count in UI
        const likeButton = document.querySelector(`button[onclick*="${topicId}"]`);
        if (likeButton) {
            const currentLikes = parseInt(likeButton.textContent.match(/\d+/)[0]) || 0;
            likeButton.innerHTML = `👍 Like (${currentLikes + 1})`;
            likeButton.disabled = true;
            likeButton.classList.add('liked');
        }
    }

    shareTopic(topicId) {
        // Enhanced sharing functionality
        const topic = this.getTopicDetails(topicId);
        const shareText = `Check out this discussion on QuantumVestAI: "${topic.title}"`;
        const shareUrl = `${window.location.origin}/community/topic/${topicId}`;
        
        if (navigator.share) {
            navigator.share({
                title: topic.title,
                text: shareText,
                url: shareUrl
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(`${shareText} ${shareUrl}`).then(() => {
                this.showNotification('Link copied to clipboard!', 'success');
            });
        }
    }

    updatePointsDisplay() {
        const pointsBadge = document.querySelector('.points-badge');
        if (pointsBadge) {
            pointsBadge.textContent = this.formatNumber(this.userPoints);
            pointsBadge.classList.add('points-updated');
            setTimeout(() => {
                pointsBadge.classList.remove('points-updated');
            }, 1000);
        }
    }

    showAchievementDetails(achievementId) {
        // Enhanced achievement details modal
        const achievement = this.getAchievementDetails(achievementId);
        
        const modal = document.createElement('div');
        modal.className = 'quantum-modal achievement-modal';
        modal.innerHTML = `
            <div class="modal-backdrop" onclick="this.parentElement.remove()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Achievement Details</h3>
                    <button class="modal-close" onclick="this.closest('.quantum-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="achievement-details">
                        <div class="achievement-icon large">
                            ${achievement.icon}
                        </div>
                        <h4>${achievement.name}</h4>
                        <p class="achievement-description">${achievement.description}</p>
                        <div class="achievement-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${achievement.progress}%"></div>
                            </div>
                            <span class="progress-text">${achievement.progress}% complete</span>
                        </div>
                        <div class="achievement-rewards">
                            <h5>Rewards</h5>
                            <ul>
                                <li>+${achievement.points} points</li>
                                <li>${achievement.badge} badge</li>
                                ${achievement.unlock ? `<li>Unlocks: ${achievement.unlock}</li>` : ''}
                            </ul>
                        </div>
                        ${achievement.tips ? `
                            <div class="achievement-tips">
                                <h5>Tips to Complete</h5>
                                <ul>
                                    ${achievement.tips.map(tip => `<li>${tip}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="this.closest('.quantum-modal').remove()">
                        Got it!
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    getAchievementDetails(achievementId) {
        const achievements = {
            'first-prediction': {
                name: 'First Prediction',
                icon: '🔮',
                description: 'Make your first AI-powered stock prediction',
                progress: 100,
                points: 50,
                badge: 'Predictor',
                tips: ['Visit the AI Predictions page', 'Select a stock to analyze', 'Review the prediction results']
            },
            'community-contributor': {
                name: 'Community Contributor',
                icon: '🤝',
                description: 'Actively participate in community discussions',
                progress: 60,
                points: 100,
                badge: 'Contributor',
                unlock: 'Premium discussion features',
                tips: ['Create new discussion topics', 'Reply to other members\' posts', 'Share helpful insights']
            },
            'portfolio-optimizer': {
                name: 'Portfolio Optimizer',
                icon: '⚖️',
                description: 'Use AI portfolio optimization 10 times',
                progress: 30,
                points: 200,
                badge: 'Optimizer',
                unlock: 'Advanced optimization features',
                tips: ['Use the portfolio optimization tool', 'Try different risk levels', 'Compare optimization results']
            }
        };
        
        return achievements[achievementId] || {
            name: 'Unknown Achievement',
            icon: '🏆',
            description: 'Achievement details not available',
            progress: 0,
            points: 0,
            badge: 'Unknown'
        };
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