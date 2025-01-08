const startDateField = document.getElementById('start-date');
const endDatefield = document.getElementById('end-date');
const indefiniteCheckBox = document.getElementById("indefinite-end-date");
const rentForm = document.getElementById('rent-form');
const clearButton = document.getElementById('clear');
const cancelButton = document.getElementById('cancel');
const bookButton = document.getElementById('book');
const locationField = document.getElementById('facility');
const sizeField = document.getElementById('unit-size');

const apiUrl = "https://cezl7l5gpk.execute-api.eu-west-1.amazonaws.com/Prod";
let unitId;

/**
 * Setting the minimum dates to the current day,
 * so that they cannot rent in the past.
*/
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split("T")[0];

    startDateField.setAttribute("min", today);
    endDatefield.setAttribute("min", today);
});

/**
 * Set the minimum end date as the selected start date.
 */
startDateField.addEventListener("change", function() {
    const startDate = this.value;
    endDatefield.setAttribute("min", startDate);
});

/**
 * Disabling and enabling the end-date field 
 * and the prepaid option
 * based on whether the user has chosen to rent indefinitely or not.
 */
indefiniteCheckBox.addEventListener('change', () => {
    const billingOption = document.getElementById('billing-option');
    const warning = document.getElementById('billing-warning');

    if (indefiniteCheckBox.checked) {
        endDatefield.disabled = true;
        billingOption.querySelector('option[value="prepaid"]').disabled = true;

        if (billingOption.value === 'prepaid') {
            warning.classList.remove('hidden');
            billingOption.value = '';
        }
    } else {
        endDatefield.disabled = false;

        billingOption.querySelector('option[value="prepaid"]').disabled = false;
        warning.classList.add('hidden');
    }
});

/**
 * Clearing the form.
 */
clearButton.addEventListener('click', () => {
    rentForm.reset();
});

/**
 * Cancel takes them back to the home page.
 */
cancelButton.addEventListener('click', () => {
    window.location.href = "home.html";
});

/**
 * Take them back to the login page because an error occurred
 * @param {string} errorMessage 
 */
function redirectToLogin(errorMessage) {
    localStorage.setItem('loginError', errorMessage);
    window.location.href = "login.html";
}

/**
 * Adding event listener for the rental form.
 * Send a GET request for all the units matching their chosen options.
 */
rentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const location = locationField.value;
    const size = sizeField.value;
    const startDate = startDateField.value;
    const endDate = indefiniteCheckBox.checked ? 'indefinite' : endDatefield.value;
    const billingOption = document.getElementById('billing-option').value;
    const paymentType = document.getElementById('payment-type').value;

    console.log(`${location} ${size} ${startDate} ${endDate} ${billingOption} ${paymentType}`);

    try {
        const response = await fetch(`${apiUrl}/units?type=state&state=available&location=${location}&size=${size}`, {
            method: 'GET', 
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`
            },
        });

        if (response.status === 401) {
            redirectToLogin("You are unauthorized please login.");
        } else if (!response.ok) {
            throw new Error(response.status);
        }

        const units = await response.json();
        displayAvailableUnits(units, startDate, endDate, billingOption, paymentType);
    } catch (err) {
        if (err instanceof TypeError) {
            redirectToLogin("You need to login to rent a unit.");
        }
        console.error('Error fetching available units:', err);
    }
});

/**
 * Display all the units matching their description
 * @param {json} jsonUnits 
 * @param {string} start 
 * @param {string} end 
 * @param {string} billing 
 * @param {string} payment 
 * @returns 
 */
function displayAvailableUnits(jsonUnits, start, end, billing, payment) {
    const container = document.getElementById('available-units-container');
    container.innerHTML = '';

    const units = JSON.parse(jsonUnits).units;

    if (units.length === 0) {
        container.innerHTML = `
            <p>No available units matching your criteria.</p>`;
        return;
    }

    units.forEach(unit => {
        unitId = unit.unit_id;
        const unitCard = document.createElement('div');
        unitCard.className = 'unit';

        unitCard.innerHTML = `
            <h3>${unit.unit_id} - ${unit.size}</h3>
            <p>Location: ${unit.location}</p>
            <p>Price: R${unit.price}</p>
            <button class='btn-secondary' onclick="rentUnit('${start}', '${end}', '${billing}',' ${payment}')">Rent Now</button>`;
        
        container.appendChild(unitCard);
    });

    openModal();
}

/**
 * Send a PUT request to rent a chosen unit
 * @param {string} start 
 * @param {string} end 
 * @param {string} billingOption 
 * @param {string} paymentType 
 */
async function rentUnit(start, end, billingOption, paymentType) {
    const rentDetails = {
        unit_id: unitId,
        start_date: start,
        end_date: end,
        email: localStorage.getItem('email'),
        billing_option: billingOption,
        payment_type: paymentType,
    };

    try {
        const response = await fetch(`${apiUrl}/rent`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`
                
            },
            body: JSON.stringify(rentDetails),
        });

        if (response.ok) {
            alert('Unit rented successfully');
            window.location.href = 'client_units.html';
        } else {
            const error = await response.json();
            alert(`Error: ${error.message}`);
        }
    } catch (err) {
        console.error('Error renting unit:', err);
    }
    console.log("Renting unit");
    closeModal();
}

/**
 * Open the modal where the available units will be displayed
 */
function openModal() {
    const modal = document.getElementById('availableUnitsModal');
    modal.style.display = 'block';
    modal.querySelector('.btn-close').addEventListener('click', () => closeModal());


    window.onclick = (e) => {
        if (e.target === modal) {
            closeModal();
        }
    };
}

/**
 * Close the modal displaying the available units
 */
function closeModal() {
    const modal = document.getElementById('availableUnitsModal');
    modal.style.display = 'none';
}
