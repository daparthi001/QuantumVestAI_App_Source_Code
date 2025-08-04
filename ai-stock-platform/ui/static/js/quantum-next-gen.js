/**
 * QuantumVestAI Next-Gen UI Effects
 * Provides enhanced animations and visual effects for the modern UI
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize glass morphism effects
  initGlassMorphism();
  
  // Initialize animations for elements that come into view
  initAnimateOnScroll();
  
  // Enhanced hover effects
  initEnhancedHoverEffects();
  
  // Theme transition enhancements
  initThemeTransitions();
});

/**
 * Adds glass morphism parallax effects to elements with specific classes
 */
function initGlassMorphism() {
  const glassElements = document.querySelectorAll('.nextgen-glass, .nextgen-glass-card');
  
  document.addEventListener('mousemove', (e) => {
    const { clientX, clientY } = e;
    
    glassElements.forEach(el => {
      const rect = el.getBoundingClientRect();
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      
      // Only apply effect if mouse is within a certain range of the element
      const distance = Math.sqrt(
        Math.pow(rect.left + rect.width/2 - clientX, 2) + 
        Math.pow(rect.top + rect.height/2 - clientY, 2)
      );
      
      if (distance < 300) {
        const strength = Math.max(0, (300 - distance) / 300) * 0.03;
        el.style.setProperty('--x-offset', `${x * strength}px`);
        el.style.setProperty('--y-offset', `${y * strength}px`);
        el.style.transition = 'none';
        el.style.transform = `translate(var(--x-offset), var(--y-offset))`;
      } else {
        el.style.transition = 'transform 0.5s ease-out';
        el.style.transform = 'translate(0, 0)';
      }
    });
  });
}

/**
 * Applies subtle animations to elements as they come into view
 */
function initAnimateOnScroll() {
  // Check for IntersectionObserver API support
  if (!('IntersectionObserver' in window)) return;
  
  const animateOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };
  
  // Cards, buttons, and other elements to animate
  const animateElements = document.querySelectorAll('.nextgen-card, .nextgen-dashboard-card, .nextgen-glass-card');
  
  const animateObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('nextgen-animated');
        animateObserver.unobserve(entry.target);
      }
    });
  }, animateOptions);
  
  animateElements.forEach(el => {
    // Add initial state class
    el.classList.add('nextgen-animate-hidden');
    animateObserver.observe(el);
  });
}

/**
 * Enhances hover effects with subtle transforms and glows
 */
function initEnhancedHoverEffects() {
  const hoverElements = document.querySelectorAll('.nextgen-btn, .nextgen-card, .nextgen-dashboard-card');
  
  hoverElements.forEach(el => {
    el.addEventListener('mouseenter', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      el.style.setProperty('--hover-x', `${x}px`);
      el.style.setProperty('--hover-y', `${y}px`);
    });
  });
}

/**
 * Enhances theme transitions with smooth color changes
 */
function initThemeTransitions() {
  const themeToggle = document.getElementById('themeToggle');
  
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.add('nextgen-theme-transition');
      
      setTimeout(() => {
        document.body.classList.remove('nextgen-theme-transition');
      }, 1000);
    });
  }
}
