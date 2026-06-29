document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('datasets');
  const logoutBtn = document.getElementById('logoutBtn');

  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        const res = await fetch('/auth/logout', {
          method: 'POST',
          credentials: 'same-origin'
        });

        if (res.ok) {
          window.location.href = '/login';
        } else {
          alert('Unable to logout right now.');
        }
      } catch (err) {
        console.error(err);
        alert('Unable to logout right now.');
      }
    });
  }

  if (!container) return;

  container.textContent = 'Loading datasets...';

  try {
    const res = await fetch('/datasets', { credentials: 'same-origin' });

    if (res.status === 401) {
      window.location.href = '/login?next=/';
      return;
    }

    if (!res.ok) {
      container.textContent = 'Failed to load datasets';
      console.error('Fetch error', res.status, await res.text());
      return;
    }

    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      container.textContent = 'No datasets available.';
      return;
    }

    const ul = document.createElement('ul');
    data.forEach(d => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${d.original_name}</strong> (${d.file_type}) - ${d.file_size_mb} MB`;
      ul.appendChild(li);
    });

    container.innerHTML = '';
    container.appendChild(ul);
  } catch (err) {
    container.textContent = 'Failed to load datasets';
    console.error(err);
  }
});