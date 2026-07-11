/**
 * auth.js — Global session & localStorage guard
 * Include this as a regular <script> (NOT module) on every authenticated page.
 * It patches fetch() globally so any 401 response auto-logs out the user.
 */

// ── DataLab localStorage keys ──
const DL_KEYS = ['active_id', 'active_name', 'active_ts'];

/**
 * Clears DataLab session data and redirects to landing/home.
 * Called on logout OR when a 401 is detected.
 */
function doLogout() {
    DL_KEYS.forEach(k => localStorage.removeItem(k));
    window.location.href = '/';
}

/**
 * Intercept all fetch() calls. If any returns 401, auto-logout.
 * This ensures that token expiry on ANY page clears localStorage
 * and bounces the user to the landing page.
 */
(function patchFetch() {
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        const response = await originalFetch.apply(this, args);
        if (response.status === 401) {
            // Clone so callers can still read the body if needed
            const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
            // Don't intercept the logout call itself to avoid loops
            if (!url.includes('/auth/logout') && !url.includes('/auth/login')) {
                console.warn('[DataLab] 401 detected — session expired. Redirecting to landing.');
                doLogout();
            }
        }
        return response;
    };
})();

/**
 * On page load: if an active_id is stored, verify it's still valid
 * by checking session age. If older than 8 hours, wipe it.
 */
(function checkStaleSession() {
    const ts = localStorage.getItem('active_ts');
    if (ts) {
        const age = Date.now() - parseInt(ts, 10);
        const EIGHT_HOURS = 8 * 60 * 60 * 1000;
        if (age > EIGHT_HOURS) {
            console.info('[DataLab] Stale active_id detected (>8h). Clearing.');
            DL_KEYS.forEach(k => localStorage.removeItem(k));
        }
    }
})();
