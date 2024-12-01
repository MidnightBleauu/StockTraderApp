// dashboard.js

document.addEventListener("DOMContentLoaded", function() {
    const userId = sessionStorage.getItem('user_id');

    if (!userId) {
        console.error("User ID not found in session storage.");
        return;
    }

    // Fetch the user's updated portfolio data
    fetch(`http://localhost:5006/update_funds?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            // Update the dashboard HTML with the user's portfolio data
            document.getElementById("portfolioBalance").innerText = `Portfolio Balance: $${data.cash_balance}`;
            document.querySelector(".available-funds").innerText = `Available Funds: $${data.available_funds}`;
            document.querySelector(".total-value").innerText = `Cash + Investments: $${data.total_value}`;
            document.querySelector(".market-value").innerText = `Market Value: $${data.market_value}`;
            document.querySelector(".day-change").innerText = `Day Change: $${data.day_change}`;
            document.querySelector(".gains-loss").innerText = `Gains/Loss: $${data.gains_loss}`;
            document.querySelector(".account-number").innerText = `Account Number: ${data.account_number}`;
        })
        .catch(error => {
            console.error("Failed to fetch portfolio data:", error);
        });
});