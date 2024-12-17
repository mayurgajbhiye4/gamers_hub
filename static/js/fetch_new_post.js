function fetchNewPosts() {
        fetch("/fetch-new-posts/")
          .then(response => response.json())
          .then(posts => {
            posts.forEach(post => {
              // Assuming you have a function to append a new post to your feed
              addPostToFeed(post);
            });
          })
          .catch(error => console.error('Error fetching new posts:', error));
      }

      // Poll the server every 10 seconds
      setInterval(fetchNewPosts, 10000);

      function addPostToFeed(post) {
        // This function should format and insert the post content into your HTML
        const postHtml = `
          <div class="card mb-4">
            <div class="card-body">
              <strong>${post.fields.author}</strong>
              <p>${post.fields.text}</p>
            </div>
          </div>`;
        document.querySelector('.feed-container').insertAdjacentHTML('afterbegin', postHtml);
      }