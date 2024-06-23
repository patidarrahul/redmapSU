document.addEventListener("DOMContentLoaded", function () {
    const scatterChartElement = document.getElementById('scatterChart');
    if (!scatterChartElement) return;

    fetch('/api/dashboard_data/')
        .then(response => response.json())
        .then(scatterData => {
            const data = scatterData.map(item => ({
                x: item.created,
                y: item.hero_device_pce,
                user: item.author,
                url: item.url
            }));

            const users = [...new Set(data.map(d => d.user))];

            const datasets = users.map(user => {
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
            });

            const config = {
                type: 'scatter',
                data: {
                    datasets: datasets
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Power Conversion Efficiency (%)'
                            }
                        }
                    }
                }
            };

            const scatterChart = new Chart(scatterChartElement, config);

            scatterChartElement.addEventListener('click', event => {
                const points = scatterChart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
                if (points[0]) {
                    window.open(data[points[0].index].url, '_blank');
                }
            });

            function getRandomColor() {
                const letters = '0123456789ABCDEF';
                let color = '#';
                for (let i = 0; i < 6; i++) {
                    color += letters[Math.floor(Math.random() * 16)];
                }
                return color;
            }
        })
        .catch(error => console.error('Error fetching data:', error));
});
