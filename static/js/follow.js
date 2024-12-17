document.querySelectorAll('.follow-btn').forEach(button => {
          button.addEventListener('click', function () {
            const username = this.dataset.username;

            // Make a POST request to toggle the follow state
            fetch(`/follow/${username}/`, {
              method: 'POST',
              headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest',
              },
            })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  // Update the button text based on follow state
                  if (data.following) {
                    this.textContent = 'Unfollow';
                  } else {
                    this.textContent = 'Follow';
                  }
                } else {
                  console.error('Error:', data.error || 'Failed to follow/unfollow');
                }
              })
              .catch(error => console.error('Error:', error));
          });
        });