document.addEventListener("DOMContentLoaded", function () {
    // Review Order Modal Elements
    const reviewOrderButton = document.getElementById("review-order");
    const modal = document.getElementById("reviewOrderModal");
    const closeModalButton = document.querySelector(".modal .close");
    const confirmOrderButton = document.getElementById("confirmOrder");

    if (reviewOrderButton && modal) {
        reviewOrderButton.addEventListener("click", function () {
            modal.style.display = "block";

            // Get form values
            const stockSymbol = document.getElementById("stock_symbol").textContent.split(":")[1].trim();  // Extract stock symbol correctly
            const action = document.getElementById("action").value;
            const quantity = parseFloat(document.getElementById("quantity").value);
            const orderType = document.getElementById("order-type").value;
            const price = parseFloat(document.getElementById("price").value);
            const timing = document.getElementById("timing").value;

            // Validate the inputs
            if (!stockSymbol || !quantity || !price || quantity <= 0 || price <= 0) {
                alert("Please enter valid quantity, price, and ensure stock symbol is available.");
                return;
            }

            // Display the order details in the modal
            const orderDetails = document.getElementById("orderDetails");
            if (orderDetails) {
                orderDetails.innerHTML = `
                    Stock: ${stockSymbol}<br>
                    Action: ${action}<br>
                    Quantity: ${quantity}<br>
                    Order Type: ${orderType}<br>
                    Price: $${price.toFixed(2)}<br>
                    Timing: ${timing}
                `;
            }

            // Calculate and display the total cost including fees
            const totalCostElement = document.getElementById("totalCost");
            if (totalCostElement) {
                const transactionFee = 4.95;
                const exchangeFee = 1.20;
                const totalFees = transactionFee + exchangeFee;
                const totalCost = (price * quantity) + totalFees; // Adding transaction and exchange fee
                totalCostElement.textContent = `$${totalCost.toFixed(2)}`;
            }
        });

        if (closeModalButton) {
            closeModalButton.onclick = function () {
                modal.style.display = "none";
            };
        }

        if (confirmOrderButton) {
            confirmOrderButton.onclick = function () {
                // Get form values again to send in the request
                const stockSymbol = document.getElementById("stock_symbol").textContent.split(":")[1].trim();  // Extract stock symbol correctly

                const action = document.getElementById("action").value;
                const quantity = parseFloat(document.getElementById("quantity").value);
                const price = parseFloat(document.getElementById("price").value);

                // Validate again to ensure all fields are filled correctly
                if (!stockSymbol || !action || !quantity || !price) {
                    alert("Please fill all the required fields.");
                    return;
                }

                // Make the POST request to execute the trade
                fetch('/execute_trade', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        stock_symbol: stockSymbol, // Send stock symbol in the request body
                        action: action,
                        quantity: quantity,
                        price: price
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Order successfully executed!');
                        // Optionally, refresh the page or update the UI
                        location.reload();
                    } else {
                        alert('Order failed: ' + data.error);
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert('Failed to execute the order. Please try again.');
                });

                modal.style.display = "none";
            };
        }

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        };
    }
});