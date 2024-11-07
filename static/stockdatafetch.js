document.addEventListener("DOMContentLoaded", function () {
    const stockContainer = document.querySelector('.stock-details-container');

    if (stockContainer) {
        const stockSymbol = stockContainer.querySelector('#stockSymbol').textContent.split(': ')[1];

        if (!stockSymbol) {
            console.error('Stock symbol is undefined.');
            return;
        }


        fetch(`/stocks/${stockSymbol}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok, status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.analytics_data && data.analytics_data['ANALYTICS']) {
                    const analyticsData = data.analytics_data['ANALYTICS'];
                    const analyticsContainer = document.getElementById('analyticsDataContainer');

                    // Clears contnet
                    analyticsContainer.innerHTML = '';

                    // Display analytics
                    const title = document.createElement('h3');
                    title.textContent = "Advanced Analytics Data:";
                    analyticsContainer.appendChild(title);

                    for (const key in analyticsData) {
                        if (analyticsData.hasOwnProperty(key)) {
                            const metricItem = document.createElement('p');
                            metricItem.innerHTML = `<strong>${key}:</strong> ${JSON.stringify(analyticsData[key])}`;
                            analyticsContainer.appendChild(metricItem);
                        }
                    }
                } else {
                    console.error('No analytics data available.');
                    const analyticsContainer = document.getElementById('analyticsDataContainer');
                    analyticsContainer.innerHTML = '<p>No analytics data available for this stock.</p>';
                }
            })
            .catch(error => {
                console.error('Error fetching analytics data:', error);
                const analyticsContainer = document.getElementById('analyticsDataContainer');
                analyticsContainer.innerHTML = '<p>Error fetching analytics data.</p>';
            });
    }
});