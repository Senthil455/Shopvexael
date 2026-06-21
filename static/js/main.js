// CSRF Token Utilities
function getToken(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getToken('csrftoken');

function getCookie(name) {
    var cookieArr = document.cookie.split(';');
    for (var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split('=');
        if (name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}

var cart = JSON.parse(getCookie('cart'));
if (cart === undefined || cart === null) {
    cart = {};
    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/';
}

function showToast(message, type) {
    type = type || 'success';
    var toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.padding = '15px 25px';
    toast.style.borderRadius = '5px';
    toast.style.color = 'white';
    toast.style.fontWeight = 'bold';
    toast.style.zIndex = '9999';
    toast.style.transition = 'opacity 0.5s ease-in-out';
    toast.textContent = message;

    if (type === 'success') toast.style.backgroundColor = '#10b981';
    else if (type === 'error') toast.style.backgroundColor = '#ef4444';
    else toast.style.backgroundColor = 'var(--accent-gold)';

    document.body.appendChild(toast);
    setTimeout(function () {
        toast.style.opacity = '0';
        setTimeout(function () { toast.remove(); }, 500);
    }, 3000);
}

function updateCartButtons() {
    document.querySelectorAll('.update-cart').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var productID = this.dataset.product;
            var action = this.dataset.action;
            var originalHTML = btn.innerHTML;
            btn.innerHTML = 'Adding...';
            btn.disabled = true;

            var url = '/update_item/';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ productID: productID, action: action })
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                btn.innerHTML = 'Added &#10003;';
                setTimeout(function () {
                    btn.innerHTML = 'Add To Cart';
                    btn.disabled = false;
                }, 2000);
                var cartCount = document.getElementById('cart-count');
                if (cartCount) cartCount.textContent = data.cartItems;
            })
            .catch(function () {
                btn.innerHTML = originalHTML;
                btn.disabled = false;
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    updateCartButtons();
});
