document.addEventListener("DOMContentLoaded", function () {
    // Gets userid
    const userId = '{{ user_id }}';

    // Function to load recent transactions
    function loadRecentTransactions(userId) {
        fetch(`/get_transactions?user_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                const transactionList = document.querySelector('#transaction-list');
                transactionList.innerHTML = ''; // Clear existing transactions

                if (data.error) {
                    console.error(data.error);
                    transactionList.innerHTML = '<p>Failed to load recent transactions.</p>';
                    return;
                }

                if (data.length === 0) {
                    transactionList.innerHTML = '<p>No recent transactions.</p>';
                } else {
                    data.forEach(transaction => {
                        const transactionItem = document.createElement('li');
                        transactionItem.textContent = `${transaction.stock_symbol} | ${transaction.action} | ${transaction.quantity} shares | $${transaction.price} | $${transaction.total_value} | ${transaction.date}`;
                        transactionList.appendChild(transactionItem);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading transactions:', error);
                const transactionList = document.querySelector('#transaction-list');
                transactionList.innerHTML = '<p>Failed to load recent transactions.</p>';
            });
    }

    loadRecentTransactions(userId);
});