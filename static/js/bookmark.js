document.addEventListener("DOMContentLoaded", function () {
          const bookmarkButtons = document.querySelectorAll(".bookmark-btn");

          bookmarkButtons.forEach((btn) => {
            btn.addEventListener("click", function () {
              const postId = btn.getAttribute("data-post-id");
              const url = `/toggle-bookmark/${postId}/`;

              fetch(url, {
                method: "POST",
                headers: {
                  "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
              })
                .then((response) => response.json())
                .then((data) => {
                  if (data.bookmarked) {
                    btn.textContent = "Unbookmark";
                  } else {
                    btn.textContent = "Bookmark";
                  }
                })
                .catch((error) => {
                  console.error("Error:", error);
                });
            });
          });
        });