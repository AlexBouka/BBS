import { API, redirectIfAuthenticated } from "../api.js";

// Check if already logged in
redirectIfAuthenticated();

// Password validation (real-time)
const form = document.getElementById('registerForm');
const registerBtn = document.getElementById('registerBtn');
const errorMessage = document.getElementById('errorMessage');

document.getElementById('password').addEventListener('input', (event) => {
    const password = event.target.value;
    const feedback = [];

    if (password.length < 8) feedback.push('Password must be at least 8 characters long');
    if (!/[A-Z]/.test(password)) feedback.push('Password must contain at least one uppercase letter');
    if (!/[a-z]/.test(password)) feedback.push('Password must contain at least one lowercase letter');
    if (!/\d/.test(password)) feedback.push('Password must contain at least one digit');

    if (feedback.length > 0) {
        errorMessage.textContent = feedback.join(', ');
        errorMessage.style.display = 'block';
    } else {
        errorMessage.style.display = 'none';
    }
});

// JavaScript to handle form submission and error handling
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Collect form data
    const formData = {
        username: document.getElementById('username').value.trim(),
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
        first_name: document.getElementById('firstName').value.trim() || undefined,
        last_name: document.getElementById('lastName').value.trim() || undefined,
        phone_number: document.getElementById('phoneNumber').value.trim() || undefined
    };

    // Validate passwords match
    const confirmPassword = document.getElementById('confirmPassword').value;
    if (formData.password !== confirmPassword) {
        errorMessage.textContent = 'Passwords do not match';
        errorMessage.style.display = 'block';
        return;
    }

    // Clean up undefined values
    Object.keys(formData).forEach(key => {
        if (formData[key] === undefined) delete formData[key];
    });

    // Show loading state
    registerBtn.disabled = true;
    registerBtn.textContent = 'Creating account...';
    errorMessage.style.display = 'none';

    // Call POST /auth/register endpoint
    try {
        const result = await API.register(formData);

        if (result.success) {
            alert('Account created successfully! Please login.');
            window.location.href = '/auth/login';
        } else {
            errorMessage.textContent = result.error;
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        errorMessage.textContent = 'Network error. Please try again.';
        errorMessage.style.display = 'block';
    } finally {
        // Reset button state
        registerBtn.disabled = false;
        registerBtn.textContent = 'Register';
    }
});
