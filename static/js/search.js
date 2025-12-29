/* ============================================
   SEARCH FUNCTIONALITY
   ============================================ */

const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

if (searchInput) {
    // Debounced search handler
    const handleSearch = debounce(async (query) => {
        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.results.length === 0) {
                searchResults.innerHTML = '<div style="padding: 1rem; text-align: center; color: #999;">No games found</div>';
                searchResults.classList.remove('hidden');
                return;
            }

            // Build HTML for search results
            const html = data.results.map(game => `
                <div class="search-result-item" onclick="goToGame(${game.id})">
                    <div style="font-weight: 600; color: #00d4ff;">${game.title}</div>
                    <div style="font-size: 0.85rem; color: #999;">${game.genre}</div>
                </div>
            `).join('');

            searchResults.innerHTML = html;
            searchResults.classList.remove('hidden');
        } catch (error) {
            console.error('Search error:', error);
            showToast('Error during search', 'error');
        }
    }, 300);

    searchInput.addEventListener('input', (e) => {
        handleSearch(e.target.value);
    });

    // Hide results when clicking elsewhere
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });
}

/**
 * Navigate to game detail
 */
function goToGame(gameId) {
    window.location.hash = `game-${gameId}`;
}