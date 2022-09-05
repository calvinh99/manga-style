// View
const filterDropdownContainer = document.getElementById('filter-dropdown-container');
const filterDropdownMenu = document.getElementById('filter-dropdown-menu');
 
// create the fitler title div
function createFilterTitle(filterTitle) {
    const filterTitleDiv = document.createElement('div');
    filterTitleDiv.classList.add('filter-title');
    filterTitleDiv.innerText = filterTitle;
    return filterTitleDiv;
}

// creating one radio box (radio button + label)
function createRadioBox(radioName, radioValue, checkedValue) {
    const filterRadioBox = document.createElement('div');
    filterRadioBox.classList.add('filter-radio-box');

    const filterRadioButton = document.createElement('input');
    filterRadioButton.type = 'radio';
    filterRadioButton.name = radioName;
    filterRadioButton.value = radioValue;
    if (radioValue === checkedValue) {
        filterRadioButton.checked = true;
    }
    const filterRadioLabel = document.createElement('label');
    filterRadioLabel.htmlFor = radioValue;
    filterRadioLabel.innerText = radioValue;

    filterRadioBox.appendChild(filterRadioButton);
    filterRadioBox.appendChild(filterRadioLabel);
    return filterRadioBox;
}

function addFilterBox(filterTitle, filterValues, radioName, radioDirection, checkedValue) {
    const filterBox = document.createElement('div');
    filterBox.classList.add('filter-box');

    // 1. Title of the filter
    filterBox.appendChild(createFilterTitle(filterTitle));

    // 2. Radio group for the filter
    const filterRadioGroup = document.createElement('div');
    filterRadioGroup.classList.add('filter-radio-group');
    filterRadioGroup.style.flexDirection = radioDirection;
    filterValues.forEach(filterValue => {
        filterRadioGroup.appendChild(createRadioBox(radioName, filterValue, checkedValue));
    });
    filterBox.appendChild(filterRadioGroup);

    // 3. Append the filter to the dropdown menu
    filterDropdownMenu.appendChild(filterBox);
}

// Controller
function toggleFilterDropdown() {
    filterDropdownContainer.classList.toggle("show");
}

const dropdownSelectors = ['.filter-button', '.filter-dropdown-menu', '.filter-dropdown-menu *'];
window.onclick = (event) => {
    if (!event.target.matches(dropdownSelectors)) {
        if (filterDropdownContainer.classList.contains('show')) {
        filterDropdownContainer.classList.remove('show');
        }
    }
}

// Implementation
for (const [filterName, filterProperties] of Object.entries(filterDict)) {
    let checkedValue = new URLSearchParams(window.location.search).get(filterName);
    if (checkedValue == null) {
        checkedValue = filterProperties['checkedValue'];
    }

    addFilterBox(filterProperties['filterTitle'], 
                 filterProperties['filterValues'], 
                 filterName, 
                 filterProperties['radioDirection'], 
                 checkedValue);
}