setInterval(() => {
        fetch('/check_notifications/', {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
        })
          .then(response => response.json())
          .then(data => {
            const bellIcon = document.querySelector('.bi-bell, .bi-bell-fill');
            if (data.unread) {
              bellIcon.classList.remove('bi-bell');
              bellIcon.classList.add('bi-bell-fill');
            } else {
              bellIcon.classList.remove('bi-bell-fill');
              bellIcon.classList.add('bi-bell');
            }
          })
          .catch(error => console.error('Error fetching notifications:', error));
      }, 5000); // Check every 5 seconds