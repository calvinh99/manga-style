// View
const pageNavigationBox = document.getElementById('page-navigation-box');

function addPageButton(pageNumber) {
    const pageButton = document.createElement('button');
    pageButton.classList.add('page-button');
    if (pageNumber === current_page) {
        pageButton.style.backgroundColor = 'rgb(220, 160, 80)';
    }
    pageButton.innerText = pageNumber;
    pageNavigationBox.appendChild(pageButton);
    pageButton.addEventListener('click', function() {
        updateSearchQuery({'page': pageNumber});
    });
}

function addArrowPageButton(arrowText)  {
    const arrowPageButton = document.createElement('button');
    arrowPageButton.classList.add('arrow-page-button');
    arrowIcon = document.createElement('i');
    arrowPageButton.appendChild(arrowIcon);
    pageNavigationBox.appendChild(arrowPageButton);
    if (arrowText === '<') {
        arrowPageButton.style.paddingRight = '2px';
        arrowIcon.classList.add('arrow', 'left');
        arrowPageButton.addEventListener('click', function() {
            if (current_page > 1) {
                updateSearchQuery({'page': (current_page - 1)});
            }
        });
    } else if (arrowText === '>') {
        arrowPageButton.style.paddingLeft = '2px';
        arrowIcon.classList.add('arrow', 'right');
        arrowPageButton.addEventListener('click', function() {
            if (current_page < num_pages) {
                updateSearchQuery({'page': (current_page + 1)});
            }
        });
    }
}

function addEllipses() {
    const ellipses = document.createElement('div');
    ellipses.classList.add('ellipses');
    ellipses.innerText = '...';
    pageNavigationBox.appendChild(ellipses);
}

function addPageButtons(pageNumber) {
    if (num_pages <= 7) {
        for (let i = 1; i <= num_pages; i++) {
        addPageButton(i);
        }
        return
    }
    addPageButton(1);
    // handle middle 4 or 5 pages
    if (current_page  === 1 || current_page === num_pages) {
        addPageButton(2);
        addPageButton(3);
        addEllipses();
        addPageButton(num_pages-2);
        addPageButton(num_pages-1);
    } else if (current_page <= 4) {
        for (let i = 2; i <= 6; i++) {
        addPageButton(i);
        }
        addEllipses();
    } else if (current_page >= num_pages - 3) {
        addEllipses();
        for (let i = num_pages - 5; i <= num_pages-1; i++) {
        addPageButton(i);
        }
    } else {
        addEllipses();
        for (let i = current_page - 2; i <= current_page + 2; i++) {
        addPageButton(i);
        }
        addEllipses();
    }

    addPageButton(num_pages);
}

// Controller
addArrowPageButton('<');
addPageButtons();
addArrowPageButton('>');