/**
 * QuantumVestAI Enhanced UI Interactions
 * Modern animations and accessibility features
 * Updated: 2025-01-09
 * Author: AI Enhancement System
 */

class QuantumUIEnhancer {
    constructor() {
        this.init();
        this.setupIntersectionObserver();
        this.setupNavigationEnhancements();
        this.setupAccessibilityFeatures();
        this.setupPerformanceOptimizations();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.enhanceUI());
        } else {
            this.enhanceUI();
        }
    }

    enhanceUI() {
        this.addQuantumClasses();
        this.setupSmoothScrolling();
        this.setupFormEnhancements();
        this.setupTooltips();
        this.setupParallaxEffects();
        this.setupThemeToggle();
    }

    addQuantumClasses() {
        // Add quantum classes to existing elements
        const cards = document.querySelectorAll('.card, .feature-card, .stats-card');
        cards.forEach(card => {
            if (!card.classList.contains('quantum-card')) {
                card.classList.add('quantum-card', 'quantum-animate-fade-in');
            }
        });

        const buttons = document.querySelectorAll('.btn, button');
        buttons.forEach(btn => {
            if (!btn.classList.contains('quantum-btn')) {
                btn.classList.add('quantum-btn');
                if (btn.classList.contains('btn-primary')) {
                    btn.classList.add('quantum-btn-primary');
                } else {
                    btn.classList.add('quantum-btn-secondary');
                }
            }
        });

        const navigation = document.querySelector('.navbar, nav');
        if (navigation && !navigation.classList.contains('quantum-nav')) {
            navigation.classList.add('quantum-nav');
        }
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('quantum-animate-fade-in');
                    
                    // Add staggered animation for child elements
                    const children = entry.target.querySelectorAll('.quantum-card, .quantum-btn');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.style.animation = `quantumFadeIn 0.8s ease-out ${index * 0.1}s both`;
                        }, 50);
                    });
                }
            });
        }, observerOptions);

        // Observe all cards and major sections
        document.querySelectorAll('.quantum-card, .section, .feature-section').forEach(el => {
            observer.observe(el);
        });
    }

    setupNavigationEnhancements() {
        const nav = document.querySelector('.quantum-nav');
        if (!nav) return;

        // Add scrolled class on scroll while keeping the menu fixed
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;

            if (currentScrollY > 100) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        }, { passive: true });

        // Setup mobile menu
        this.setupMobileMenu();
    }

    setupMobileMenu() {
        const hamburger = document.querySelector('.quantum-hamburger');
        const mobileMenu = document.querySelector('.quantum-mobile-menu');
        
        if (!hamburger || !mobileMenu) {
            // Create mobile menu if it doesn't exist
            this.createMobileMenu();
            return;
        }

        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
        });

        // Close menu when clicking on links
        mobileMenu.addEventListener('click', (e) => {
            if (e.target.classList.contains('quantum-mobile-menu-link')) {
                hamburger.classList.remove('active');
                mobileMenu.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    createMobileMenu() {
        const nav = document.querySelector('.quantum-nav');
        if (!nav) return;

        const container = nav.querySelector('.quantum-nav-container') || nav;
        
        // Create hamburger menu
        const hamburger = document.createElement('div');
        hamburger.className = 'quantum-hamburger';
        hamburger.innerHTML = '<span></span><span></span><span></span>';
        hamburger.setAttribute('aria-label', 'Toggle mobile menu');
        
        // Create mobile menu
        const mobileMenu = document.createElement('div');
        mobileMenu.className = 'quantum-mobile-menu';
        
        const menuList = document.createElement('ul');
        menuList.className = 'quantum-mobile-menu-list';
        
        // Copy existing nav links
        const navLinks = document.querySelectorAll('.quantum-nav-link, .nav-link');
        navLinks.forEach(link => {
            const li = document.createElement('li');
            li.className = 'quantum-mobile-menu-item';
            
            const mobileLink = link.cloneNode(true);
            mobileLink.className = 'quantum-mobile-menu-link';
            
            li.appendChild(mobileLink);
            menuList.appendChild(li);
        });
        
        mobileMenu.appendChild(menuList);
        container.appendChild(hamburger);
        document.body.appendChild(mobileMenu);
        
        this.setupMobileMenu();
    }

    setupAccessibilityFeatures() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Skip to main content link
        this.addSkipLink();

        // Enhance focus management
        this.setupFocusManagement();

        // Add ARIA labels where missing
        this.enhanceARIALabels();
    }

    addSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'sr-only skip-link';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #000;
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 10000;
            border-radius: 4px;
        `;

        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });

        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });

        document.body.insertBefore(skipLink, document.body.firstChild);

        // Ensure main content has ID
        let mainContent = document.querySelector('#main-content');
        if (!mainContent) {
            mainContent = document.querySelector('main, .main-content, .container');
            if (mainContent) {
                mainContent.id = 'main-content';
            }
        }
    }

    setupFocusManagement() {
        // Add focus styles for better visibility
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-navigation *:focus {
                outline: 3px solid var(--quantum-accent, #4facfe) !important;
                outline-offset: 2px !important;
                border-radius: 4px !important;
            }
            
            .quantum-focus-trap {
                outline: 3px solid var(--quantum-accent, #4facfe);
                outline-offset: 2px;
            }
        `;
        document.head.appendChild(style);
    }

    enhanceARIALabels() {
        // Add missing ARIA labels
        const buttons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
        buttons.forEach(btn => {
            if (!btn.textContent.trim() && !btn.querySelector('span, i')) {
                btn.setAttribute('aria-label', 'Button');
            }
        });

        // Enhance form labels
        const inputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])');
        inputs.forEach(input => {
            const label = document.querySelector(`label[for="${input.id}"]`);
            if (!label && input.placeholder) {
                input.setAttribute('aria-label', input.placeholder);
            }
        });
    }

    setupSmoothScrolling() {
        // Enhanced smooth scrolling for anchor links
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="#"]');
            if (!link) return;

            const href = link.getAttribute('href');
            if (href === '#') return;

            const target = document.querySelector(href);
            if (!target) return;

            e.preventDefault();

            const navHeight = document.querySelector('.quantum-nav')?.offsetHeight || 0;
            const targetPosition = target.offsetTop - navHeight - 20;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        });
    }

    setupFormEnhancements() {
        // Enhanced form interactions
        const formInputs = document.querySelectorAll('input, textarea, select');
        
        formInputs.forEach(input => {
            // Add floating label effect
            this.addFloatingLabel(input);
            
            // Add validation feedback
            this.addValidationFeedback(input);
            
            // Add loading states
            this.addLoadingStates(input);
        });
    }

    addFloatingLabel(input) {
        const parent = input.parentElement;
        if (!parent || parent.querySelector('.floating-label')) return;

        const label = document.querySelector(`label[for="${input.id}"]`);
        if (!label) return;

        parent.classList.add('floating-label-container');
        label.classList.add('floating-label');

        const updateLabel = () => {
            if (input.value || input === document.activeElement) {
                label.classList.add('active');
            } else {
                label.classList.remove('active');
            }
        };

        input.addEventListener('focus', updateLabel);
        input.addEventListener('blur', updateLabel);
        input.addEventListener('input', updateLabel);
        
        updateLabel();
    }

    addValidationFeedback(input) {
        if (input.type === 'email') {
            input.addEventListener('blur', () => {
                const isValid = input.validity.valid;
                input.classList.toggle('invalid', !isValid);
                input.classList.toggle('valid', isValid);
            });
        }
    }

    addLoadingStates(input) {
        if (input.closest('form')) {
            input.closest('form').addEventListener('submit', () => {
                input.classList.add('quantum-loading');
            });
        }
    }

    setupTooltips() {
        // Simple tooltip system
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(el => {
            el.addEventListener('mouseenter', (e) => this.showTooltip(e));
            el.addEventListener('mouseleave', () => this.hideTooltip());
        });
    }

    showTooltip(e) {
        const text = e.target.getAttribute('data-tooltip');
        if (!text) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'quantum-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            z-index: 10000;
            pointer-events: none;
            animation: quantumFadeIn 0.2s ease-out;
        `;

        document.body.appendChild(tooltip);

        const updatePosition = (e) => {
            tooltip.style.left = e.pageX + 10 + 'px';
            tooltip.style.top = e.pageY - tooltip.offsetHeight - 10 + 'px';
        };

        updatePosition(e);
        e.target.addEventListener('mousemove', updatePosition);
    }

    hideTooltip() {
        const tooltip = document.querySelector('.quantum-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    setupParallaxEffects() {
        // Subtle parallax for hero sections
        const parallaxElements = document.querySelectorAll('.quantum-parallax, .hero-section');
        
        if (parallaxElements.length === 0) return;

        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(el => {
                const rate = scrolled * -0.5;
                el.style.transform = `translateY(${rate}px)`;
            });
        }, { passive: true });
    }

    setupThemeToggle() {
        // Theme switching functionality
        const themeToggle = document.querySelector('.theme-toggle, #theme-toggle');
        if (!themeToggle) {
            this.createThemeToggle();
            return;
        }

        themeToggle.addEventListener('click', () => this.toggleTheme());
        this.loadTheme();
    }

    createThemeToggle() {
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle quantum-btn quantum-btn-secondary';
        toggle.innerHTML = '🌙';
        toggle.setAttribute('aria-label', 'Toggle dark/light theme');
        toggle.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            z-index: 1000;
            font-size: 20px;
        `;

        toggle.addEventListener('click', () => this.toggleTheme());
        document.body.appendChild(toggle);
        this.loadTheme();
    }

    toggleTheme() {
        const currentTheme = localStorage.getItem('quantum-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        localStorage.setItem('quantum-theme', newTheme);
        this.applyTheme(newTheme);
    }

    loadTheme() {
        const theme = localStorage.getItem('quantum-theme') || 'dark';
        this.applyTheme(theme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.innerHTML = theme === 'dark' ? '🌙' : '☀️';
        }

        // Add theme-specific styles
        this.addThemeStyles(theme);
    }

    addThemeStyles(theme) {
        const existingStyle = document.querySelector('#quantum-theme-styles');
        if (existingStyle) existingStyle.remove();

        const style = document.createElement('style');
        style.id = 'quantum-theme-styles';
        
        if (theme === 'light') {
            style.textContent = `
                :root {
                    --glass-bg: rgba(255, 255, 255, 0.8);
                    --glass-border: rgba(0, 0, 0, 0.1);
                }
                
                body {
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    color: #333;
                }
                
                .quantum-card {
                    background: rgba(255, 255, 255, 0.9);
                    color: #333;
                }
                
                .quantum-nav {
                    background: rgba(255, 255, 255, 0.9);
                }
            `;
        }
        
        document.head.appendChild(style);
    }

    setupPerformanceOptimizations() {
        // Lazy loading for images
        this.setupLazyLoading();
        
        // Debounced resize handler
        this.setupResizeHandler();
        
        // Preload critical resources
        this.preloadCriticalResources();
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }

    setupResizeHandler() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    }

    handleResize() {
        // Recalculate any size-dependent features
        const mobileMenu = document.querySelector('.quantum-mobile-menu');
        if (mobileMenu && window.innerWidth > 768) {
            mobileMenu.classList.remove('active');
            document.querySelector('.quantum-hamburger')?.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    preloadCriticalResources() {
        // Preload critical CSS
        const criticalCSS = [
            '/static/css/quantum-enhancements.css'
        ];

        criticalCSS.forEach(href => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'style';
            link.href = href;
            document.head.appendChild(link);
        });
    }
}

// Initialize the enhancer when the script loads
const quantumUIEnhancer = new QuantumUIEnhancer();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumUIEnhancer;
}