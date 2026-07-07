import { populateDropdownMenu } from "./chart.js";

function showError(elId, msg) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = msg; el.style.display = "block"; }
}
function hideError(elId) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = ""; el.style.display = "none"; }
}
function showSuccess(elId, msg) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = msg; el.style.display = "block"; }
}
function hideSuccess(elId) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = ""; el.style.display = "none"; }
}

async function apiFetch(url, options = {}) {
    const response = await fetch(url, { credentials: "include", ...options });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Request failed.");
    return data;
}

function showView(viewId) {
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.toggle('hidden', panel.id !== viewId);
    });
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.view === viewId);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const datasetId = localStorage.getItem('active_id');

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            showView(link.dataset.view);
        });
    });
    const overallFillNaRadio = document.getElementById('fill-na-overall');
    const overalldropNaRadio = document.getElementById('drop-na-overall');
    const fillNaRadio = document.getElementById('fill-na');
    const dropNaRadio = document.getElementById('drop-na-row-wise');
    const fillNaPanel = document.getElementById('for-fill-na');
    const customValueField = document.getElementById('custom-value-field');
    overallFillNaRadio.classList.add('hidden')
    overalldropNaRadio.classList.add('hidden')
    fillNaRadio?.addEventListener('change', () => fillNaPanel.classList.remove('hidden'));
    dropNaRadio?.addEventListener('change', () => fillNaPanel.classList.add('hidden'));

    document.querySelectorAll('input[name="fill-type"]').forEach(radio => {
        radio.addEventListener('change', () => {
            customValueField.classList.toggle('hidden', radio.value !== 'custom');
        });
    });

    
    document.querySelectorAll('input[name="scope"]').forEach(radio => {
            radio.addEventListener('change', () => {
                const value= radio.value
                if( value=="drop"){
                    overallFillNaRadio.classList.add('hidden')
                    overalldropNaRadio.classList.remove('hidden')
                }
                else{
                    overalldropNaRadio.classList.add('hidden')
                    overallFillNaRadio.classList.remove('hidden')
                }

            });
        });

    if (!datasetId) {
        showError('global-error', "No dataset selected. Go back and select a dataset first.");
        return;
    }

    await initializeClean(datasetId);
    wireUpButtons(datasetId);
});



function populateMetadataDropdown(selectElement, columnsArray, nullCountsMap, isOptional = false) {
    if (!selectElement) return;

    // Clear previous options
    selectElement.innerHTML = isOptional 
        ? '<option value="">-- Optional (None) --</option>' 
        : '<option value="">-- Select Target Column --</option>';

    columnsArray.forEach(colName => {
        const option = document.createElement('option');
        option.value = colName;

        // Extract the null count from your new backend map (fallback to 0 if undefined)
        const nullCount = nullCountsMap[colName] !== undefined ? nullCountsMap[colName] : 0;

        // Visual enhancement: Add a warning indicator if column has missing data
        if (nullCount > 0) {
            option.textContent = `${colName} (⚠️ ${nullCount} nulls)`;
            option.style.color = "#dc3545"; // Light style cue for dirty columns
        } else {
            option.textContent = `${colName} (clean)`;
            option.value = "";
        }

        selectElement.appendChild(option);
    });
}
async function initializeClean(datasetId) {
    try {
        const data = await apiFetch(`/datasets/columns?dataset_id=${datasetId}`);
        const columns = data.columns;
        const colCleanSelect=document.querySelector("#column-select")

        if (colCleanSelect) {
            populateMetadataDropdown(colCleanSelect, data.columns, data["columns-null"], false);
        }
    
        populateDropdownMenu(document.querySelector("#rename-column-select"), columns, false);
        populateDropdownMenu(document.querySelector("#categorical-columns"), columns, false);

        hideError('global-error');
    } catch (err) {
        showError('global-error', err.message);
    }
}



function wireUpButtons(datasetId) {
    document.getElementById('column-clean-btn')?.addEventListener('click', async () => {
        hideError('column-clean-error');
        hideSuccess('column-clean-success');
        const userConfirmed = confirm(
        "⚠️ Commit Changes Permanently?\n\nThis operation will directly modify your original dataset file on the server. This action cannot be undone. Do you want to proceed?"
        );

        if (!userConfirmed) {
            return; 
        }

        const column_name = document.querySelector("#column-select").value;
        if (column_name==""){
            showError('column-clean-error',"Already Clean");
            return
        }

        const cleanType = document.querySelector('input[name="clean-type"]:checked').value;

        if (!column_name) return showError('column-clean-error', "Select a column first.");
        if (!cleanType) return showError('column-clean-error', "Select fill NA or drop NA.");

        const payload={
            column_name:column_name,
            clean_type:cleanType
        }
        if (cleanType=='fill-na'){
            const fillType=document.querySelector('input[name="fill-type"]:checked').value;
            payload.fill_type = fillType
            if (fillType == 'custom'){
                const custom_fill=document.querySelector('#replace-value').value;
                payload.custom_fill_value = custom_fill
            }
        }
        try {
            const data = await apiFetch(`datasets/column-clean?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            await initializeClean(datasetId)
            showSuccess('column-clean-success', data.message || "Column cleaned successfully.");
            
        } catch (err) {
            showError('column-clean-error', err.message);
        }
    });


    document.getElementById('overall-clean-btn')?.addEventListener('click', async () => {
        hideError('overall-clean-error');
        hideSuccess('overall-clean-success');

        const dropScope = document.querySelector('input[name="drop-na-scope"]:checked')?.value;
        const fillValue = document.getElementById('global-fill-na').value.trim();

        if (!dropScope && !fillValue) {
            return showError('overall-clean-error', "Choose drop NA scope or enter a fill value.");
        }

        try {
            const data = await apiFetch(`/process/overall-clean?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ drop_scope: dropScope, fill_value: fillValue || null })
            });
            showSuccess('overall-clean-success', data.message || "Dataset cleaned.");
        } catch (err) {
            showError('overall-clean-error', err.message);
        }
    });

    // Encoding
    document.getElementById('encoding-btn')?.addEventListener('click', async () => {
        hideError('encoding-error');
        hideSuccess('encoding-success');

        const selected = [...document.querySelectorAll("#categorical-columns option:checked")].map(o => o.value);
        const strategy = document.querySelector('input[name="encoding-type"]:checked')?.value;

        if (selected.length === 0) return showError('encoding-error', "Select at least one column to encode.");

        try {
            const data = await apiFetch(`/process/encode?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ columns: selected, strategy })
            });
            showSuccess('encoding-success', data.message || "Encoding applied.");
        } catch (err) {
            showError('encoding-error', err.message);
        }
    });

    // Rename
    document.getElementById('rename-btn')?.addEventListener('click', async () => {
        hideError('rename-error');
        hideSuccess('rename-success');

        const column = document.querySelector("#rename-column-select").value;
        const newName = document.getElementById('new-column-name').value.trim();

        if (!column) return showError('rename-error', "Select a column to rename.");
        if (!newName) return showError('rename-error', "Enter a new column name.");
        if (column === newName) return showError('rename-error', "New name is the same as the current name.");

        try {
            const data = await apiFetch(`/process/rename?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ column, new_name: newName })
            });
            showSuccess('rename-success', data.message || "Column renamed.");

            
            await initializeClean(datasetId);
            document.getElementById('new-column-name').value = '';
        } catch (err) {
            showError('rename-error', err.message);
        }
    });
}