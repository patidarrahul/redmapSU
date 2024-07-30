document.addEventListener("DOMContentLoaded", function () {
    const scatterChartElement = document.getElementById('scatterChart');
    const filterButton = document.getElementById('filterButton');

    let scatterChart = null; // Variable to store the chart instance

    if (!scatterChartElement || !filterButton) return;

    // Attach event listener for the filter button
    filterButton.addEventListener('click', fetchFilteredData);

    // Initial fetch to load data without any filters
    fetchData();

    function fetchData(params = '') {
        fetch(`/api/dashboard_data/${params}`)
            .then(response => response.json())
            .then(renderChart)
            .catch(error => console.error('Error fetching data:', error));
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
            url: item.url
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
            console.log(points[0].index);
            if (points.length > 0) {
                const pointIndex = points[0].index;
                const datasetIndex = points[0].datasetIndex;
                const pointData = scatterChart.data.datasets[datasetIndex].data[pointIndex];
                window.open(pointData.url, '_blank');
            }
        });
    }

    function createDataset(user, data) {
        const userData = data.filter(d => d.user === user);
        const color = getRandomColor();
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

    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }
});
