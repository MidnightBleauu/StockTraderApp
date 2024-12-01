document.addEventListener("DOMContentLoaded", function () {
    // Modal elements and buttons
    const modal = document.getElementById("watchlistModal");
    const addWatchlistButton = document.getElementById("addWatchlistButton");
    const closeButton = document.getElementsByClassName("close")[0];
    const addStockButton = document.getElementById("addStockToWatchlist");
    const stockTickerInput = document.getElementById("stockTickerInput");
    const currentPriceInput = document.getElementById("currentPriceInput");
    const targetPriceInput = document.getElementById("alertPrice");
    const alertSetDateInput = document.getElementById("alertSetDate");
    const alertDurationInput = document.getElementById("alertDuration");
    const suggestionBox = document.getElementById("suggestion-box");

    // Open modal when "Watchlist Stock" button is clicked
    addWatchlistButton.onclick = function () {
        modal.style.display = "block";
    };

    // Close modal when 'x' button is clicked
    closeButton.onclick = function () {
        modal.style.display = "none";
    };

    // Close modal when clicking outside of it
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    // Event listener for stock ticker input to get suggestions for watchlist modal
    stockTickerInput.addEventListener("input", async function () {
        const query = stockTickerInput.value.trim();
        if (query.length < 2) {
            suggestionBox.innerHTML = ""; // Clear suggestions if query is too short
            suggestionBox.style.display = "none";
            return;
        }

        try {
            // Fetch stock suggestions from your backend stock microservice
            const response = await fetch(`http://localhost:5001/search_api?query=${query}`);
            if (response.ok) {
                const data = await response.json();
                const matches = data.bestMatches;
                suggestionBox.innerHTML = ""; // Clear existing suggestions

                if (matches && matches.length > 0) {
                    suggestionBox.style.display = "block"; // Show suggestions box
                    matches.forEach(match => {
                        const symbol = match["1. symbol"];
                        const name = match["2. name"];

                        const suggestionItem = document.createElement("li");
                        suggestionItem.textContent = `${symbol} - ${name}`;
                        suggestionItem.classList.add("suggestion-item");

                        // Click event on suggestion to select it
                        suggestionItem.onclick = async function () {
                            stockTickerInput.value = symbol;
                            suggestionBox.innerHTML = ""; // Clear suggestions after selection
                            suggestionBox.style.display = "none"; // Hide suggestions box

                            // Fetch the current price of the selected stock
                            await fetchCurrentPrice(symbol);
                        };

                        suggestionBox.appendChild(suggestionItem);
                    });
                }
            }
        } catch (error) {
            console.error("Error fetching stock suggestions:", error);
        }
    });

    // Function to fetch the current price of the stock
    async function fetchCurrentPrice(symbol) {
        try {
            const response = await fetch(`http://localhost:5001/stock_details/${symbol}`);
            if (response.ok) {
                const data = await response.json();
                if (data.current_price) {
                    currentPriceInput.value = data.current_price;  // Display the current price in the input field
                } else {
                    currentPriceInput.value = "N/A";
                }
            } else {
                console.error("Failed to fetch current price");
            }
        } catch (error) {
            console.error("Error fetching current price:", error);
        }
    }

    // Add a new stock to the watchlist when "Add to Watchlist" is clicked
    addStockButton.onclick = async function () {
        const selectedStock = stockTickerInput.value.trim().toUpperCase();
        const targetAlertPrice = targetPriceInput.value;
        const alertSetDate = alertSetDateInput.value;
        const alertDuration = alertDurationInput.value;

        if (!selectedStock) {
            alert("Please enter a stock to add to your watchlist.");
            return;
        }

        if (!targetAlertPrice || targetAlertPrice <= 0) {
            alert("Please enter a valid target alert price.");
            return;
        }

        if (!alertSetDate) {
            alert("Please enter the alert set date.");
            return;
        }

        if (!alertDuration || alertDuration <= 0) {
            alert("Please enter a valid alert duration in days.");
            return;
        }

        // Send POST request to the microservice to add the stock
        try {
            const response = await fetch(`http://localhost:6465/stocks/${selectedStock}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    target_price: targetAlertPrice
                })
            });

            if (response.ok) {
                // Store additional data in local storage
                const stockData = {
                    symbol: selectedStock,
                    target_price: targetAlertPrice,
                    alert_set_date: alertSetDate,
                    alert_duration: alertDuration
                };
                localStorage.setItem(`stock_${selectedStock}`, JSON.stringify(stockData));

                alert(`Successfully added ${selectedStock} to the watchlist with target price of $${targetAlertPrice}.`);
                await updateWatchlist();
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            console.error("Error adding stock to watchlist:", error);
            alert("Failed to add stock to watchlist. Please try again later.");
        }

        // Close the modal
        modal.style.display = "none";
    };

    // Function to update the watchlist in the UI
    async function updateWatchlist() {
        try {
            const response = await fetch("http://localhost:6465/stocks", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const stocks = await response.json();
                const watchlist = document.querySelector('.stock-watch-list ul');
                watchlist.innerHTML = ""; // Clear the current watchlist

                if (stocks.length > 0) {
                    // Populate watchlist
                    stocks.forEach(stock => {
                        const storedData = JSON.parse(localStorage.getItem(`stock_${stock.symbol}`)) || {};
                        const newStockItem = document.createElement('li');
                        newStockItem.innerHTML = `
                            ${stock.symbol} | Current Price: $${stock.curr_price || '---'} | 
                            Target Price: $${storedData.target_price || '---'} | 
                            Date Set: ${storedData.alert_set_date || '--/--/--'} | 
                            Duration: ${storedData.alert_duration || '--'} days 
                            <button class="remove-button">Remove</button>
                        `;

                        // Add click event to the "Remove" button to remove the item
                        newStockItem.querySelector('.remove-button').onclick = async function () {
                            await removeStockFromWatchlist(stock.symbol);
                        };

                        watchlist.appendChild(newStockItem);
                    });
                } else {
                    // If no stocks are in the watchlist, display a message
                    const noStocksMessage = document.createElement('li');
                    noStocksMessage.textContent = "No stocks in your watchlist.";
                    watchlist.appendChild(noStocksMessage);
                }
            } else {
                console.error("Failed to update watchlist");
            }
        } catch (error) {
            console.error("Error fetching watchlist:", error);
        }
    }

    // Function to remove a stock from the watchlist
    async function removeStockFromWatchlist(stockSymbol) {
        try {
            const response = await fetch(`http://localhost:6465/stocks/${stockSymbol}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Remove the stock data from local storage
                localStorage.removeItem(`stock_${stockSymbol}`);
                alert(`Successfully removed ${stockSymbol} from the watchlist.`);
                await updateWatchlist();
            } else {
                const errorData = await response.json();
                alert(`Error removing stock: ${errorData.error}`);
            }
        } catch (error) {
            console.error("Error removing stock from watchlist:", error);
            alert("Failed to remove stock from watchlist. Please try again later.");
        }
    }

    // Initial update to load watchlist on page load
    updateWatchlist();

    // Poll and check alerts every 30 seconds
    setInterval(checkPriceAlerts, 200);

    // Function to check stock prices against target price
    async function checkPriceAlerts() {
        try {
            const response = await fetch("http://localhost:6465/stocks", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const stocks = await response.json();

                stocks.forEach(stock => {
                    const storedData = JSON.parse(localStorage.getItem(`stock_${stock.symbol}`)) || {};
                    if (storedData.target_price) {
                        const currentPrice = parseFloat(stock.curr_price);
                        const targetPrice = parseFloat(storedData.target_price);

                        if (currentPrice <= targetPrice) {
                            displayNotification(stock.symbol);
                        }
                    }
                });
            } else {
                console.error("Failed to fetch watchlist for price alerts.");
            }
        } catch (error) {
            console.error("Error checking price alerts:", error);
        }
    }

    // Function to display an alert notification
    function displayNotification(stockSymbol) {
        const watchlistItems = document.querySelectorAll('.stock-watch-list ul li');

        watchlistItems.forEach(item => {
            if (item.textContent.includes(stockSymbol)) {
                if (!item.querySelector('.alert-icon')) {
                    const alertIcon = document.createElement('span');
                    alertIcon.textContent = ' ⚠️';  // Alert icon
                    alertIcon.classList.add('alert-icon');
                    item.appendChild(alertIcon);
                }
            }
        });

        // Display popup notification
        alert(`Price alert triggered for ${stockSymbol}!`);
    }
});