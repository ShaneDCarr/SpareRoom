// Get the unit id from the url params
const params = new URLSearchParams(window.location.search);
const unitId = params.get("unit_id");
const unitInfoSection = document.getElementById('unit-info');

const apiUrl = "https://cezl7l5gpk.execute-api.eu-west-1.amazonaws.com/Prod";

let shared;
let unit;
let openButton;
const loadingScreen = document.querySelector('.loading-screen');
const container = document.querySelector('.details-container');

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
 * Redirect to the login screen
 * Called after an error occurs and the error message is displayed on the login page
 * @param {string} errorMessage 
 */
function redirectToLogin(errorMessage) {
    localStorage.setItem('loginError', errorMessage);
    window.location.href = "login.html";
}

/**
 * Go back to the client units page
 */
function goBack() {
    window.location.href = "client_units.html";
}

/**
 * Reload the unit details page
 * Usually after change occurs
 */
function unitDetailsBack() {
    window.location.href = `unit_details.html?unit_id=${unitId}`;
}

/**
 * Make a GET request to fetch the details of a particular unit
 */
async function fetchUnitDetails() {
    try {
        const response = await fetch(`${apiUrl}/units?type=unit_id&unit_id=${unitId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`,
            },
        });

        if (!response.ok) {
            throw new Error(response.status);
        }

        hideLoading();
        const responseUnit = await response.json();
        unit = JSON.parse(responseUnit);
        console.log(unit);
        displayDetails();
    } catch (err) {
        // Can assume if there is a TypeError that the user is attempting to access information without being logged in
        if (err instanceof TypeError) {
            redirectToLogin("You need to login to fetch your units.")
        } else {
            console.error('Error fetching the unit details:', err)
        }
    }
}

/**
 * Display all the unit details in a unit information section
 */
function displayDetails() {
    shared = determineShared(unit.shared);
    if (unit) {
        unitInfoSection.innerHTML = `
        <h3>Unit ${unitId}</h3>
        <p>Location: ${unit.location}</p>
        <p>Size: ${unit.size}</p>
        <p>Price: R${unit.accrued_cost}</p>
        <p>Billing: ${unit.billing_option}</p>
        <p>Payment: ${unit.unit_payment_type}</p>
        <p>Shared: ${shared}</p>
        <p id='${unit.unit_id}-open-tag'>Open: ${unit.open === false ? 'no' : 'yes'}</p>
        <p>End Date: ${unit.end_date === 'indefinite' ? 'Never' : unit.end_date}</p>
        <button class="btn-secondary" id='${unit.unit_id}-open'>${unit.open === false ? 'Open' : 'Close'}</button>
        `
        // If the user has cancelled notify them that the unit will be unavailable at the end of the month
        if (unit.state === "Cancelled") {
            const warningParagraph = document.createElement("p");
            warningParagraph.textContent = "This unit will be cancelled by the end of the month.";
            warningParagraph.style.color = "red";
            unitInfoSection.appendChild(warningParagraph);
        }

        // Event listener to handle functionality of the open button
        openButton = document.getElementById(`${unit.unit_id}-open`);
        openButton.addEventListener('click', (e) => {
            e.stopPropagation();
            if (openButton.innerText === 'Open') {
                sendRequest(unit.unit_id, "open", "true", openButton);
            } else {
                sendRequest(unit.unit_id, "open", "false", openButton);
            }
        });
    }
}

/**
 * Make a PUT request to change the openness of the unit
 * For opening and closing the unit.
 * @param {string} unitID 
 * @param {string} change 
 * @param {BOOL} value 
 * @param {element} openButton 
 */
async function sendRequest(unitID, change, value, openButton) {
    const changeSet = {
        unit_id: unitID,
        changeset: {
            change: change,
            client: localStorage.getItem("email"),
            value: value
        }
    };

    try {
        const response = await fetch(`${apiUrl}/units`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`,
            },
            method: 'PUT',
            body: JSON.stringify(changeSet),
        });

        // Change the button and open text to the respective values after successful response
        if (response.ok) {
            openButton.innerText = (value === "false") ? 'Open' : 'Close';
            document.getElementById(`${unitID}-open-tag`).textContent = 
                "Open: " + ((value === "false") ? 'no' : 'yes');  
        } else {
            console.error('Error occurred opening/closing the unit');
        }
    } catch (err) {
        console.error(err);
    }

}


/**
 * Determine whether the unit is currently being shared or not
 * @param {json} shared 
 * @returns string
 */
function determineShared(shared) {
    if (!shared) {
        return "No";
    } else {
        return "with " + shared.shared_with;
    }
}

/**
 * Close the popup and reload unit details
 */
function closeModal(modal, form) {
    modal.style.display = 'none';
    if (form !== null) {
        form.reset();
    }
    unitDetailsBack();
}

/**
 * Send a PUT request to make changes to the unit
 * @param {element} modal 
 * @param {element} form 
 * @param {json} changeset 
 * @param {string} message 
 */
async function sendSpecialRequest(modal, form, changeset, message) {
    try {
        const response = await fetch(`${apiUrl}/units`, {
            method: 'PUT', 
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`,
            },
            body: JSON.stringify(changeset),
        });

        if (!response.ok) {
            alert(message)
        } else {
            closeModal(modal, form);
        }

    } catch (err) {
        console.error(err);
    }
}

/**
 * Functionality to allow the user to enter the email of the user they would like to share access to their unit with
 */
function shareAccess() {
    const shareModal = document.getElementById('shareAccessModal');
    const shareAccessForm = document.getElementById('shareAccessForm');
    shareModal.querySelector('.btn-close').addEventListener('click', () => closeModal(shareModal, shareAccessForm));

    shareModal.style.display = 'block';

    shareAccessForm.onsubmit = (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;

        const jsonChangeSet = {
            unit_id: unitId,
            changeset: {
                client: localStorage.getItem('email'),
                change: "shared",
                value: email
            }
        };

        sendSpecialRequest(shareModal, shareAccessForm, jsonChangeSet, "Error while trying to share access.")
    };
}



/**
 * Ensures user cannot extend the rental of an already indefinitely
 * booked unit.
 */
function showIndefinitePopup() {
    const modal = document.getElementById('indefinitePopup');
    const okBtn = document.getElementById('btn-okay');

    modal.style.display = 'block';

    okBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

/**
 * Extending the rental period of a unit.
 */
async function extendRental() {
    const extendModal = document.getElementById('extendRentalModal');
    const extendRentalForm = document.getElementById('extendRentalForm');
    extendModal.querySelector('.btn-close').addEventListener('click', () => closeModal(extendModal, extendRentalForm));
    
    if (unit.end_date === "indefinite") {
        showIndefinitePopup();
    } else {
        const endDateInput = document.getElementById('end-date');
        const formattedDate = new Date(unit.end_date).toISOString().split('T')[0];
        console.log(formattedDate);
        endDateInput.setAttribute('min', formattedDate);
        extendModal.style.display = 'block';

        extendRentalForm.onsubmit = (e) => {
            e.preventDefault();
            const endDate = endDateInput.value;

            const jsonChangeSet = {
                unit_id: unitId,
                changeset: {
                    client: localStorage.getItem('email'),
                    change: "end_date",
                    value: endDate
                }
            };

            sendSpecialRequest(extendModal, extendRentalForm, jsonChangeSet, "Error while trying to extend the rental.")
            
        }
    }
};

/**
 * Stopping the rental of a unit.
 */
function stopRental() {
    if (unit.state === "Cancelled") {
        alert("This unit is already cancelled. You cannot stop renting it.")
        return;
    }

    const stopRentingModal = document.getElementById("stopRentalModal");
    stopRentingModal.style.display = 'block';

    stopRentingModal.querySelector('.btn-close').addEventListener('click', () => {
        stopRentingModal.style.display = 'none';
    });

    stopRentingModal.querySelector('#btn-okay').addEventListener('click', () => {
        const jsonChangeSet = {
            unit_id: unitId,
            changeset: {
                change: "state",
                value: "cancelled"
            }
        };

        sendSpecialRequest(stopRentingModal, null, jsonChangeSet, "Error while trying to stop renting.")

        stopRentingModal.style.display = 'none';
    });

    stopRentingModal.querySelector('#btn-no').addEventListener('click', () => {
        stopRentingModal.style.display = 'none';
    });
}

/**
 * Stop sharing access with user(s) they are currently sharing their unit with
 */
function stopSharing() {
    const stopShareModal = document.getElementById("stopShareModal");
    const stopShareForm = document.getElementById("stopShareForm");
    stopShareModal.querySelector('.btn-close').addEventListener('click', () => closeModal(stopShareModal, stopShareForm));

    stopShareModal.style.display = 'block';
    populateStopShareModal();

    document.getElementById('submitStopShare').addEventListener('click', () => {
        const selectedUsers = Array.from(
            document.querySelectorAll('input[name="sharedUsers"]:checked')
        ).map(checkbox => checkbox.value);

        console.log(selectedUsers);

        const jsonChangeSet = {
            unit_id: unitId,
            changeset: {
                change: "stop_sharing",
                value: selectedUsers,
                client: localStorage.getItem('email')
            }
        };

        sendSpecialRequest(stopShareModal, stopShareForm, jsonChangeSet, `Failed to stop sharing the unit with ${selectedUsers}`);

        // closeModal(stopShareModal, stopShareForm);
    });
}

/**
 * Add the users that the unit is being shared with to the modal
 */
function populateStopShareModal() {
    const checkboxList = document.getElementById('userCheckboxList');
    checkboxList.innerHTML = '';

    const checkboxContainer = document.createElement('div');
    checkboxContainer.classList.add('checkbox-container');

    if (unit.shared === undefined) {
        const submitBut = document.getElementById('submitStopShare');
        submitBut.style.display = 'none';

        const notShared = document.createElement('p');
        notShared.innerText = "Not currently sharing this unit.";
        checkboxContainer.appendChild(notShared);
        checkboxList.appendChild(checkboxContainer);
    } else {
        users = unit.shared.shared_with;
        users.forEach(user => {
            const checkboxDiv = document.createElement('div');
            checkboxDiv.classList.add("checkbox");

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = user;
            checkbox.name = 'sharedUsers';
            checkbox.value = user;

            const label = document.createElement('label');
            label.htmlFor = `${user}`;
            label.textContent = user;

            checkboxDiv.appendChild(checkbox);
            checkboxDiv.appendChild(label);

            checkboxContainer.appendChild(checkboxDiv);
            
            checkboxList.appendChild(checkboxContainer);
        });
    }
}

/**
 * Allow the user to change their payment method
 */
function checkPayments() {
    const modal = document.getElementById("changePaymentModal");
    const form = document.getElementById('changePaymentForm');
    const cardPayment = document.getElementById("cardPayment");
    const eftPayment = document.getElementById('eftPayment');

    if (unit.unit_payment_type === 'card') {
        cardPayment.checked = true;
    } else if (unit.unit_payment_type === 'eft') {
        eftPayment.checked = true;
    }

    modal.style.display = 'block'

    modal.querySelector('.btn-close').addEventListener('click', () => closeModal(modal, form));

    form.onsubmit = (e) => {
        e.preventDefault();
        let paymentType;
        if (cardPayment.checked) {
            paymentType = "card";
        } else if (eftPayment.checked) {
            paymentType = "eft";
        }

        const jsonChangeSet = {
            unit_id: unitId,
            changeset: {
                client: localStorage.getItem('email'),
                change: "payment_type",
                value: paymentType
            }
        };

        sendSpecialRequest(modal, form, jsonChangeSet, "Error changing payment type.")
    }
}

/**
 * Redirect to the notifications page
 */
function loadNotifications() {
    localStorage.setItem("unit_id", unit.unit_id);
    window.location.href = "notifications.html";
}

/**
 * When the page is loaded show the loading icon and try to fetch the unit details
 */
window.onload = function () {
    displayLoading();
    fetchUnitDetails();
}
