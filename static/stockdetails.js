document.addEventListener('DOMContentLoaded', () => {
    const timeSeriesData = JSON.parse(document.getElementById('timeSeriesData').textContent);
    const labels = Object.keys(timeSeriesData).reverse().slice(0, 30); // Get the last 30 days of data for chart
    const closingPrices = labels.map(date => parseFloat(timeSeriesData[date]['4. close']));

    const ctx = document.getElementById('stockChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: document.getElementById('stockName').textContent + ' Closing Price',
                data: closingPrices,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Stock Price Over Time'
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
});