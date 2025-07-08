/**
 * QuantumVestAI Internationalization System
 * Multi-language support for global recognition
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumI18n {
    constructor() {
        this.currentLanguage = localStorage.getItem('quantum-language') || 'en';
        this.translations = {};
        this.supportedLanguages = {
            'en': { name: 'English', flag: '🇺🇸', rtl: false },
            'es': { name: 'Español', flag: '🇪🇸', rtl: false },
            'fr': { name: 'Français', flag: '🇫🇷', rtl: false },
            'de': { name: 'Deutsch', flag: '🇩🇪', rtl: false },
            'zh': { name: '中文', flag: '🇨🇳', rtl: false },
            'ja': { name: '日本語', flag: '🇯🇵', rtl: false },
            'ko': { name: '한국어', flag: '🇰🇷', rtl: false },
            'ar': { name: 'العربية', flag: '🇸🇦', rtl: true },
            'hi': { name: 'हिन्दी', flag: '🇮🇳', rtl: false },
            'pt': { name: 'Português', flag: '🇧🇷', rtl: false },
            'ru': { name: 'Русский', flag: '🇷🇺', rtl: false },
            'it': { name: 'Italiano', flag: '🇮🇹', rtl: false }
        };
        
        this.init();
    }

    async init() {
        await this.loadTranslations();
        this.setupLanguageSelector();
        this.applyLanguage(this.currentLanguage);
        this.translatePage();
    }

    async loadTranslations() {
        // Load translation data for each supported language
        this.translations = {
            en: {
                // Navigation
                'nav.dashboard': 'Dashboard',
                'nav.portfolio': 'Portfolio',
                'nav.analytics': 'Analytics',
                'nav.market': 'Market',
                'nav.news': 'News',
                'nav.settings': 'Settings',
                'nav.login': 'Login',
                'nav.logout': 'Logout',
                'nav.register': 'Register',
                'nav.brand': 'QuantumVestAI',
                'nav.forecast': 'Forecast',
                'nav.profile': 'Profile',

                // Dashboard
                'dashboard.title': 'QuantumVestAI Dashboard',
                'dashboard.welcome': 'Welcome to QuantumVestAI',
                'dashboard.portfolio_value': 'Portfolio Value',
                'dashboard.daily_change': 'Daily Change',
                'dashboard.total_return': 'Total Return',
                'dashboard.market_cap': 'Market Cap',
                'dashboard.volume': 'Volume',
                'dashboard.live_data': 'Live Data',
                'dashboard.last_updated': 'Last Updated',

                // Common
                'common.loading': 'Loading...',
                'common.error': 'Error',
                'common.success': 'Success',
                'common.cancel': 'Cancel',
                'common.confirm': 'Confirm',
                'common.save': 'Save',
                'common.edit': 'Edit',
                'common.delete': 'Delete',
                'common.search': 'Search',
                'common.filter': 'Filter',
                'common.sort': 'Sort',
                'common.refresh': 'Refresh',

                // Authentication
                'auth.login': 'Login',
                'auth.register': 'Register',
                'auth.email': 'Email',
                'auth.password': 'Password',
                'auth.confirm_password': 'Confirm Password',
                'auth.forgot_password': 'Forgot Password?',
                'auth.remember_me': 'Remember Me',
                'auth.sign_in': 'Sign In',
                'auth.sign_up': 'Sign Up',
                'auth.logout': 'Logout',

                // Market
                'market.trending': 'Trending Stocks',
                'market.gainers': 'Top Gainers',
                'market.losers': 'Top Losers',
                'market.most_active': 'Most Active',
                'market.price': 'Price',
                'market.change': 'Change',
                'market.volume': 'Volume',

                // Features
                'features.ai_predictions': 'AI Predictions',
                'features.portfolio_optimization': 'Portfolio Optimization',
                'features.sentiment_analysis': 'Sentiment Analysis',
                'features.risk_assessment': 'Risk Assessment',
                'features.real_time_data': 'Real-time Data',
                'features.advanced_charts': 'Advanced Charts',

                // Settings
                'settings.language': 'Language',
                'settings.theme': 'Theme',
                'settings.notifications': 'Notifications',
                'settings.privacy': 'Privacy',
                'settings.account': 'Account',
                'settings.preferences': 'Preferences',

                // Time and Date
                'time.today': 'Today',
                'time.yesterday': 'Yesterday',
                'time.this_week': 'This Week',
                'time.this_month': 'This Month',
                'time.this_year': 'This Year',

                // Footer
                'footer.copyright': '© 2025 QuantumVestAI. All rights reserved.',
                'footer.privacy_policy': 'Privacy Policy',
                'footer.terms_of_service': 'Terms of Service',
                'footer.contact': 'Contact Us'
            },

            es: {
                // Navigation
                'nav.dashboard': 'Panel de Control',
                'nav.portfolio': 'Cartera',
                'nav.analytics': 'Análisis',
                'nav.market': 'Mercado',
                'nav.news': 'Noticias',
                'nav.settings': 'Configuración',
                'nav.login': 'Iniciar Sesión',
                'nav.logout': 'Cerrar Sesión',
                'nav.register': 'Registrarse',
                'nav.brand': 'QuantumVestAI',
                'nav.forecast': 'Pronóstico',
                'nav.profile': 'Perfil',

                // Dashboard
                'dashboard.title': 'Panel de QuantumVestAI',
                'dashboard.welcome': 'Bienvenido a QuantumVestAI',
                'dashboard.portfolio_value': 'Valor de la Cartera',
                'dashboard.daily_change': 'Cambio Diario',
                'dashboard.total_return': 'Rendimiento Total',
                'dashboard.market_cap': 'Capitalización de Mercado',
                'dashboard.volume': 'Volumen',
                'dashboard.live_data': 'Datos en Vivo',
                'dashboard.last_updated': 'Última Actualización',

                // Common
                'common.loading': 'Cargando...',
                'common.error': 'Error',
                'common.success': 'Éxito',
                'common.cancel': 'Cancelar',
                'common.confirm': 'Confirmar',
                'common.save': 'Guardar',
                'common.edit': 'Editar',
                'common.delete': 'Eliminar',
                'common.search': 'Buscar',
                'common.filter': 'Filtrar',
                'common.sort': 'Ordenar',
                'common.refresh': 'Actualizar',

                // Authentication
                'auth.login': 'Iniciar Sesión',
                'auth.register': 'Registrarse',
                'auth.email': 'Correo Electrónico',
                'auth.password': 'Contraseña',
                'auth.confirm_password': 'Confirmar Contraseña',
                'auth.forgot_password': '¿Olvidaste tu contraseña?',
                'auth.remember_me': 'Recordarme',
                'auth.sign_in': 'Entrar',
                'auth.sign_up': 'Registrarse',
                'auth.logout': 'Cerrar Sesión'
            },

            fr: {
                // Navigation
                'nav.dashboard': 'Tableau de Bord',
                'nav.portfolio': 'Portefeuille',
                'nav.analytics': 'Analyses',
                'nav.market': 'Marché',
                'nav.news': 'Actualités',
                'nav.settings': 'Paramètres',
                'nav.login': 'Connexion',
                'nav.logout': 'Déconnexion',
                'nav.register': 'Inscription',
                'nav.brand': 'QuantumVestAI',
                'nav.forecast': 'Prévisions',
                'nav.profile': 'Profil',

                // Dashboard
                'dashboard.title': 'Tableau de Bord QuantumVestAI',
                'dashboard.welcome': 'Bienvenue sur QuantumVestAI',
                'dashboard.portfolio_value': 'Valeur du Portefeuille',
                'dashboard.daily_change': 'Variation Quotidienne',
                'dashboard.total_return': 'Rendement Total',
                'dashboard.market_cap': 'Capitalisation Boursière',
                'dashboard.volume': 'Volume',
                'dashboard.live_data': 'Données en Temps Réel',
                'dashboard.last_updated': 'Dernière Mise à Jour'
            },

            de: {
                // Navigation
                'nav.dashboard': 'Dashboard',
                'nav.portfolio': 'Portfolio',
                'nav.analytics': 'Analysen',
                'nav.market': 'Markt',
                'nav.news': 'Nachrichten',
                'nav.settings': 'Einstellungen',
                'nav.login': 'Anmelden',
                'nav.logout': 'Abmelden',
                'nav.register': 'Registrieren',
                'nav.brand': 'QuantumVestAI',
                'nav.forecast': 'Prognose',
                'nav.profile': 'Profil',

                // Dashboard
                'dashboard.title': 'QuantumVestAI Dashboard',
                'dashboard.welcome': 'Willkommen bei QuantumVestAI',
                'dashboard.portfolio_value': 'Portfolio-Wert',
                'dashboard.daily_change': 'Tägliche Änderung',
                'dashboard.total_return': 'Gesamtrendite',
                'dashboard.market_cap': 'Marktkapitalisierung',
                'dashboard.volume': 'Volumen',
                'dashboard.live_data': 'Live-Daten',
                'dashboard.last_updated': 'Zuletzt Aktualisiert'
            },

            zh: {
                // Navigation
                'nav.dashboard': '仪表板',
                'nav.portfolio': '投资组合',
                'nav.analytics': '分析',
                'nav.market': '市场',
                'nav.news': '新闻',
                'nav.settings': '设置',
                'nav.login': '登录',
                'nav.logout': '退出',
                'nav.register': '注册',
                'nav.brand': 'QuantumVestAI',
                'nav.forecast': '预测',
                'nav.profile': '个人资料',

                // Dashboard
                'dashboard.title': 'QuantumVestAI 仪表板',
                'dashboard.welcome': '欢迎使用 QuantumVestAI',
                'dashboard.portfolio_value': '投资组合价值',
                'dashboard.daily_change': '日变化',
                'dashboard.total_return': '总回报',
                'dashboard.market_cap': '市值',
                'dashboard.volume': '成交量',
                'dashboard.live_data': '实时数据',
                'dashboard.last_updated': '最后更新'
            }
        };
    }

    setupLanguageSelector() {
        const existingSelector = document.querySelector('.quantum-language-selector');
        if (existingSelector) return;

        const selector = document.createElement('div');
        selector.className = 'quantum-language-selector';
        selector.innerHTML = `
            <button class="quantum-language-button quantum-btn quantum-btn-secondary" aria-label="Select Language">
                <span class="language-flag">${this.supportedLanguages[this.currentLanguage].flag}</span>
                <span class="language-code">${this.currentLanguage.toUpperCase()}</span>
                <span class="language-arrow">▼</span>
            </button>
            <div class="quantum-language-dropdown">
                ${Object.entries(this.supportedLanguages).map(([code, lang]) => `
                    <button class="quantum-language-option ${code === this.currentLanguage ? 'active' : ''}" 
                            data-language="${code}">
                        <span class="language-flag">${lang.flag}</span>
                        <span class="language-name">${lang.name}</span>
                    </button>
                `).join('')}
            </div>
        `;

        // Add styles
        this.addLanguageSelectorStyles();

        // Add to navigation
        const nav = document.querySelector('.quantum-nav-container, .navbar');
        if (nav) {
            nav.appendChild(selector);
        } else {
            // Fallback: add to body
            selector.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            `;
            document.body.appendChild(selector);
        }

        this.setupLanguageSelectorEvents(selector);
    }

    addLanguageSelectorStyles() {
        const style = document.createElement('style');
        style.id = 'quantum-language-styles';
        style.textContent = `
            .quantum-language-selector {
                position: relative;
                display: inline-block;
            }

            .quantum-language-button {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                background: var(--glass-bg, rgba(255, 255, 255, 0.1));
                backdrop-filter: blur(10px);
                border-radius: 8px;
                color: white;
                cursor: pointer;
                transition: var(--transition-smooth, all 0.2s ease);
                min-width: 80px;
            }

            .quantum-language-button:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-2px);
            }

            .quantum-language-dropdown {
                position: absolute;
                top: 100%;
                right: 0;
                background: var(--glass-bg, rgba(0, 0, 0, 0.9));
                backdrop-filter: blur(15px);
                border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.2));
                border-radius: 12px;
                padding: 8px;
                min-width: 200px;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-10px);
                transition: var(--transition-smooth, all 0.3s ease);
                z-index: 1000;
                box-shadow: var(--quantum-shadow-medium, 0 12px 40px rgba(0, 0, 0, 0.3));
            }

            .quantum-language-selector.open .quantum-language-dropdown {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }

            .quantum-language-option {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                border: none;
                background: transparent;
                color: white;
                cursor: pointer;
                border-radius: 8px;
                transition: var(--transition-smooth, all 0.2s ease);
                width: 100%;
                text-align: left;
            }

            .quantum-language-option:hover {
                background: rgba(255, 255, 255, 0.1);
            }

            .quantum-language-option.active {
                background: var(--quantum-accent, linear-gradient(135deg, #4facfe 0%, #00f2fe 100%));
                color: white;
            }

            .language-flag {
                font-size: 18px;
                width: 24px;
                text-align: center;
            }

            .language-name {
                font-weight: 500;
            }

            .language-code {
                font-weight: 600;
                font-size: 12px;
            }

            .language-arrow {
                margin-left: auto;
                font-size: 10px;
                transition: transform 0.3s ease;
            }

            .quantum-language-selector.open .language-arrow {
                transform: rotate(180deg);
            }

            @media (max-width: 768px) {
                .quantum-language-dropdown {
                    right: auto;
                    left: 0;
                    min-width: 180px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    setupLanguageSelectorEvents(selector) {
        const button = selector.querySelector('.quantum-language-button');
        const dropdown = selector.querySelector('.quantum-language-dropdown');
        const options = selector.querySelectorAll('.quantum-language-option');

        button.addEventListener('click', (e) => {
            e.stopPropagation();
            selector.classList.toggle('open');
        });

        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const languageCode = option.dataset.language;
                this.changeLanguage(languageCode);
                selector.classList.remove('open');
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            selector.classList.remove('open');
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                selector.classList.remove('open');
            }
        });
    }

    async changeLanguage(languageCode) {
        if (!this.supportedLanguages[languageCode]) return;

        this.currentLanguage = languageCode;
        localStorage.setItem('quantum-language', languageCode);
        
        await this.applyLanguage(languageCode);
        this.translatePage();
        this.updateLanguageSelector();
        
        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: languageCode } 
        }));
    }

    async applyLanguage(languageCode) {
        const lang = this.supportedLanguages[languageCode];
        
        // Set document language
        document.documentElement.lang = languageCode;
        
        // Set RTL direction if needed
        document.documentElement.dir = lang.rtl ? 'rtl' : 'ltr';
        
        // Add language-specific classes
        document.documentElement.className = document.documentElement.className
            .replace(/lang-\w+/g, '') + ` lang-${languageCode}`;
        
        // Update page title if translation exists
        const titleKey = 'page.title';
        if (this.translations[languageCode] && this.translations[languageCode][titleKey]) {
            document.title = this.translations[languageCode][titleKey];
        }
    }

    translatePage() {
        // Find all elements with data-i18n attribute
        const elements = document.querySelectorAll('[data-i18n]');
        
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.translate(key);
            
            if (translation) {
                // Handle different content types
                if (element.tagName === 'INPUT' && element.type === 'submit') {
                    element.value = translation;
                } else if (element.tagName === 'INPUT' && element.placeholder !== undefined) {
                    element.placeholder = translation;
                } else if (element.getAttribute('aria-label')) {
                    element.setAttribute('aria-label', translation);
                } else {
                    element.textContent = translation;
                }
            }
        });

        // Auto-translate common elements if they don't have data-i18n
        this.autoTranslateCommonElements();
    }

    autoTranslateCommonElements() {
        // Auto-translate navigation items
        const navItems = document.querySelectorAll('nav a, .nav-link');
        navItems.forEach(item => {
            if (!item.hasAttribute('data-i18n')) {
                const text = item.textContent.trim().toLowerCase();
                const key = `nav.${text}`;
                const translation = this.translate(key);
                if (translation && translation !== key) {
                    item.textContent = translation;
                }
            }
        });

        // Auto-translate buttons
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            if (!button.hasAttribute('data-i18n') && button.textContent.trim()) {
                const text = button.textContent.trim().toLowerCase().replace(/\s+/g, '_');
                const key = `common.${text}`;
                const translation = this.translate(key);
                if (translation && translation !== key) {
                    button.textContent = translation;
                }
            }
        });
    }

    translate(key, params = {}) {
        const translations = this.translations[this.currentLanguage] || this.translations['en'];
        let translation = translations[key] || key;
        
        // Replace parameters in translation
        Object.keys(params).forEach(param => {
            translation = translation.replace(`{${param}}`, params[param]);
        });
        
        return translation;
    }

    updateLanguageSelector() {
        const button = document.querySelector('.quantum-language-button');
        const options = document.querySelectorAll('.quantum-language-option');
        
        if (button) {
            const flag = button.querySelector('.language-flag');
            const code = button.querySelector('.language-code');
            
            if (flag) flag.textContent = this.supportedLanguages[this.currentLanguage].flag;
            if (code) code.textContent = this.currentLanguage.toUpperCase();
        }
        
        options.forEach(option => {
            option.classList.toggle('active', option.dataset.language === this.currentLanguage);
        });
    }

    // Format numbers according to locale
    formatNumber(number, options = {}) {
        const locales = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'ar': 'ar-SA',
            'hi': 'hi-IN',
            'pt': 'pt-BR',
            'ru': 'ru-RU',
            'it': 'it-IT'
        };
        
        const locale = locales[this.currentLanguage] || 'en-US';
        return new Intl.NumberFormat(locale, options).format(number);
    }

    // Format currency according to locale
    formatCurrency(amount, currency = 'USD') {
        return this.formatNumber(amount, {
            style: 'currency',
            currency: currency
        });
    }

    // Format dates according to locale
    formatDate(date, options = {}) {
        const locales = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'ar': 'ar-SA',
            'hi': 'hi-IN',
            'pt': 'pt-BR',
            'ru': 'ru-RU',
            'it': 'it-IT'
        };
        
        const locale = locales[this.currentLanguage] || 'en-US';
        return new Intl.DateTimeFormat(locale, options).format(new Date(date));
    }

    // Get current language
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Get supported languages
    getSupportedLanguages() {
        return this.supportedLanguages;
    }

    // Add translation at runtime
    addTranslation(languageCode, key, value) {
        if (!this.translations[languageCode]) {
            this.translations[languageCode] = {};
        }
        this.translations[languageCode][key] = value;
    }
}

// Initialize i18n system
const quantumI18n = new QuantumI18n();

// Ensure translation runs after the DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => quantumI18n.translatePage());
} else {
    quantumI18n.translatePage();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumI18n;}