const apiUrl = "https://cezl7l5gpk.execute-api.eu-west-1.amazonaws.com/Prod";

/**
 * Redirect to the login screen
 * Called after an error occurs and the error message is displayed on the login page
 * @param {string} errorMessage 
 */
function redirectToLogin(errorMessage) {
    localStorage.setItem('loginError', errorMessage);
    window.location.href = "login.html";
}

const loadingScreen = document.querySelector('.loading-screen');
const container = document.querySelector(".container");

/**
 * Display the loading icon while waiting for api response
 */
function displayLoading() {
    container.style.display = 'none';
    loadingScreen.style.display = 'flex';
}

/**
 * Hide the loading icon so that data can be shown
 */
function hideLoading() {
    loadingScreen.style.display = 'none';
    container.style.display = 'block';
}

/**
 * Make a GET request to fetch the client's units
 */
async function fetchClientUnits() {
    try {
        const response = await fetch(`${apiUrl}/units?type=client&client=${localStorage.getItem('email')}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // used to send JWT as part of the request 
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`,
            },
        });

        if (response.status === 401) {
            redirectToLogin("You are unauthorized please login.")
        } else if (!response.ok) {
            throw new Error(response.status);
        }

        const clientUnits = await response.json();
        hideLoading();
        displayUnits(clientUnits);
    } catch (error) {
        if (error instanceof TypeError) {
            redirectToLogin("You need to login to fetch your units.")
        } else {
            console.error('Error fetching client units:', error);
        }
    }
}

/**
 * Showing whether a unit is being shared or not
 * @param {json} unit 
 * @param {element} unitDiv 
 */
function sharedUnit(unit, unitDiv) {
    if (unit.shared_with && unit.shared_with.length > 0) {
        const sharedDiv = document.createElement('div');
        sharedDiv.className = "shared-container";
        const sharedIcon = document.createElement('img');
        sharedIcon.className = 'shared-icon';
        sharedIcon.src = "https://img.icons8.com/?size=100&id=5tsTtEE1S9CP&format=png&color=000000";
        sharedIcon.alt = 'Shared Icon';
        sharedDiv.appendChild(sharedIcon);
        const tooltip = document.createElement('span');
        tooltip.className = 'tooltip';
        tooltip.innerText = 'Shared with: ' + unit.shared_with; 
        sharedDiv.appendChild(tooltip);
        unitDiv.appendChild(sharedDiv);
    }
}

/**
 * Load the unit details page
 * @param {json} unit 
 */
function loadCardScreen(unit) {
    const unitDetailUrl = `unit_details.html?unit_id=${unit.unit_id}`;
    window.location.href = unitDetailUrl;
}

/**
 * Display the client's units
 * @param {json} json 
 * @returns if no units are being rented
 */
function displayUnits(json) {
    const container = document.getElementById('units-container');
    container.innerHTML = '';
    units = JSON.parse(json).units;

    if (units.length === 0) {
        container.innerHTML = '<p>You are not currently renting any units</p>';
        return;
    }

    units.forEach(unit => {
        console.log(unit);
        const unitDiv = document.createElement('div');
        unitDiv.className = `unit`;

        unitDiv.innerHTML = `
        <h3>${unit.unit_id} - ${unit.size}</h3>
        <p>Location: ${unit.location}</p>
        <p>Total Expense: R${unit.accrued_cost}</p>
        <p>End Date: ${unit.end_date === "indefinite" ? "Never" : unit.end_date}</p>
        `;
        
        sharedUnit(unit, unitDiv);

        unitDiv.addEventListener("click", () => loadCardScreen(unit));

        container.appendChild(unitDiv);
    });
}

/**
 * When the page loads diasplay loading and try to fetch the client's units
 */
window.onload = function () {
    displayLoading();
    fetchClientUnits();
}

