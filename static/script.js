document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('#search-input');
    const suggestionBox = document.querySelector('#suggestion-box');
    let debounceTimeout;

    // Limit API calls (only 25 a day allowed)
    const debounce = (func, delay) => {
        return (...args) => {
            if (debounceTimeout) {
                clearTimeout(debounceTimeout);
            }
            debounceTimeout = setTimeout(() => {
                func.apply(null, args);
            }, delay);
        };
    };

    // Fetch and display suggestions
    const fetchSuggestions = async (query) => {
        try {
            const response = await fetch(`/search_api?query=${query}`);
            const data = await response.json();

            // this will clear suggestions
            suggestionBox.innerHTML = '';

            if (data.length > 0) {
                suggestionBox.style.display = 'block';
                data.forEach(result => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${result['1. symbol']} - ${result['2. name']}`;
                    suggestionBox.appendChild(listItem);

                    // Event listener for clicking and then to display suggesutions
                    listItem.addEventListener('click', () => {
                        searchInput.value = result['1. symbol'];
                        suggestionBox.innerHTML = ''; // Clear suggestions
                        suggestionBox.style.display = 'none';
                    });
                });
            } else {
                suggestionBox.style.display = 'none';
            }
        } catch (error) {
            console.error("Error fetching search results:", error);
        }
    };


    searchInput.addEventListener('input', debounce(function () {
        const query = this.value.trim();

        if (query.length > 1) {
            fetchSuggestions(query);
        } else {
            suggestionBox.innerHTML = '';
            suggestionBox.style.display = 'none';
        }
    }, 300));
    
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionBox.contains(e.target)) {
            suggestionBox.style.display = 'none';
        }
    });
});
