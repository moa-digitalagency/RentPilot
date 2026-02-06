document.addEventListener('DOMContentLoaded', () => {

    // --- NAVIGATION LOGIC ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('main > section');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');

    function switchView(viewId) {
        // Hide all sections
        sections.forEach(section => {
            section.classList.add('hidden');
        });

        // Show target section
        const targetSection = document.getElementById(`view-${viewId}`);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }

        // Update Nav Active State
        navItems.forEach(item => {
            if (item.dataset.view === viewId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Close mobile sidebar if open
        if (window.innerWidth < 1024) {
            closeSidebar();
        }
    }

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = item.dataset.view;
            if (viewId) {
                switchView(viewId);
            }
        });
    });

    // --- MOBILE SIDEBAR ---
    function openSidebar() {
        sidebar.classList.remove('-translate-x-full');
        sidebarOverlay.classList.remove('hidden');
        // Small delay to allow display:block to apply before opacity transition if needed
        setTimeout(() => sidebarOverlay.classList.remove('opacity-0'), 10);
    }

    function closeSidebar() {
        sidebar.classList.add('-translate-x-full');
        sidebarOverlay.classList.add('opacity-0');
        setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', openSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // --- TABS LOGIC (Generic) ---
    // Expects buttons with data-tab="target-id" and content divs with id="target-id"
    // Also expects buttons to have a specific class to group them, e.g. "tab-btn" or "tab-btn-maint"

    function setupTabs(btnSelector) {
        const buttons = document.querySelectorAll(btnSelector);

        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.dataset.tab;
                const container = btn.parentElement.parentElement.parentElement; // Crude way to find container scope if needed, but IDs are unique so:

                // Find all siblings/related content to hide
                // We assume tab content is siblings or in the same container.
                // A safer way: find all elements controlled by this group of buttons

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
            } else {
                syndicInput.classList.add('hidden');
            }
        });
    }

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
