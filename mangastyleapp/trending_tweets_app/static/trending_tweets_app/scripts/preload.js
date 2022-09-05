// constrain the loaded images' aspect ratios
function aspectRatioConstraints(img) {
    const aspectRatio = img.naturalWidth / img.naturalHeight;
    if (aspectRatio < 3/4) {
        img.style.aspectRatio = '3/4';
    }
    else if (aspectRatio > 2) {
        img.style.aspectRatio = '2/1';
    }
}

// update the query string in url
function updateSearchQuery(queries) {
    const searchParams = new URLSearchParams(window.location.search);
    for (const [key, value] of Object.entries(queries)) {
        searchParams.set(key, value);
    }
    window.location.search = searchParams.toString();
}

// update the query string in url with checked filters
function applyFilters() {
    const queries = {'page': 1};
    for (const filterName of Object.keys(filterDict)) {
        checkedRadio = document.querySelector(`input[name=${filterName}]:checked`).value;
        if (checkedRadio !== 'None') {  // so you don't add a query string for None
            queries[filterName] = checkedRadio;
        }
    }
    updateSearchQuery(queries);
}