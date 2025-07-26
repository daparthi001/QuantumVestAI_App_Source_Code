// Floating Action Button to open watchlist
class QuantumWatchlistFAB {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.createButton();
        });
    }

    createButton() {
        const btn = document.createElement('button');
        btn.className = 'quantum-fab';
        btn.title = 'Open Watchlist';
        btn.setAttribute('aria-label', 'Open Watchlist');
        btn.setAttribute('data-bs-toggle', 'tooltip');
        btn.setAttribute('data-bs-placement', 'left');
        btn.innerHTML = '⭐';
        btn.addEventListener('click', () => {
            window.location.href = '/watchlist';
        });
        document.body.appendChild(btn);
        if (window.bootstrap && window.bootstrap.Tooltip) {
            new window.bootstrap.Tooltip(btn);
        }
    }
}

new QuantumWatchlistFAB();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumWatchlistFAB;
}
