// ── Shared localStorage keys ─────────────────────────────────────────────────
const DL_KEYS = ['active_id', 'active_name', 'active_ts'];

// ── Redirect helper ───────────────────────────────────────────────────────────
function doLogout() {
    DL_KEYS.forEach(k => localStorage.removeItem(k));
    window.location.href = '/';
}

// ── Logout button wiring ──────────────────────────────────────────────────────
const logoutControls = [];
const desktopLogout = document.getElementById('logoutBtn');
if (desktopLogout) logoutControls.push(desktopLogout);
document.querySelectorAll('.mob-logout-btn').forEach(el => logoutControls.push(el));

logoutControls.forEach(btn => {
    btn.addEventListener('click', async () => {
        try {
            const res = await fetch('/auth/logout', {
                method: 'POST',
                credentials: 'same-origin'
            });
            if (res.ok) {
                doLogout();
            } else {
                alert('Unable to logout right now.');
            }
        } catch (err) {
            console.error('[DataLab] Logout error:', err);
            alert('Unable to logout right now.');
        }
    });
});

// ── Global fetch interceptor (mid-session 401 guard) ─────────────────────────
// Catches any API call that returns 401 while the user is mid-session
// (e.g. token expired after page load). Skips /auth/* URLs to avoid loops.
(function patchFetch() {
    const _originalFetch = window.fetch;
    window.fetch = async function (...args) {
        const response = await _originalFetch.apply(this, args);
        if (response.status === 401) {
            const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
            const isAuthRoute = url.includes('/auth/');
            if (!isAuthRoute) {
                console.warn('[DataLab] 401 on API call — session expired, redirecting.');
                doLogout();
            }
        }
        return response;
    };
})();

// ── Stale local-session guard ─────────────────────────────────────────────────
// Clears localStorage if the selected dataset is more than 8 hours old.
(function checkStaleSession() {
    const ts = localStorage.getItem('active_ts');
    if (ts) {
        const age = Date.now() - parseInt(ts, 10);
        const EIGHT_HOURS = 8 * 60 * 60 * 1000;
        if (age > EIGHT_HOURS) {
            console.info('[DataLab] Stale active_id (>8h). Clearing.');
            DL_KEYS.forEach(k => localStorage.removeItem(k));
        }
    }
})();


async function checkAuth() {
    try {
        const res = await fetch('/auth/me', {
            method: 'GET',
            credentials: 'same-origin'
        });

        if (res.status === 401) {
            console.warn('[DataLab] Not authenticated — redirecting to /');
            DL_KEYS.forEach(k => localStorage.removeItem(k));
            window.location.href = '/';
        }
    } catch (err) {
      
        console.error('[DataLab] Auth check network error:', err);
    }
}

document.addEventListener('DOMContentLoaded', checkAuth);
