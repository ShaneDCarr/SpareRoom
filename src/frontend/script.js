/**
 * Method that handles the showing/removing of the navabar items
 * called on clicking the hamburger menu.
 */
function toggleMenu() {
    const menu = document.getElementById('menu');
    if (menu.classList.contains('show')) {
        menu.classList.remove('show');
    } else {
        menu.classList.add('show')
    }
}

/**
 * EventListener for logging out
 */
document.getElementById('logout-link').addEventListener('click', (e) => {
    localStorage.clear();

    e.preventDefault();
    window.location.href = "login.html";
})