const poolData = {
    UserPoolId: "eu-west-1_sh2aqkrbu",
    ClientId: "78vdtfkfdaos79d19pakrclkac"
};

const loginForm = document.getElementById('loginForm');
const errorMessage = document.getElementById('error-message');
const loadingScreen = document.querySelector('.loading-screen');
const loginContainer = document.getElementById('login-container');

/**
 * Display the loading icon while waiting for api response
 */
function displayLoading() {
    loginContainer.style.display = 'none';
    loadingScreen.style.display = 'flex';
}

/**
 * Hide the loading icon so that data can be shown
 */
function hideLoading() {
    loadingScreen.style.display = 'none';
    loginContainer.style.display = 'block';
}

/**
 * Show an error message when something goes wrong
 * @param {string} message 
 */
function displayError(message) {
    errorMessage.textContent = message || 'An unexpected error occurred. Please try again or sign up.';
    errorMessage.style.display = 'block';
};

/**
 * Remove the error message
 */
function removeError() {
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
};

/**
 * Login functionality to authenticate the user
 */
function login() {
    const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
    const emailValue = document.getElementById('email').value;
    const passwordValue = document.getElementById('password').value;
    displayLoading();
    
    removeError();

    const authenticationData = {
        Username: emailValue,
        Password: passwordValue,
    };

    const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);

    const userData = {
        Username: emailValue,
        Pool: userPool,
    };

    const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result) => {
            localStorage.setItem('idToken', result.getIdToken().getJwtToken())
            localStorage.setItem('email', emailValue);
            console.log('ID Token stored');
            window.location.href = "home.html";
        },
        onFailure: (err) => {
            hideLoading();
            displayError(err.message);
        },
    });
};

/**
 * Allow for the enter key to submit the form
 */
loginForm.addEventListener('keydown', (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        login();
    }
});

/**
 * Submit button event listener
 */
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    login();
});

/**
 * Showing or hiding password when the eye icon is clicked
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
 * If there is a login error in local storage then the user has been redirected due to an error
 */
window.onload = function () {
    const loginError = localStorage.getItem('loginError');
    if (loginError) {
        displayError(loginError);
        localStorage.removeItem('loginError');
    }
};
