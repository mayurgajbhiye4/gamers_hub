document.querySelectorAll('.like-btn').forEach(button => {
            button.addEventListener('click', function () {
              const postId = this.dataset.postId;

              fetch(`/post/${postId}/`, {  // Endpoint points to `post_detail` view
                method: "POST",
                headers: {
                  "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                  "X-Requested-With": "XMLHttpRequest",
                },
              })
                .then(response => response.json())
                .then(data => {
                  if (data.success) {
                    // Update likes count dynamically
                    const likeCount = document.querySelector(`.like-count[data-post-id="${postId}"]`);
                    likeCount.textContent = data.likes_count;

                    // Toggle heart icon
                    const icon = this.querySelector('i');
                    icon.classList.toggle('bi-heart');
                    icon.classList.toggle('bi-heart-fill');
                  }
                })
                .catch(error => console.error("Error:", error));
            });
          });