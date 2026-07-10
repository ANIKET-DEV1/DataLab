let activeDatasetId = null;
let myChartInstance = null;


export function showError(message) {
    const errorBlock = document.querySelector("#error");
    if (errorBlock) {
        errorBlock.style.display = "block";
        errorBlock.textContent = message;
    }
}

export function hideError() {
    const errorBlock = document.querySelector("#error");
    if (errorBlock) {
        errorBlock.style.display = "none";
        errorBlock.textContent = "";
    }
}

export function populateDropdownMenu(selectElement, columnsArray, allowOptionalNone) {
    if (!selectElement) return;
    selectElement.innerHTML = allowOptionalNone
        ? '<option value="">-- None (count frequency) --</option>'
        : '<option value="">-- Select X column --</option>';

    columnsArray.forEach(colName => {
        const option = document.createElement('option');
        option.value = colName;
        option.textContent = colName;
        selectElement.appendChild(option);
    });
}


async function initializeVisualizerContext(datasetId) {
    activeDatasetId = datasetId;

    if (!datasetId) {
        showError("No dataset selected. Please select a dataset from the sidebar first.");
        const generateBtn = document.querySelector("#generateBtn");
        if (generateBtn) generateBtn.disabled = true;
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

        const xAxisSelect = document.querySelector("#xAxisCol");
        const yAxisSelect = document.querySelector("#yAxisCol");
        const generateBtn = document.querySelector("#generateBtn");

        populateDropdownMenu(xAxisSelect, data.columns, false);
        populateDropdownMenu(yAxisSelect, data.columns, true);
        if (generateBtn) generateBtn.disabled = false;
        hideError();

    } catch {
        showError("Could not reach the server. Check your connection.");
    }
}


async function generateVisualChart(data) {
    const canvas = document.getElementById('myChart');
    if (!canvas) {
        console.error("Canvas #myChart not found.");
        return;
    }
    canvas.style.display = "block";

    if (myChartInstance) {
        myChartInstance.destroy();
        myChartInstance = null;
    }

    const chartType = document.querySelector("#chartType").value.toLowerCase();
    const xColumnName = document.querySelector("#xAxisCol").value;
    const yColumnName = document.querySelector("#yAxisCol").value;

    const activeChartType = (chartType === 'hist') ? 'bar' : chartType;

    const COLORS = ['#007bff','#28a745','#ffc107','#dc3545','#6f42c1','#fd7e14','#20c997','#17a2b8'];

    let chartConfig = {
        type: activeChartType,
        data: {},
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: (chartType === 'pie' || data.mode === 'multi_series')
                }
            },
            scales: {
                x: chartType === 'pie'
                    ? { display: false }
                    : { title: { display: true, text: xColumnName } },
                y: chartType === 'pie'
                    ? { display: false }
                    : {
                        title: {
                            display: true,
                            text: yColumnName ? `Mean of ${yColumnName}` : 'Frequency count'
                        },
                        beginAtZero: true
                    }
            }
        }
    };

    if (data.mode === "multi_series") {
        chartConfig.data.labels = data.labels;
        chartConfig.data.datasets = data.datasets.map((set, i) => ({
            label: set.label,
            data: set.data,
            backgroundColor: COLORS[i % COLORS.length],
            borderColor: COLORS[i % COLORS.length],
            borderWidth: 1,
        }));
        if (activeChartType === 'bar') {
            chartConfig.options.scales.x.stacked = true;
            chartConfig.options.scales.y.stacked = true;
        }

    } else if (chartType === 'scatter' || data.scatterData) {
        chartConfig.type = 'scatter';
        chartConfig.data = {
            datasets: [{
                label: `${xColumnName} vs ${yColumnName}`,
                data: data.scatterData,
                backgroundColor: '#007bff',
                pointRadius: 5,
            }]
        };

    } else {
        chartConfig.data.labels = data.labels;
        chartConfig.data.datasets = [{
            label: yColumnName ? `Average ${yColumnName}` : 'Frequency count',
            data: data.values,
            backgroundColor: chartType === 'pie' ? COLORS : '#007bff',
            borderColor: chartType === 'line' ? '#007bff' : 'transparent',
            fill: chartType === 'line' ? false : true,
            borderWidth: 1,
        }];
    }

    myChartInstance = new Chart(canvas.getContext('2d'), chartConfig);
}


document.addEventListener("DOMContentLoaded", async () => {
    const datasetId =localStorage.getItem('active_id')

    await initializeVisualizerContext(datasetId);

    const formElement = document.querySelector("#visual-form");
    if (!formElement) return;

    formElement.addEventListener('submit', async (evt) => {
        evt.preventDefault();
        hideError();
        const chartType  = document.getElementById('chartType').value;
    
        let xColumn = document.getElementById('xAxisCol').value;
        let yColumn = document.getElementById('yAxisCol').value || null;

        
        if (!xColumn && yColumn) {
            xColumn = yColumn;
            yColumn = null;
        }

        if (!xColumn) {
            showError("Please select at least an X column.");
            return;
        }

    
        if (xColumn && yColumn && xColumn === yColumn) {
            showError("X and Y columns can't be the same.");
            return;
        }

        try {
            const response = await fetch(`/datasets/visualize?dataset_id=${datasetId}`, {
                method: 'POST',
                credentials: 'include',   
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chart_type: chartType,
                    x_column: xColumn,
                    y_column: yColumn,
                }),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                showError(err.detail || "Something went wrong generating the chart.");
                return;
            }

            const data = await response.json();
            await generateVisualChart(data);

        } catch {
            showError("Server is unreachable. Please try again.");
        }
    });
});