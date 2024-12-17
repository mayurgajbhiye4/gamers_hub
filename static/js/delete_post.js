function deletePost(postId) {
        fetch(`/post/${postId}/delete/`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': '{{ csrf_token }}'
          },
        })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              document.querySelector(`#post-${postId}`).remove(); // Remove post from DOM
              alert('Post deleted successfully.');
            } else {
              alert('Error deleting post.');
            }
          })
          .catch(error => console.error('Error:', error));
      }