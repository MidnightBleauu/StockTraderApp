document.addEventListener("DOMContentLoaded", function () {
    // Review Order Modal Elements
    const reviewOrderButton = document.getElementById("review-order");
    const modal = document.getElementById("reviewOrderModal");
    const closeModalButton = document.querySelector(".modal .close");
    const confirmOrderButton = document.getElementById("confirmOrder");

    if (reviewOrderButton && modal) {
        reviewOrderButton.addEventListener("click", function () {
            modal.style.display = "block";


            const action = document.getElementById("action").value;
            const quantity = document.getElementById("quantity").value;
            const orderType = document.getElementById("order-type").value;
            const price = document.getElementById("price").value;
            const timing = document.getElementById("timing").value;

            const orderDetails = document.getElementById("orderDetails");
            if (orderDetails) {
                orderDetails.textContent = `
                    Action: ${action}
                    Quantity: ${quantity}
                    Order Type: ${orderType}
                    Price: ${price}
                    Timing: ${timing}
                `;
            }

            const totalCostElement = document.getElementById("totalCost");
            if (totalCostElement) {
                const totalCost = (price * quantity) + 6.15; // Adding transaction and exchange fee
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
                alert("Order Confirmed!");
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