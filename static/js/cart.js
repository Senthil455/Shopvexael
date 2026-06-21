// Add to Cart AJAX Logic
(function () {
    var userElement = document.getElementById('user-status');
    var user = userElement ? userElement.textContent : 'AnonymousUser';

    function addCookieItem(productID, action, btn) {
        if (action === 'add') {
            if (cart[productID] === undefined) {
                cart[productID] = { quantity: 1 };
            } else {
                cart[productID].quantity += 1;
            }
            showToast('Added to Cart \u2713');
            if (btn && btn.tagName === 'BUTTON') {
                btn.innerHTML = 'Added \u2713';
                setTimeout(function () {
                    btn.innerHTML = 'Add To Cart';
                    btn.disabled = false;
                }, 2000);
            }
        }
        if (action === 'remove') {
            cart[productID].quantity -= 1;
            if (cart[productID].quantity <= 0) {
                delete cart[productID];
            }
        }
        document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/';

        if (window.location.pathname === '/cart/') {
            location.reload();
        } else {
            var total = Object.values(cart).reduce(function (a, b) { return a + b.quantity; }, 0);
            var cartTotal = document.getElementById('cart-total');
            if (cartTotal) cartTotal.textContent = total;
        }
    }

    function updateUserOrder(productID, action, btn) {
        var url = '/update_item/';
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ productID: productID, action: action })
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (action === 'add') {
                showToast('Added to Cart \u2713');
                if (btn && btn.tagName === 'BUTTON') {
                    btn.innerHTML = 'Added \u2713';
                    setTimeout(function () {
                        btn.innerHTML = 'Add To Cart';
                        btn.disabled = false;
                    }, 2000);
                }
            }
            if (window.location.pathname === '/cart/' || window.location.pathname === '/checkout/') {
                location.reload();
            } else {
                if (data.cartItems !== undefined) {
                    var cartTotal = document.getElementById('cart-total');
                    if (cartTotal) cartTotal.textContent = data.cartItems;
                }
            }
        });
    }

    var updateBtns = document.querySelectorAll('.update-cart');
    for (var i = 0; i < updateBtns.length; i++) {
        updateBtns[i].addEventListener('click', function () {
            var productID = this.dataset.product;
            var action = this.dataset.action;
            var btn = this;

            if (btn.tagName === 'BUTTON' && action === 'add') {
                btn.innerHTML = 'Adding...';
                btn.disabled = true;
            }

            if (user === 'AnonymousUser') {
                addCookieItem(productID, action, btn);
            } else {
                updateUserOrder(productID, action, btn);
            }
        });
    }
})();
