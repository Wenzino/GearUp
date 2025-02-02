document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.querySelector('.search-btn');
    const searchInput = document.querySelector('.search-input');
    const resultsContainer = document.querySelector('.autocomplete-results');

    // Toggle search input
    searchBtn.addEventListener('click', function(e) {
        e.preventDefault();
        searchInput.classList.toggle('active');
        if (searchInput.classList.contains('active')) {
            searchInput.focus();
        }
    });

    // Live search
    searchInput.addEventListener('input', function(e) {
        const query = this.value.trim();
        
        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        fetch(`/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    resultsContainer.innerHTML = data.results.map(item => `
                        <div class="autocomplete-item" data-url="${item.url}">
                            <img src="${item.image}" alt="${item.name}">
                            <div>
                                <h6>${item.name}</h6>
                                <small>R$ ${item.price.toFixed(2)}</small>
                            </div>
                        </div>
                    `).join('');
                    resultsContainer.style.display = 'block';
                } else {
                    resultsContainer.style.display = 'none';
                }
            });
    });

    // Handle click outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container')) {
            searchInput.classList.remove('active');
            resultsContainer.style.display = 'none';
        }
    });

    // Handle item selection
    resultsContainer.addEventListener('click', function(e) {
        if (e.target.closest('.autocomplete-item')) {
            window.location.href = e.target.closest('.autocomplete-item').dataset.url;
        }
    });
}); 