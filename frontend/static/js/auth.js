function doLogout() {
  localStorage.removeItem('active_id');
  localStorage.removeItem('active_name');
  localStorage.removeItem('active_ts');
  window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadDatasets();

  // Attach logout handler to all logout controls (desktop + mobile)
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
