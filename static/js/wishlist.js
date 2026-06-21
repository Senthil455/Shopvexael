// Wishlist AJAX
(function () {
    var wishlistForms = document.querySelectorAll('.wishlist-form');
    for (var i = 0; i < wishlistForms.length; i++) {
        wishlistForms[i].addEventListener('submit', function (e) {
            e.preventDefault();
            var url = this.action;
            var btn = this.querySelector('button');
            var icon = btn ? btn.querySelector('i') : null;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function (response) { return response.json(); })
            .then(function (data) {
                if (data.status === 'unauthenticated') {
                    window.location.href = '/login/';
                } else if (data.status === 'added') {
                    showToast('Added to Wishlist \u2713', 'success');
                    if (icon) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        icon.style.color = 'var(--accent-red)';
                    }
                } else if (data.status === 'removed') {
                    showToast('Removed from Wishlist', 'info');
                    if (icon) {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        icon.style.color = '';
                    }
                }
            });
        });
    }
})();
