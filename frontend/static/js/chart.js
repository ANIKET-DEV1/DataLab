let activeDatasetId = null;

async function initializeVisualizerContext(datasetId) {
    activeDatasetId = datasetId;
    const selectedDatasetId = localStorage.getItem('active_id');
    
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
};

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

async function generateVisualChart(){

}

document.addEventListener("DOMContentLoaded", async () => {
    const selectedDatasetId = localStorage.getItem('active_id');
    const errorBlock = document.querySelector("#error");
    const formElement = document.querySelector("#visual-form");

    if (!selectedDatasetId) {
        if (errorBlock) {
            errorBlock.style.display = "block";
            errorBlock.textContent = "⚠️ Please select a dataset asset file from the folder view first.";
        }
        return;
    }

    if (errorBlock) errorBlock.style.display = "none";

    await initializeVisualizerContext(selectedDatasetId);

    if (formElement) {
        formElement.addEventListener('submit', async (evt) => {
            evt.preventDefault(); 
            const chart_type = document.getElementById('chartType').value
            const x_column = document.getElementById('xAxisCol').value
            const y_column = document.getElementById('yAxisCol').value
            if (x_column == "" && y_column!=""){
                x_column=y_column
                y_column=none
            }
            else if(x_column == "" && y_column==""){
                if (errorBlock) {
                errorBlock.style.display = "block";
                errorBlock.textContent = "X and Y can't be same";
                }
                return;
            }
            else{
                try{
                    const response = await fetch(`/datasets/visualize?dataset_id=${selectedDatasetId}`,{
                        method:'POST',

                        headers: {
                                'Content-Type': 'application/json' 
                            },

                            body: JSON.stringify({
                                'chart_type': chart_type,
                                'x_column': x_column,
                                'y_column': y_column || null 
                            })
                        });
                    if (!response.ok){
                        alert("Error Occured in System")
                    }
                    else{
                        const data = await response.json();
                        
                        await generateVisualChart(data); 
                    }
                }
                catch{
                    alert("Server Occured")
                }
            }
        });
    }
});
async function generateVisualChart(data){
    console.log(data)
}