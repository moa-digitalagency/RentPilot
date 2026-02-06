document.addEventListener('DOMContentLoaded', () => {

    // --- MOBILE SIDEBAR ---
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('-translate-x-full');
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('hidden');
            setTimeout(() => sidebarOverlay.classList.remove('opacity-0'), 10);
        }
    }

    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('-translate-x-full');
        if (sidebarOverlay) {
            sidebarOverlay.classList.add('opacity-0');
            setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
        }
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', openSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // --- TABS LOGIC (Generic) ---
    // Expects buttons with data-tab="target-id" and content divs with id="target-id"
    function setupTabs(btnSelector) {
        const buttons = document.querySelectorAll(btnSelector);

        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.dataset.tab;

                // Deactivate all buttons in this group
                buttons.forEach(b => {
                    b.classList.remove('active', 'bg-white', 'shadow-sm', 'text-gray-700');
                    b.classList.add('text-gray-500', 'hover:bg-white/50');

                    // Hide content
                    const content = document.getElementById(b.dataset.tab);
                    if (content) content.classList.add('hidden');
                });

                // Activate clicked button
                btn.classList.add('active', 'bg-white', 'shadow-sm', 'text-gray-700');
                btn.classList.remove('text-gray-500', 'hover:bg-white/50');

                // Show target content
                const targetContent = document.getElementById(targetId);
                if (targetContent) targetContent.classList.remove('hidden');
            });
        });
    }

    setupTabs('.tab-btn'); // For Chat
    setupTabs('.tab-btn-maint'); // For Maintenance


    // --- CONFIGURATION FORM LOGIC ---
    const syndicCheck = document.getElementById('syndic-check');
    const syndicInput = document.getElementById('syndic-input');

    if (syndicCheck && syndicInput) {
        syndicCheck.addEventListener('change', () => {
            if (syndicCheck.checked) {
                syndicInput.classList.remove('hidden');
                syndicInput.classList.add('animate-fade-in-down');
            } else {
                syndicInput.classList.add('hidden');
            }
        });
    }

    // --- ACTIVE LINK HIGHLIGHTING ---
    // Simple logic to highlight the sidebar link that corresponds to the current page
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '#') {
            item.classList.add('active');
        } else {
             // Optional: Handle exact match or default dashboard
             // For now, let the HTML class be the default or handled here.
             // We'll leave it to the HTML to default 'dashboard' active if needed, or this script overrides.
             item.classList.remove('active');
        }
    });

});

// --- MODALS (Exposed to Window) ---
window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}
