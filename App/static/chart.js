// Helper function to generate a random color for chart datasets
function getRandomColor() {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, 0.6)`;
}

// === Monthly Trends Chart (Line Chart) ===
// Endpoint: /charts/api/monthly_trends
// Canvas ID: Monthlytrends
fetch('/charts/api/monthly_trends')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('Monthlytrends').getContext('2d');
    const backgroundColors = data.labels.map(() => getRandomColor());
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Monthly trends',
                data: data.data,
                backgroundColor: backgroundColors,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true
        }
    });
});

// === Transaction Distribution Chart (Pie Chart) ===
// Endpoint: /charts/api/transaction_distribution
// Canvas ID: Tra
fetch('/charts/api/transaction_distribution')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('Tra').getContext('2d');
    const backgroundColors = data.labels.map(() => getRandomColor());
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Transaction Distribution',
                data: data.data,
                backgroundColor: backgroundColors,
            }]
        },
        options: {
            responsive: true,
        }
    });
});

// === Transaction Volume by Type Chart (Bar Chart) ===
// Endpoint: /charts/api/volume_type (Corrected from previous version)
// Canvas ID: Totaltransactionvolumebytype
fetch('/charts/api/volume_type')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('Totaltransactionvolumebytype').getContext('2d');
    const backgroundColors = data.labels.map(() => getRandomColor());
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Transaction Volume by Type',
                data: data.data,
                backgroundColor: backgroundColors,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Type',
                        color: 'blue',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of transactions',
                        color: 'blue',
                        font: { size: 14, weight: 'bold' }
                    }
                }
            }
        }
    });
});

// === Transaction Amount by Type Chart (Bar Chart) ===
// Endpoint: /charts/api/amount_type (Corrected from previous version)
// Canvas ID: TransactionAmountbyType
fetch('/charts/api/amount_type')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('TransactionAmountbyType').getContext('2d');
    const backgroundColors = data.labels.map(() => getRandomColor());
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Transaction Amount by Type',
                data: data.data,
                backgroundColor: backgroundColors,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Type',
                        color: 'blue',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Amount',
                        color: 'blue',
                        font: { size: 14, weight: 'bold' }
                    }
                }
            }
        }
    });
});

// === Average Transaction Amount Chart (Bar Chart) ===
// Endpoint: /charts/api/transaction_amount
// Canvas ID: AverageTransactionAmount
fetch('/charts/api/transaction_amount')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('AverageTransactionAmount').getContext('2d');
    const backgroundColors = data.labels.map(() => getRandomColor());
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Transaction Amount',
                data: data.data,
                backgroundColor: backgroundColors,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y', // Renders the bar chart horizontally
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Average amount',
                        color: 'blue',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Type',
                        color: 'blue',
                        font: { size: 14, weight: 'bold' }
                    }
                }
            }
        }
    });
});