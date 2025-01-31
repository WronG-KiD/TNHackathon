// Chart.js Configuration for Threats Over Time
const threatCtx = document.getElementById('threatChart').getContext('2d');
const threatChart = new Chart(threatCtx, {
    type: 'line',
    data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June'], // Example labels
        datasets: [{
            label: 'Threats Detected',
            data: [5, 10, 12, 8, 15, 20], // Example data
            borderColor: '#ff3366',
            backgroundColor: 'rgba(255, 51, 102, 0.2)',
            borderWidth: 2,
            fill: true
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    }
});

// Chart.js Configuration for Data Leak Insights
const leakCtx = document.getElementById('leakChart').getContext('2d');
const leakChart = new Chart(leakCtx, {
    type: 'bar',
    data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June'], // Example labels
        datasets: [{
            label: 'Data Leaks',
            data: [1, 3, 5, 7, 4, 6], // Example data
            backgroundColor: '#00bfae',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    }
});
