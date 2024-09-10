document.addEventListener("DOMContentLoaded", () => {
    const scatterChartElement = document.getElementById('scatterChart');
    const filterButton = document.getElementById('filterButton');

    if (!scatterChartElement || !filterButton) return;

    let scatterChart = null; // Variable to store the chart instance

    // Attach event listener for the filter button
    filterButton.addEventListener('click', fetchFilteredData);

    // Initial fetch to load data without any filters
    fetchData();

    async function fetchData(params = '') {
        try {
            const response = await fetch(`/api/dashboard_data/${params}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            renderChart(data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    function fetchFilteredData() {
        const author = document.getElementById('author').value;
        const dateFrom = document.getElementById('date_from').value;
        const dateTo = document.getElementById('date_to').value;

        const queryParams = new URLSearchParams();
        if (author) queryParams.append('author', author);
        if (dateFrom) queryParams.append('date_from', dateFrom);
        if (dateTo) queryParams.append('date_to', dateTo);

        fetchData(`?${queryParams.toString()}`);
    }

    function renderChart(scatterData) {
        if (scatterChart) {
            scatterChart.destroy(); // Destroy the existing chart instance
        }

        const data = scatterData.map(item => ({
            x: item.created,
            y: item.hero_device_pce,
            user: item.author,
            url: item.url,
            color: item.color
        }));

        const users = [...new Set(data.map(d => d.user))];
        const datasets = users.map(user => createDataset(user, data));

        const config = {
            type: 'scatter',
            data: { datasets },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'day' },
                        title: { display: true, text: 'Date' }
                    },
                    y: { title: { display: true, text: 'Power Conversion Efficiency (%)' } }
                }
            }
        };

        scatterChart = new Chart(scatterChartElement, config);

        scatterChartElement.addEventListener('click', event => {
            const points = scatterChart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
            if (points.length > 0) {
                const { index: pointIndex, datasetIndex } = points[0];
                const pointData = scatterChart.data.datasets[datasetIndex].data[pointIndex];
                window.open(pointData.url, '_blank');
            }
        });
    }

    function createDataset(user, data) {
        const userData = data.filter(d => d.user === user);
        const color = userData[0].color;
        return {
            label: user,
            data: userData,
            backgroundColor: color,
            borderColor: color,
            borderWidth: 1,
            pointRadius: 5,
            pointHoverRadius: 8,
            pointStyle: 'circle',
            hoverBackgroundColor: color,
            hoverBorderWidth: 2,
            hoverRadius: 15,
            pointHoverStyle: 'dash'
        };
    }
});

// Experiments by User

async function fetchExperimentsByUser() {
    try {
        const response = await fetch('/api/get_experiments_by_user/');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        const users = data.map(item => item.user);
        const experimentsCounts = data.map(item => item.experiments);

        plotExperimentsByUser(users, experimentsCounts);
    } catch (error) {
        console.error('Error fetching experiments by user:', error);
    }
}

function plotExperimentsByUser(users, experimentsCounts) {
    const ctx = document.getElementById('experimentsByUserChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: users,
            datasets: [{
                label: 'Experiments Done',
                data: experimentsCounts,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Call the fetch function when the page loads
window.onload = fetchExperimentsByUser;

// Cummulative Experiments Chart

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

async function plotChart() {
    const response = await fetch('/api/get_total_experiments/');
    const data = await response.json();
    const dates = data.map(item => formatDate(item.date));  // Reformat each date
    const experiments = data.map(item => item.experiments);
    const cumulative = experiments.map((sum => value => sum += value)(0));


    const ctx = document.getElementById('totalExperimentsChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Daily Experiments',
                data: experiments,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }, {
                label: 'Cumulative Experiments',
                data: cumulative,
                type: 'line',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true, // Ensures responsiveness
            maintainAspectRatio: false, // Prevents aspect ratio maintenance to fill container
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

plotChart();