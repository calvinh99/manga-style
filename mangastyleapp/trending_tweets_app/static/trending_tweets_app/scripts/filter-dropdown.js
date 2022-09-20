// View
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
    filterRadioButton.id = radioValue;
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

// Implementation
for (const [filterName, filterProperties] of Object.entries(filterDict)) {
    let radioToCheck = new URLSearchParams(window.location.search).get(filterName); // TODO: test if you edit search param to a non valid value
    const radioValues = Object.keys(filterProperties['filterValues'])
    if (radioToCheck == null || !radioValues.includes(radioToCheck)) {
        radioToCheck = filterProperties['radioToCheck'];
    }

    addFilterBox(filterProperties['filterTitle'], 
                 radioValues, 
                 filterProperties['radioName'], 
                 filterProperties['radioDirection'], 
                 radioToCheck);
}