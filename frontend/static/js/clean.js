import { populateDropdownMenu } from "./chart.js";
import { showError , hideError} from "./chart.js"
document.addEventListener("DOMContentLoaded", async () => {
    const datasetId =localStorage.getItem('active_id')
    await initializeClean(datasetId);
})

const links = document.querySelectorAll('.nav-link');
const panels = document.querySelectorAll('.panel');
const fillNaOption= document.querySelector('#for-fill-na');
const selectedRadio = document.querySelector('input[id="fill-na"]');
const selectedRadiodrop = document.querySelector('input[id="drop-na-row-wise"]');
selectedRadio.addEventListener('change', (event) => {
        if (event.target.checked) {
            fillNaOption.classList.remove('hidden')
        }
});
selectedRadiodrop.addEventListener('change', (event) => {
        if (event.target.checked) {
            fillNaOption.classList.add('hidden')
        }
});


function showView(viewId) {
    panels.forEach(panel => {
        panel.classList.toggle('hidden', panel.id !== viewId);
    });
    links.forEach(link => {
        link.classList.toggle('active', link.dataset.view === viewId);
    });
}

links.forEach(link => {
    link.addEventListener('click', event => {
        event.preventDefault();
        showView(link.dataset.view);
    });
});

async function initializeClean(datasetId){
        if (!datasetId) {
            showError("No dataset selected. Please select a dataset from the sidebar first.");
            return;
        }
        try {
            const response = await fetch(`/datasets/columns?dataset_id=${datasetId}`, {
                method: "GET",
                credentials: "include", 
            });
    
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                showError(err.detail || "Failed to load columns. Try refreshing.");
                return;
            }
    
            const data = await response.json();
            const columns=document.querySelectorAll("#column-select")
            columns.forEach(cols =>
                populateDropdownMenu(cols,data.columns,False)
            )
            hideError();
    
        } catch {
            showError("Could not reach the server. Check your connection.");
        }


}