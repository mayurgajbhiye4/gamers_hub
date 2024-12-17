document.getElementById('searchInput').addEventListener('input', function () {
          const query = this.value.trim();

          if (query.length > 0) {
            fetch(`/search/?q=${encodeURIComponent(query)}`)
              .then(response => response.json())
              .then(data => {
                if (data.profiles || data.posts) {
                  let resultsHTML = '';

                  // Display profiles
                  if (data.profiles && data.profiles.length > 0) {
                    resultsHTML += '<h5>Users</h5><ul>';
                    data.profiles.forEach(profile => {
                      resultsHTML += `
                            <li>
                                <a href="${profile.profile_url}">
                                    <img src="${profile.avatar || '/static/images/default_avatar.png'}" alt="Avatar" class="rounded-circle me-2" width="40" height="40">
                                    <strong>${profile.first_name} ${profile.last_name}</strong> @${profile.username}
                                </a>
                            </li>
                        `;
                    });
                    resultsHTML += '</ul>';
                  }

                  // Display posts
                  if (data.posts && data.posts.length > 0) {
                    resultsHTML += '<h5>Posts</h5><ul>';
                    data.posts.forEach(post => {
                      resultsHTML += `
                                <li>
                                    <a href="${post.post_url}">
                                        <strong>${post.author}</strong>: ${post.text}
                                    </a>
                                    <span>${post.created_at}</span>
                                </li>
                            `;
                    });
                    resultsHTML += '</ul>';
                  }
                  
                  // Display Game zones
                  if (data.game_zones && data.game_zones.length > 0) {
                    resultsHTML += '<h5>Game Zones</h5><ul>';
                    data.game_zones.forEach(zone => {
                      resultsHTML += `
                                      <li>
                                          <a href="${zone.game_url}">
                                              <strong>${zone.game_title}</strong>
                                          </a>
                                      </li>
                                  `;
                    });
                    resultsHTML += '</ul>';
                  }

                  document.getElementById('searchResults').innerHTML = resultsHTML;
                } else {
                  document.getElementById('searchResults').innerHTML = '<p>No results found.</p>';
                }
              })
              .catch(error => {
                console.error('Error:', error);
                document.getElementById('searchResults').innerHTML = '<p>Something went wrong. Please try again later.</p>';
              });
          } else {
            document.getElementById('searchResults').innerHTML = '';
          }
        });