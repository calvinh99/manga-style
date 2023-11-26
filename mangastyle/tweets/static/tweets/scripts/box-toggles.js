const infoModal = document.getElementById("info-modal");
const filterDropdownContainer = document.getElementById('filter-dropdown-container');

function toggleInfoModal() {
    infoModal.classList.toggle('show-modal');
}

function toggleFilterDropdown() {
    filterDropdownContainer.classList.toggle('show-filter-dropdown');
}

const boxSelectors = ['.filter-button', '.filter-dropdown-menu', '.filter-dropdown-menu *',
                      '.info-button'];
                      
window.addEventListener('click', function(event) {
    if (!event.target.matches(boxSelectors)) {
        if (filterDropdownContainer.classList.contains('show-filter-dropdown')) {
            filterDropdownContainer.classList.remove('show-filter-dropdown');
        }
        if (infoModal.classList.contains('show-modal')) {
            infoModal.classList.remove('show-modal');
        }
    }
});