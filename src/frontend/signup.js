const apiUrl = "https://cezl7l5gpk.execute-api.eu-west-1.amazonaws.com/Prod/create_user";

const signupForm = document.getElementById('signupForm');

/**
 * Sends a POST request to register a user
 * Handles the retrieving of values and verifies those values before sending
 */
async function signUp() {
    const name = document.getElementById('name').value;
    const surname = document.getElementById('surname').value;
    const email = document.getElementById('email').value;
    const location = document.getElementById('location').value;

    const password1 = document.getElementById('password').value;
    const password2 = document.getElementById('confirm-password').value;
    const errorMessage = document.getElementById('error-message');

    const countryCode = document.getElementById('country-code').value;
    const phoneNumber = document.getElementById('phone').value.replace(/\s+/g, '');
    const phonePattern = /^\d{6,14}$/;

    errorMessage.style.display = 'none';
    errorMessage.textContent = '';

    if (!phonePattern.test(phoneNumber)) {
        errorMessage.textContent = 'Please enter a valid phone number.'
        errorMessage.style.display = 'block';
        return;
    }

    if (password1 !== password2) {
        errorMessage.textContent = 'Passwords do not match.';
        errorMessage.style.display = 'block';
        return;
    }

    const fullNumber = `${countryCode} ${phoneNumber}`;

    const registrationDetails = {
        name: name,
        surname: surname,
        email: email,
        phone_number: fullNumber,
        location: location,
        password: password1
    };

    console.log(registrationDetails);

    try {
        const response = await fetch(apiUrl, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify(registrationDetails),
        });

        if (response.ok) {
            window.location.href = "login.html";
        } else {
            const errorData = await response.json();
            const errorMessageText = errorData.Message || 'An unexpected error occurred.';

            errorMessage.textContent = errorMessageText;
            errorMessage.style.display = 'block';
        }
    } catch (err) {
        errorMessage.textContent = err;
        errorMessage.style.display = 'block';
    }
}

/**
 * Allow users to press enter to submit the form
 */
signupForm.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        signUp();
    }
})

/**
 * Event listener for the submit button
 */
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    signUp();
});

/**
 * Functionality for showing and hiding the entered password when the eye icon is clicked
 */
document.getElementById('toggle-password').addEventListener('click', function () {
    const passwordInput = document.getElementById('password');
    const icon = this;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.setAttribute('name', 'eye');
    } else {
        passwordInput.type = 'password';
        icon.setAttribute('name', 'eye-off');
    }
});

/**
 * Functionality for showing and hiding the entered repeat password when the eye icon is clicked
 */
document.getElementById('toggle-confirm-password').addEventListener('click', function () {
    const confirmPasswordInput = document.getElementById('confirm-password');
    const icon = this;

    if (confirmPasswordInput.type === 'password') {
        confirmPasswordInput.type = 'text';
        icon.setAttribute('name', 'eye');
    } else {
        confirmPasswordInput.type = 'password';
        icon.setAttribute('name', 'eye-off');
    }
});