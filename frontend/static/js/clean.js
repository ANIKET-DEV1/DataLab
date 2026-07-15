function showError(elId, msg) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = msg; el.style.display = "flex"; }
}
function hideError(elId) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = ""; el.style.display = "none"; }
}
function showSuccess(elId, msg) {
    const el = document.getElementById(elId);
    if (el) { el.textContent = msg; el.style.display = "flex"; }
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

document.addEventListener("DOMContentLoaded", async () => {
    const datasetId = localStorage.getItem('active_id');

    if (!datasetId) {
        showError('global-error', "No dataset selected. Go back and select a dataset first.");
        return;
    }

    await initializeClean(datasetId);
    wireUpButtons(datasetId);
});

function populateMetadataDropdown(selectElement, columnsArray, nullCountsMap, isOptional = false) {
    if (!selectElement) return;

    selectElement.innerHTML = isOptional
        ? '<option value="">-- Optional (None) --</option>'
        : '<option value="">-- Select Target Column --</option>';

    columnsArray.forEach(colName => {
        const option = document.createElement('option');
        const nullCount = nullCountsMap[colName] !== undefined ? nullCountsMap[colName] : 0;

        if (nullCount > 0) {
            option.value = colName;
            option.textContent = `${colName} (⚠️ ${nullCount} nulls)`;
            option.dataset.null = "true";
        } else {
            option.value = colName;
            option.textContent = `${colName} (clean)`;
        }

        selectElement.appendChild(option);
    });
}

function populateDropdownMenu(selectElement, columnsArray, isOptional = false) {
    if (!selectElement) return;

    selectElement.innerHTML = isOptional
        ? '<option value="">-- Optional (None) --</option>'
        : '<option value="">-- Select Column --</option>';

    columnsArray.forEach(colName => {
        const option = document.createElement('option');
        option.value = colName;
        option.textContent = colName;
        selectElement.appendChild(option);
    });
}

async function initializeClean(datasetId) {
    try {
        const data = await apiFetch(`/datasets/columns?dataset_id=${datasetId}`);
        const columns = data.columns;

        populateMetadataDropdown(
            document.querySelector("#column-select"),
            columns,
            data["columns-null"] || {},
            false
        );

        populateDropdownMenu(document.querySelector("#rename-column-select"), columns, false);

        hideError('global-error');
    } catch (err) {
        showError('global-error', err.message);
    }
}

function wireUpButtons(datasetId) {
    // Column clean
    document.getElementById('column-clean-btn')?.addEventListener('click', async () => {
        hideError('column-clean-error');
        hideSuccess('column-clean-success');

        const column_name = document.querySelector("#column-select").value;
        if (!column_name) return showError('column-clean-error', "Select a column first.");
        const column_type = document.querySelector("#column-select")
        if (column_type.textContent.includes('(clean)')) return showSuccess('column-clean-success','Already Cleaned')


        const cleanType = document.querySelector('input[name="clean-op"]:checked')?.value;
        if (!cleanType) return showError('column-clean-error', "Select fill NA or drop NA.");

        const payload = {
            column_name: column_name,
            clean_type: cleanType
        };

        if (cleanType === 'fill-na') {
            const fillType = document.querySelector('input[name="fill-type"]:checked')?.value;
            payload.fill_type = fillType;
            if (fillType === 'custom') {
                payload.custom_fill_value = document.querySelector('#replace-value').value;
            }
        }
        const cleanBtn= document.getElementById('column-clean-btn')
        cleanBtn.disabled=true;

        try {
            const data = await apiFetch(`datasets/column-clean?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            await initializeClean(datasetId);
            showSuccess('column-clean-success', data.message || "Column cleaned successfully.");
        } catch (err) {
            showError('column-clean-error', err.message);
        } finally {
            cleanBtn.disabled=false;
        }
    });

    // Overall clean
    document.getElementById('overall-clean-btn')?.addEventListener('click', async () => {
        hideError('overall-clean-error');
        hideSuccess('overall-clean-success');

        const type = document.querySelector('input[name="scope"]:checked')?.value;
        if (!type) return showError('overall-clean-error', "Choose drop NA scope or enter a fill value.");

        const payload = { clean_type: type };

        if (type === 'drop-na') {
            const axisValue = document.querySelector('input[name="axis"]:checked')?.value;
            if (!axisValue) return showError('overall-clean-error', "Choose drop NA axis.");
            payload.axis = axisValue === 'row' ? 0 : 1;
        } else {
            const value = document.querySelector("#global-fill-na").value;
            if (!value || value.trim().length < 1) {
                return showError('overall-clean-error', "Please provide a value to fill null values.");
            }
            payload.custom_fill_value = value;
        }
        const cleanBtn= document.getElementById('overall-clean-btn')
        cleanBtn.disabled=true;

        try {
            const data = await apiFetch(`/datasets/overall-clean?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            await initializeClean(datasetId);
            showSuccess('overall-clean-success', data.message || "Dataset cleaned.");
        } catch (err) {
            showError('overall-clean-error', err.message);
        } finally{
             cleanBtn.disabled=false;
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
        const renameBtn= document.getElementById('rename-btn')
        renameBtn.disabled=true;

        const payload = {
            old_column: column,
            new_name_columns: newName
        };

        try {

            const data = await apiFetch(`/datasets/rename-column?dataset_id=${datasetId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            showSuccess('rename-success', data.message || "Column renamed.");

            await initializeClean(datasetId);
            document.getElementById('new-column-name').value = '';
        } catch (err) {
            showError('rename-error', err.message);
        } finally{
            renameBtn.disabled=false;
        }
    });
}