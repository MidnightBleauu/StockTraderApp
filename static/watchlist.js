document.addEventListener("DOMContentLoaded", function () {
        var modal = document.getElementById("watchlistModal");
        var btn = document.getElementById("addWatchlistButton");
        var span = document.getElementsByClassName("close")[0];

        // When the user clicks on the button opens the popup
        btn.onclick = function() {
            modal.style.display = "block";
        }

        span.onclick = function() {
            modal.style.display = "none";
        }

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }

        // Get the "Add to Watchlist" button
        var addStockButton = document.getElementById("addStockToWatchlist");
        addStockButton.onclick = function() {
            var stockTickerSelect = document.getElementById("stockTickerSelect");
            var selectedStock = stockTickerSelect.value;

            var watchlist = document.querySelector('.stock-watch-list ul');
            var newStockItem = document.createElement('li');
            newStockItem.textContent = selectedStock + " | --- | --- | --- | --/--/--";
            watchlist.appendChild(newStockItem);

            modal.style.display = "none";
        }
    });