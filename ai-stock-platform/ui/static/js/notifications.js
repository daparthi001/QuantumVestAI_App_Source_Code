// Simple notifications dropdown handler
// Handles toggling and mark-all-read functionality

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('notificationsToggle');
    const dropdown = document.getElementById('notificationsDropdown');
    const markAllBtn = document.querySelector('.mark-all-read-btn');
    const badge = document.querySelector('.notification-badge');

    if (toggle && dropdown) {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && !toggle.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    }

    if (markAllBtn && dropdown) {
        markAllBtn.addEventListener('click', () => {
            dropdown.querySelectorAll('.notification-card.unread')
                .forEach(card => card.classList.remove('unread'));
            if (badge) {
                badge.textContent = '0';
                badge.style.display = 'none';
            }
        });
    }

    dropdown?.querySelectorAll('.notification-dismiss').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.notification-card')?.remove();
        });
    });
});
