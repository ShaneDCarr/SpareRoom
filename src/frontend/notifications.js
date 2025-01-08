const apiUrl = "https://cezl7l5gpk.execute-api.eu-west-1.amazonaws.com/Prod";
const notificationsList = document.getElementById('notifications');

/**
 * Go back to the last page in history
 */
function goBack() {
    window.history.back();
}

/**
 * Send a GET request to fetch all the notifications for the unit
 * Will be opening or closing actions
 */
async function fetchNotifications() {
    notificationsList.innerHTML = "";
    const unitId = localStorage.getItem("unit_id");
    try {
        const response = await fetch(`${apiUrl}/notifications?unit_id=${unitId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('idToken')}`,
            },
        });

        if (!response.ok) {
            throw new Error(response.status);
        }

        const notifications = await response.json();

        if (notifications.length === 0) {
            const listItem = document.createElement('li');
            listItem.style.listStyle = 'none';
            listItem.textContent = "No notifications to display."
            notificationsList.appendChild(listItem);
        } else {
            notifications.forEach(element => {
                const listItem = document.createElement('li');
                listItem.textContent = `${element.time}: ${element.user} ${element.action}`;
                notificationsList.appendChild(listItem);
            });
        }
        
    } catch (err) {
        console.error('Error fetching client notifications: ', err);
    }
}

fetchNotifications();