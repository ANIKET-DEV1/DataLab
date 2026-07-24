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
            <div class="empty-state-icon"><i data-lucide="folder" style="width:36px;"></i></div>
            <h3>No datasets yet</h3>
            <p>Upload a CSV or Excel file to get started with your analysis.</p>
            <a href="/upload" class="btn btn-primary" style="margin-top:8px;"><i data-lucide="upload" style="width:36px;"></i> Upload Dataset</a>
          </div>
        </div>`;
          if (window.lucide) {
    lucide.createIcons();
}
      return;
    }

    console.log('Found', data.datasets.length, 'datasets');

    // Create dataset cards
    
    datasetsContainer.innerHTML = data.datasets.map(dataset => `
      <div class="dataset-card animate-in" id="card-${escapeHtml(dataset.id)}">
        <h3><i data-lucide="file-chart-column" style="width:16px;"></i> ${escapeHtml(dataset.original_name)}</h3>
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
          <button class="btn btn-primary btn-sm" style="flex:1;" id="downloadBtn-${escapeHtml(dataset.id)}" onClick="downloadLargeFile('${dataset.id}')">
            <i data-lucide="download" style="width:16px;"></i>
          </button>
          <button class="btn btn-danger btn-sm" onClick="del('${dataset.id}')">
            <i data-lucide="Trash2" style="width:16px;"></i>
          </button>
        </div>

        <button class="btn btn-primary btn-sm btn-select" onClick="selectbybutton('${dataset.id}','${escapeHtml(dataset.original_name)}')">
          ✓ Select
        </button>
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
async function downloadLargeFile(datasetId) {
    const button = document.getElementById('downloadBtn');
    button.disabled = true; 

    try {
        const response = await fetch(`/datasets/download?dataset_id=${datasetId}`);
        
        if (!response.ok) throw new Error('Download failed');

      
        const reader = response.body.getReader();
        const chunks = [];
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break; 
            
            chunks.push(value);
        }

        
        const blob = new Blob(chunks, { type: 'application/octet-stream' });
        
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = "dataset.csv"; 
        document.body.appendChild(a);
        a.click();
        
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
        console.error('Download execution error:', error);
    } finally {
        button.disabled = false; 
    }
}


document.addEventListener('DOMContentLoaded', async () => {
  await loadDatasets();
});