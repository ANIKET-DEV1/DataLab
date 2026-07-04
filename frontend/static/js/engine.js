document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const selectedDatasetId = urlParams.get('dataset_id');
    console.log(selectedDatasetId)
    try{
        const response = await fetch(`/datasets/preview?dataset_id=${selectedDatasetId}`,{
        method:"GET",
        });
        if (response.ok) {
            const data = await response.json();
            buildGenericTable(data[0].preview, "previewTableContainer");
            buildGenericTable(data[0].describe, "describeTableContainer");
            buildGenericTable(data[0].info, "infoTableContainer");
        }
        else{
            alert("Error Occured")
        }
    }
    catch{
        alert("Server Error")
    }
});

function buildGenericTable(arrayData, containerId) {
    const container = document.getElementById(containerId);
    
    if (!arrayData || arrayData.length === 0) {
        container.innerHTML = "<p>No data available for this section.</p>";
        return;
    }
    const headers = Object.keys(arrayData[0]);

    const headerHtml = headers.map(h => `<th>${escapeHtml(h)}</th>`).join('');
    const rowsHtml = arrayData.map(row => {
        const cellsHtml = headers.map(h => `<td>${escapeHtml(String(row[h] ?? ''))}</td>`).join('');
        return `<tr>${cellsHtml}</tr>`;
    }).join('');

    container.innerHTML = `
        <table class="data-table">
            <thead><tr>${headerHtml}</tr></thead>
            <tbody>${rowsHtml}</tbody>
        </table>
    `;
}
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}