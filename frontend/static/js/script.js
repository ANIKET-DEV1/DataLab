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
      datasetsContainer.innerHTML = '<div class="empty-message">No datasets yet. <a href="/upload">Upload one</a></div>';
      return;
    }

    console.log('Found', data.datasets.length, 'datasets');

    // Create dataset cards
    datasetsContainer.innerHTML = data.datasets.map(dataset => `
      <div class="dataset-card">
        <h3>${escapeHtml(dataset.original_name)}</h3>
        <p><strong>File Type:</strong> ${escapeHtml(dataset.file_type)}</p>
        <p><strong>Uploaded:</strong> ${new Date(dataset.created_at).toLocaleDateString()}</p>
        <p><strong>Size:</strong> ${(dataset.file_size_bytes / 1024).toFixed(2)} KB</p>
        <p><strong>Last Accessed:</strong> ${new Date(dataset.last_accessed_at).toLocaleDateString()}</p>
        <button value="delete" class="del" onClick="del('${dataset.id}')">Delete</button>
        <button value="Select" class="Data-select" onClick="selectbybutton('${dataset.id}')">Select<button>
      </div>
    `).join('');

  } catch (error) {
    console.error('Error loading datasets:', error);
    const datasetsContainer = document.getElementById('datasets');
    const loadingDiv = document.getElementById('loading');
    
    if (loadingDiv) {
      loadingDiv.style.display = 'none';
    }
    
    datasetsContainer.innerHTML = '<div class="empty-message" style="color: red;">Error loading datasets: ' + error.message + '</div>';
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
  } else {
     alert("Glad you're staying!");
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

// Here The preview--<

async function selectbybutton(id) {
      window.location.href = `/preview?dataset_id=${id}`;
}
