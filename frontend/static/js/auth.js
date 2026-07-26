const DL_KEYS=['active_id','active_name','active_ts']
function doLogout() {
  localStorage.removeItem('active_id');
  localStorage.removeItem('active_name');
  localStorage.removeItem('active_ts');
  window.location.href = '/';
}


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
        console.error(err);
        alert('Unable to logout right now.');
      }
    });
  });


(function patchFetch() {
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        const response = await originalFetch.apply(this, args);
        if (response.status === 401) {
            const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
            if (!url.includes('/auth/logout') && !url.includes('/auth/login')) {
                console.warn('[DataLab] 401 detected — session expired. Redirecting to landing.');
                doLogout();
            }
        }
        return response;
    };
})();


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


// ── Page-load auth guard ─────────────────────────────────────────────────────
// Runs once on every page that includes auth.js (via base.html).
// Hits GET /auth/me with the HTTP-only cookie; if the server says 401
// the user is not (or no longer) authenticated → redirect to landing page.
(function checkAuthOnLoad() {
    document.addEventListener('DOMContentLoaded', async () => {
        try {
            const res = await fetch('/auth/me', {
                method: 'GET',
                credentials: 'same-origin'
            });
            if (res.status === 401) {
                console.warn('[DataLab] Not authenticated on page load — redirecting to landing.');
                DL_KEYS.forEach(k => localStorage.removeItem(k));
                window.location.href = '/';
            }
            // 200 → authenticated, stay on page
            // any other status → don't disrupt, let the page handle it
        } catch (err) {
            // Network error — don't redirect, let the user see the page
            console.error('[DataLab] Auth check failed (network error):', err);
        }
    });
})();
