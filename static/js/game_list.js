document.addEventListener('DOMContentLoaded', function () {
        const searchInput = document.getElementById('searchInput');
        const gameList = document.getElementById('gameList');

        // Listen for user input
        searchInput.addEventListener('input', function () {
            const query = searchInput.value;

            // Make an AJAX GET request
            fetch(`/game-zone/ajax/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Clear the game list
                    gameList.innerHTML = '';

                    // Populate the list dynamically
                    if (data.games.length > 0) {
                        data.games.forEach(game => {
                            const listItem = document.createElement('a');
                            listItem.href = `/game_zone/${game}/`;
                            listItem.className = 'list-group-item list-group-item-action';
                            listItem.innerHTML = `<strong>${game}</strong>`;
                            gameList.appendChild(listItem);
                        });
                    } else {
                        // Show 'No games available' if empty
                        gameList.innerHTML = '<p class="text-center">No games available.</p>';
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });