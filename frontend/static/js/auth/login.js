import { API, redirectIfAuthenticated } from "../api.js";

// Check if already logged in (Javascript)
redirectIfAuthenticated();

// JavaScript to handle form submission and error handling
document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const loginBtn = document.getElementById('loginBtn');
    const usernameOrEmail = document.getElementById('usernameOrEmail').value;
    const password = document.getElementById('password').value;

    // Show loading state
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';

    // This calls POST /auth/login endpoint
    const result = await API.login(usernameOrEmail, password);

    if (result.success) {
        window.location.href = '/auth/dashboard';
    } else {
        document.getElementById('errorMessage').textContent = result.error;
        document.getElementById('errorMessage').style.display = 'block';
        loginBtn.disabled = false;
        loginBtn.textContent = 'Login';
    }
});
