const apiUrl = "https://cezl7l5gpk.execute-api.eu-west-1.amazonaws.com/Prod";

// Fetch all units
async function fetchAllUnits() {
    const idToken = localStorage.getItem('idToken');
    if (!idToken) {
        redirectToLogin("You need to log in to fetch all units.");
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/units?type=admin`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${idToken}`,
            },
        });

        if (response.status === 401) {
            redirectToLogin("You are unauthorized. Please log in.");
        } else if (!response.ok) {
            throw new Error(`Failed to fetch units: ${response.status}`);
        }

        const allUnits = await response.json();
        hideLoading();
        populateUnitsTable(allUnits.units); // Assuming API returns an array in `units`
    } catch (error) {
        console.error('Error fetching all units:', error);
        redirectToLogin("An error occurred. Please try logging in again.");
    }
}

// Populate the units table
function populateUnitsTable(units) {
    const tableBody = document.querySelector('#units-table tbody');
    tableBody.innerHTML = ''; // Clear any existing rows

    units.forEach(unit => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${unit.unit_id}</td>
            <td>${unit.location}</td>
            <td>${unit.size}</td>
            <td>${unit.status}</td>
            <td>R${unit.accrued_cost}</td>
            <td>${determineShared(unit.shared)}</td>
            <td>${unit.open === 'false' ? 'No' : 'Yes'}</td>
            <td>${unit.end_date === 'indefinite' ? 'Never' : unit.end_date}</td>
            <td>
                <button class="btn-secondary" id="${unit.unit_id}-open">
                    ${unit.open === 'false' ? 'Open' : 'Close'}
                </button>
            </td>
        `;

        // Add functionality to the Open/Close button
        const openButton = row.querySelector(`#${unit.unit_id}-open`);
        openButton.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = openButton.innerText === 'Open' ? 'true' : 'false';
            sendRequest(unit.unit_id, 'open', action, openButton);
        });

        tableBody.appendChild(row);
    });
}

// Determine shared status
function determineShared(shared) {
    return shared && shared.length > 0 
        ? `Shared with: ${shared.join(', ')}` 
        : 'Not Shared';
}


function hideLoading() {
    document.querySelector('.loading-screen').style.display = 'none';
    document.querySelector('.container').style.display = 'block';
}

// // Example usage on page load
// window.onload = function () {
//     displayLoading();
//     fetchAllUnits();
// };

// // Mock display loading
// function displayLoading() {
//     document.querySelector('.loading-screen').style.display = 'flex';
//     document.querySelector('.container').style.display = 'none';
// }
