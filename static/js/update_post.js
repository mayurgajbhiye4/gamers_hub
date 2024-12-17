document.addEventListener('DOMContentLoaded', function () {
        const updatePostModal = document.getElementById('updatePostModal');
        const updatePostForm = document.getElementById('updatePostForm');
        const updatePostText = document.getElementById('updatePostText');
        const updatePostImage = document.getElementById('updatePostImage');
        const updatePostVideo = document.getElementById('updatePostVideo');
        const updateGameTitle = document.getElementById('updateGameTitle'); // Game title input field

        // Open the modal and populate it with post data
        document.querySelectorAll('.update-post-btn').forEach(button => {
          button.addEventListener('click', function () {
            const postId = this.dataset.postId;
            const postContent = this.dataset.postContent;
            const gameTitle = this.dataset.gameTitle;  // Fetch game_title from dataset

            // Populate the modal fields
            updatePostText.value = postContent;
            updateGameTitle.value = gameTitle || ''; // Set game_title field
            updatePostForm.setAttribute('data-post-id', postId);

            // Show the modal
            const modal = new bootstrap.Modal(updatePostModal);
            modal.show();
          });
        });

        // Handle form submission
        updatePostForm.addEventListener('submit', function (event) {
          event.preventDefault();

          const form = event.target;
          const postId = form.getAttribute('data-post-id');
          const formData = new FormData(form);

          // Append the game_title explicitly (if the form doesn't auto-include it)
          formData.append('game_title', updateGameTitle.value);

          fetch(`/post/${postId}/update/`, {
            method: 'POST',
            body: formData,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
          })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                // Redirect to the provided URL
                window.location.href = data.redirect_url;
              } else {
                alert(data.error || 'Failed to update the post.');
              }
            })
            .catch(error => {
              console.error('Error:', error);
              alert('Something went wrong. Please try again.');
            });
        });
      });