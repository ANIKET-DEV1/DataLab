/* ── Shared logout utility — call this from anywhere ── */
function doLogout() {
  localStorage.removeItem('active_id');
  localStorage.removeItem('active_name');
  localStorage.removeItem('active_ts');
  window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadDatasets();

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
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
  }
});

async function loadDatasets() {
  try {
    const datasetsContainer = document.getElementById('datasets');
    const loadingDiv = document.getElementById('loading');

    console.log('Fetching datasets from /datasets/list...');
    
    const response = await fetch('/datasets/list', {
      method: 'GET',
      credentials: 'same-origin'
    });

    console.log('Response status:', response.status);

    if (!response.ok) {
      // 401 = session expired / token invalid → clear stale localStorage and go to landing
      if (response.status === 401) {
        localStorage.removeItem('active_id');
        localStorage.removeItem('active_name');
        localStorage.removeItem('active_ts');
        window.location.href = '/';
        return;
      }
      const errorText = await response.text();
      console.error('Server response:', errorText);
      throw new Error(`Failed to load datasets: ${response.status}`);
    }

    const data = await response.json();
    console.log('Datasets data received:', data);
    
    // Set username
    const usernameSpan = document.getElementById('username');
    if (usernameSpan) {
      usernameSpan.textContent = data.username;
    }

    // Hide loading message
    if (loadingDiv) {
      loadingDiv.style.display = 'none';
    }

    // Display datasets
    if (!data.datasets || data.datasets.length === 0) {
      console.log('No datasets found');
      datasetsContainer.innerHTML = `
        <div style="grid-column:1/-1">
          <div class="empty-state">
            <div class="empty-state-icon">📂</div>
            <h3>No datasets yet</h3>
            <p>Upload a CSV or Excel file to get started with your analysis.</p>
            <a href="/upload" class="btn btn-primary" style="margin-top:8px;">📤 Upload Dataset</a>
          </div>
        </div>`;
      return;
    }

    console.log('Found', data.datasets.length, 'datasets');

    // Create dataset cards
    
    datasetsContainer.innerHTML = data.datasets.map(dataset => `
      <div class="dataset-card animate-in" id="card-${escapeHtml(dataset.id)}">
        <h3> <i data-lucide="file-chart-column" style="width:16px;"></i> ${escapeHtml(dataset.original_name)}</h3>
        <div class="meta-row">
          <span class="meta-label">File Type</span>
          <span class="meta-value">${escapeHtml(dataset.file_type)}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Size</span>
          <span class="meta-value">${(dataset.file_size_bytes / 1024).toFixed(2)} KB</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Uploaded</span>
          <span class="meta-value">${new Date(dataset.created_at).toLocaleDateString()}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Last Accessed</span>
          <span class="meta-value">${new Date(dataset.last_accessed_at).toLocaleDateString()}</span>
        </div>
        <div class="dataset-card-actions">
          <button class="btn btn-primary btn-sm" style="flex:1;" onClick="selectbybutton('${dataset.id}','${escapeHtml(dataset.original_name)}')">
            ✓ Select
          </button>
          <button class="btn btn-danger btn-sm" onClick="del('${dataset.id}')"><i data-lucide="Trash2" style="width:16px;"></i></button>
        </div>
      </div>
    `).join('');
    if (window.lucide) {
    lucide.createIcons();
}

  } catch (error) {
    console.error('Error loading datasets:', error);
    const datasetsContainer = document.getElementById('datasets');
    const loadingDiv = document.getElementById('loading');
    
    if (loadingDiv) {
      loadingDiv.style.display = 'none';
    }
    
    datasetsContainer.innerHTML = `
      <div style="grid-column:1/-1">
        <div class="msg-error" style="justify-content:center;padding:20px;">
          ✗ Error loading datasets: ${error.message}
        </div>
      </div>`;
  }
}

async function del(id){
  if (window.confirm("Do you want to delete?")) {
    try{
        response=await fetch(`/datasets/delete?dataset_id=${id}`,{
            method:"DELETE",
          })
        const data = await response.json()
        if(!response.ok){
          alert(data.detail)
        }
        else{
          window.location.reload()
        }
    }
    catch{
      alert("We couldnt delete")
    }
  }

};

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}


let activeDatasetId = null;

function selectbybutton(newId, newName) {
    activeDatasetId = newId;
    localStorage.setItem('active_id', newId);
    localStorage.setItem('active_name', newName);
    localStorage.setItem('active_ts', Date.now().toString());

    // Visual feedback: highlight the selected card
    document.querySelectorAll('.dataset-card').forEach(c => c.style.borderColor = '');
    const card = document.getElementById(`card-${newId}`);
    if (card) {
        card.style.borderColor = 'rgba(99,137,255,0.55)';
        card.style.boxShadow = '0 0 20px rgba(99,137,255,0.2)';
    }

    // Update active badge in header
    const label = document.getElementById('active-name-label');
    const info  = document.getElementById('active-info');
    if (label) label.textContent = newName;
    if (info)  info.style.display = 'flex';

    console.log(`Active dataset set: ${newName} (id: ${newId})`);
}