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
        btn.innerHTML = '⭐';
        btn.addEventListener('click', () => {
            window.location.href = '/watchlist';
        });
        document.body.appendChild(btn);
    }
}

new QuantumWatchlistFAB();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuantumWatchlistFAB;
}
