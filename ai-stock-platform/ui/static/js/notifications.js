class NotificationsManager {
    constructor() {
        document.addEventListener('DOMContentLoaded', () => this.init());
    }

    init() {
        const toggle = document.getElementById('notificationsToggle');
        const dropdown = document.getElementById('notificationsDropdown');
        const markAll = dropdown ? dropdown.querySelector('.mark-all-read-btn') : null;

        if (toggle && dropdown) {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('active');
            });

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && e.target !== toggle) {
                    dropdown.classList.remove('active');
                }
            });
        }

        if (dropdown) {
            dropdown.addEventListener('click', (e) => {
                const dismissBtn = e.target.closest('.notification-dismiss');
                if (dismissBtn) {
                    e.preventDefault();
                    const card = dismissBtn.closest('.notification-card');
                    if (card) card.remove();
                }
            });
        }

        if (markAll && dropdown) {
            markAll.addEventListener('click', () => {
                dropdown.querySelectorAll('.notification-card').forEach(card => card.remove());
            });
        }
    }
}

new NotificationsManager();
