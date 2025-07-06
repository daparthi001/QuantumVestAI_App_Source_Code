/**
 * Enhanced Navigation Component
 * Created: 2025-01-09
 * Author: AI Assistant
 */

class NavigationController {
    constructor() {
        this.currentPage = window.location.pathname;
        this.init();
    }
    
    init() {
        this.setupMobileNavigation();
        this.setupActiveLinks();
        this.setupBreadcrumbs();
        this.setupUserMenu();
        this.setupThemeToggle();
    }
    
    setupMobileNavigation() {
        const mobileToggle = document.getElementById('mobileMenuToggle');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        
        if (mobileToggle && sidebar) {
            mobileToggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
                document.body.classList.toggle('sidebar-open');
            });
        }
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
            });
        }
        
        // Restore sidebar state
        const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (sidebarCollapsed && sidebar) {
            sidebar.classList.add('collapsed');
        }
        
        // Close mobile menu on outside click
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar?.contains(e.target) && !mobileToggle?.contains(e.target)) {
                    sidebar?.classList.remove('show');
                    document.body.classList.remove('sidebar-open');
                }
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                sidebar?.classList.remove('show');
                document.body.classList.remove('sidebar-open');
            }
        });
    }
    
    setupActiveLinks() {
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPath = window.location.pathname;
        
        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            
            // Remove active class from all links
            link.parentElement?.classList.remove('active');
            
            // Add active class to current page
            if (linkPath === currentPath || 
                (currentPath !== '/' && linkPath !== '/' && currentPath.startsWith(linkPath))) {
                link.parentElement?.classList.add('active');
            }
        });
    }
    
    setupBreadcrumbs() {
        const breadcrumbContainer = document.querySelector('.breadcrumb');
        if (!breadcrumbContainer) return;
        
        const pathSegments = window.location.pathname.split('/').filter(segment => segment !== '');
        const breadcrumbs = [{ name: 'Home', url: '/' }];
        
        let currentPath = '';
        pathSegments.forEach(segment => {
            currentPath += `/${segment}`;
            const name = this.formatSegmentName(segment);
            breadcrumbs.push({ name, url: currentPath });
        });
        
        // Clear existing breadcrumbs
        breadcrumbContainer.innerHTML = '';
        
        // Add breadcrumb items
        breadcrumbs.forEach((breadcrumb, index) => {
            const isLast = index === breadcrumbs.length - 1;
            const li = document.createElement('li');
            li.className = `breadcrumb-item ${isLast ? 'active' : ''}`;
            
            if (isLast) {
                li.textContent = breadcrumb.name;
                li.setAttribute('aria-current', 'page');
            } else {
                const a = document.createElement('a');
                a.href = breadcrumb.url;
                a.textContent = breadcrumb.name;
                li.appendChild(a);
            }
            
            breadcrumbContainer.appendChild(li);
        });
    }
    
    setupUserMenu() {
        const userMenuToggle = document.querySelector('[data-bs-toggle="dropdown"]');
        const logoutButtons = document.querySelectorAll('[data-action="logout"]');
        
        // Handle logout
        logoutButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                
                if (confirm('Are you sure you want to log out?')) {
                    try {
                        // Try to call logout endpoint
                        await fetch('/logout', { method: 'POST' });
                    } catch (error) {
                        console.error('Logout request failed:', error);
                    }
                    
                    // Clear local storage
                    localStorage.clear();
                    sessionStorage.clear();
                    
                    // Redirect to login
                    window.location.href = '/login?msg=Successfully logged out';
                }
            });
        });
    }
    
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;
        
        // Get saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
    
    setTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
        
        // Update theme toggle icon
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
            }
        }
    }
    
    formatSegmentName(segment) {
        // Convert URL segment to readable name
        const nameMap = {
            'dashboard': 'Dashboard',
            'stocks': 'Stocks',
            'watchlist': 'Watchlist',
            'portfolio': 'Portfolio',
            'analytics': 'Analytics',
            'settings': 'Settings',
            'profile': 'Profile',
            'forecast': 'Forecast',
            'news': 'News',
            'alerts': 'Alerts'
        };
        
        return nameMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
    }
    
    // Navigation methods
    navigateTo(url, replaceState = false) {
        if (replaceState) {
            window.history.replaceState(null, '', url);
        } else {
            window.history.pushState(null, '', url);
        }
        
        // Update active links and breadcrumbs
        this.setupActiveLinks();
        this.setupBreadcrumbs();
    }
    
    goBack() {
        window.history.back();
    }
    
    goForward() {
        window.history.forward();
    }
    
    // Add loading indicator to navigation
    showNavigationLoading() {
        const loadingIndicator = document.createElement('div');
        loadingIndicator.id = 'nav-loading';
        loadingIndicator.className = 'position-fixed top-0 start-0 w-100 bg-primary';
        loadingIndicator.style.cssText = `
            height: 3px;
            z-index: 9999;
            animation: navProgress 2s ease-in-out infinite;
        `;
        
        document.body.appendChild(loadingIndicator);
        
        // Add CSS animation
        if (!document.getElementById('nav-loading-styles')) {
            const style = document.createElement('style');
            style.id = 'nav-loading-styles';
            style.textContent = `
                @keyframes navProgress {
                    0% { width: 0%; }
                    50% { width: 70%; }
                    100% { width: 100%; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    hideNavigationLoading() {
        const loadingIndicator = document.getElementById('nav-loading');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }
    
    // Handle SPA-style navigation
    handleLinkClick(event) {
        const link = event.target.closest('a');
        if (!link) return;
        
        const href = link.getAttribute('href');
        
        // Skip external links and special protocols
        if (!href || 
            href.startsWith('http') || 
            href.startsWith('mailto:') || 
            href.startsWith('tel:') ||
            href.includes('#') ||
            link.hasAttribute('download') ||
            link.getAttribute('target') === '_blank') {
            return;
        }
        
        // Skip if it's the current page
        if (href === window.location.pathname) {
            event.preventDefault();
            return;
        }
        
        event.preventDefault();
        
        // Show loading
        this.showNavigationLoading();
        
        // Navigate
        window.location.href = href;
    }
}

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.navigation = new NavigationController();
    
    // Handle link clicks for SPA-style navigation
    document.addEventListener('click', (e) => {
        window.navigation.handleLinkClick(e);
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
        window.navigation.setupActiveLinks();
        window.navigation.setupBreadcrumbs();
    });
});

// Handle page load completion
window.addEventListener('load', function() {
    // Hide any loading indicators
    if (window.navigation) {
        window.navigation.hideNavigationLoading();
    }
});

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Alt + Home = Go to dashboard
    if (e.altKey && e.key === 'Home') {
        e.preventDefault();
        window.location.href = '/dashboard';
    }
    
    // Alt + Left = Go back
    if (e.altKey && e.key === 'ArrowLeft') {
        e.preventDefault();
        window.history.back();
    }
    
    // Alt + Right = Go forward
    if (e.altKey && e.key === 'ArrowRight') {
        e.preventDefault();
        window.history.forward();
    }
});