document.getElementById("add-comment-form").addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent the default form submission
            
            const postId = document.getElementById("add-comment-form").dataset.postId;
            const text = document.getElementById("comment-text").value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/post/${postId}/add_comment/`, {
              method: "POST",
              headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken,
              },
              body: new URLSearchParams({
                text: text,
              }),
            })
              .then((response) => response.json())
              .then((data) => {
                if (data.error) {
                  alert(data.error);
                } else {
                  // Add the new comment to the comments list
                  const commentsContainer = document.getElementById("comments-container");
                  const newComment = `
          <div class="card mb-2">
            <div class="card-body">
              <strong>${data.user}</strong> <small class="text-muted">@${data.username}</small>
              <p>${data.text}</p>
              <small class="text-muted">${data.timestamp}</small>
            </div>
          </div>
        `;
                  commentsContainer.insertAdjacentHTML("beforeend", newComment);

                  // Clear the comment input field
                  document.getElementById("comment-text").value = "";
                }
              })
              .catch((error) => console.error("Error:", error));
          });