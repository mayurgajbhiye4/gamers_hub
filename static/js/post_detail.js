function openPostDetail(postId) {
    window.location.href = `{% url 'post_detail' 0 %}`.replace(0, postId);
}
