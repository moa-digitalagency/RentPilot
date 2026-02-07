
const CACHE_NAME = 'rentpilot-pwa-v1';

// Install event
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Fetch event - Network only for now to ensure no regressions,
// but existence satisfies PWA criteria.
self.addEventListener('fetch', (event) => {
    // Optional: Add offline fallback here later
});
