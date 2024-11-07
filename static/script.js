document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#search-input');
    const suggestionBox = document.querySelector('#suggestion-box');

    // Fetches and pulls the suggestions
    const fetchSuggestions = async (query) => {
        try {
            // Fetchs from the correct location from the stock.py
            const response = await fetch(`http://localhost:5001/search_api?query=${query}`);
            if (response.ok) {
                const data = await response.json();

                // clears any old suggestions
                suggestionBox.innerHTML = '';

                if (data.bestMatches && data.bestMatches.length > 0) {
                    suggestionBox.style.display = 'block';
                    data.bestMatches.forEach(result => {
                        const listItem = document.createElement('li');
                        listItem.textContent = `${result['1. symbol']} - ${result['2. name']}`;
                        listItem.classList.add('suggestion-item');
                        suggestionBox.appendChild(listItem);

                        // Event listener for clicking the suggesitons
                        listItem.addEventListener('click', () => {
                            // Redirects to teh stock page
                            window.location.href = `/stocks/${result['1. symbol']}`;
                        });
                    });
                } else {
                    suggestionBox.style.display = 'none';
                }
            } else {
                console.error("Error fetching search results:", response.statusText);
            }
        } catch (error) {
            console.error("Error fetching search results:", error);
        }
    };

    // Fetches the suggestins
    searchInput.addEventListener('input', function () {
        const query = this.value ? this.value.trim() : '';

        if (query.length > 1) {
            fetchSuggestions(query);
        } else {
            suggestionBox.innerHTML = '';
            suggestionBox.style.display = 'none';
        }
    });

    // Hides the box
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionBox.contains(e.target)) {
            suggestionBox.style.display = 'none';
        }
    });
});