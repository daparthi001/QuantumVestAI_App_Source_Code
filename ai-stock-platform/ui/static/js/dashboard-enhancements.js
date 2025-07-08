/**
 * Dashboard Enhancements - Interactive Features
 * Adds modern UI interactions and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Chart period selection
    const chartControls = document.querySelector('.chart-controls');
    if (chartControls) {
        chartControls.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn') && e.target.dataset.period) {
                // Remove active class from all buttons
                chartControls.querySelectorAll('.btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Add active class to clicked button
                e.target.classList.add('active');
                
                // Simulate chart update
                updateChart(e.target.dataset.period);
            }
        });
    }
    
    // Add hover animations to metric cards
    const metricCards = document.querySelectorAll('.quantum-card');
    metricCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
    
    // Animate confidence bars on page load
    setTimeout(() => {
        const confidenceBars = document.querySelectorAll('.confidence-fill');
        confidenceBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            bar.style.transition = 'width 1s ease-out';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }, 500);
    
    // Add ripple effect to action buttons
    const actionButtons = document.querySelectorAll('.quantum-action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Auto-refresh dashboard data
    setInterval(() => {
        updateDashboardData();
    }, 60000); // Update every minute
    
    // Add loading states
    const refreshButton = document.getElementById('refresh-data');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refreshing...';
            this.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
                this.disabled = false;
                showNotification('Dashboard data refreshed!', 'success');
            }, 2000);
        });
    }
});

function updateChart(period) {
    const chartContainer = document.getElementById('portfolio-chart');
    if (!chartContainer) return;
    
    // Add loading state
    chartContainer.classList.add('loading-pulse');
    
    // Simulate chart update
    setTimeout(() => {
        chartContainer.classList.remove('loading-pulse');
        console.log(`Chart updated for period: ${period}`);
        showNotification(`Chart updated for ${period} period`, 'info');
    }, 1000);
}

function updateDashboardData() {
    // Simulate real-time data updates
    const priceDisplays = document.querySelectorAll('.price-display');
    priceDisplays.forEach(display => {
        // Add subtle animation to indicate data refresh
        display.style.opacity = '0.7';
        setTimeout(() => {
            display.style.opacity = '1';
        }, 200);
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    notification.innerHTML = `
        <i class="bi bi-info-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" aria-label="Close"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Add close functionality
    const closeBtn = notification.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 5000);
}

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        background-color: rgba(255, 255, 255, 0.7);
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .notification-toast {
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
`;
document.head.appendChild(style);

// Add performance monitoring
const performanceMonitor = {
    start: Date.now(),
    
    logPageLoad() {
        const loadTime = Date.now() - this.start;
        console.log(`Dashboard loaded in ${loadTime}ms`);
        
        // Show performance indicator for development
        if (loadTime > 3000) {
            console.warn('Dashboard loading slowly. Consider optimizing resources.');
        }
    }
};

// Monitor page load performance
window.addEventListener('load', () => {
    performanceMonitor.logPageLoad();
});