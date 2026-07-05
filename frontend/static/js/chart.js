document.addEventListener("DOMContentLoaded", async () => {
    const selectedDatasetId = localStorage.getItem('active_id');
    const selectedDatasetName = localStorage.getItem('active_name');
    
    const errorBlock = document.querySelector("#error");
    const formElement = document.querySelector("#visual-form");
    if (!selectedDatasetId) {
        if (errorBlock) {
            errorBlock.style.display = "block";
            errorBlock.textContent = "⚠️ Missing Workspace Context: Please select a dataset from the sidebar panel first.";
        }
        const generateBtn = document.querySelector("#generateBtn");
        if (generateBtn) generateBtn.disabled = true;
        return;
    }
    else{
        try{
            const response = await fetch(`/datasets/columns?dataset_id=${selectedDatasetId}`,{
            method:"GET",
            });
            if (response.ok) {
                const data = await response.json();
                const xAxisSelect = document.querySelector("#xAxisCol");
                const yAxisSelect = document.querySelector("#yAxisCol");
                const generateBtn = document.querySelector("#generateBtn");

                populateDropdownMenu(xAxisSelect, data.columns, false);
                populateDropdownMenu(yAxisSelect, data.columns, true);
                generateBtn.disabled = false;
            }
            else{
                alert("Error Occured")
            }
        }
        catch{
            alert("Server Error")
        }
    }
    if (errorBlock) errorBlock.style.display = "none";
});

function populateDropdownMenu(selectElement, columnsArray, allowOptionalNone) {
    if (!selectElement) return;
    selectElement.innerHTML = allowOptionalNone 
        ? '<option value="">-- Count Frequency (None) --</option>' 
        : '<option value="">-- Select Target Column --</option>';
        
    columnsArray.forEach(colName => {
        const option = document.createElement('option');
        option.value = colName;
        option.textContent = colName;
        selectElement.appendChild(option);
    });
}

