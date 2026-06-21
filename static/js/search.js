// AJAX Search with Suggestions
(function () {
    var searchInput = document.getElementById('search-input');
    var suggestionsBox = document.getElementById('search-suggestions');
    if (!searchInput || !suggestionsBox) return;

    var debounceTimer = null;

    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        var query = this.value.trim();

        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(function () {
            fetch('/ajax_search/?q=' + encodeURIComponent(query))
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    suggestionsBox.innerHTML = '';
                    if (data.length > 0) {
                        data.forEach(function (item) {
                            var div = document.createElement('div');
                            div.style.cssText = 'padding: 12px 15px; cursor: pointer; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid var(--border-color);';
                            div.className = 'suggestion-item';

                            var img = document.createElement('img');
                            img.src = item.image || '';
                            img.style.cssText = 'width: 40px; height: 40px; object-fit: cover; border-radius: 4px; background: white;';
                            var textDiv = document.createElement('div');
                            var nameDiv = document.createElement('div');
                            nameDiv.style.cssText = 'font-weight: bold; font-size: 0.9rem;';
                            nameDiv.textContent = item.name;
                            var priceDiv = document.createElement('div');
                            priceDiv.style.cssText = 'color: var(--accent-gold); font-size: 0.8rem;';
                            priceDiv.textContent = '\u20B9' + item.price;
                            textDiv.appendChild(nameDiv);
                            textDiv.appendChild(priceDiv);
                            div.appendChild(img);
                            div.appendChild(textDiv);
                            div.onclick = function () { window.location.href = item.url; };
                            suggestionsBox.appendChild(div);
                        });
                        suggestionsBox.style.display = 'block';
                    } else {
                        suggestionsBox.style.display = 'none';
                    }
                });
        }, 300);
    });

    document.addEventListener('click', function (e) {
        if (!suggestionsBox.contains(e.target) && e.target !== searchInput) {
            suggestionsBox.style.display = 'none';
        }
    });
})();
