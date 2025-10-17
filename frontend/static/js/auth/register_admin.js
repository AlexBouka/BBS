import { API, requireAdmin } from "../api.js";

// Require authentication
requireAdmin();

document.getElementById('registerAdminBtn').addEventListener('submit', async (event) => {
    event.preventDefault();

    const registerAdminBtn = document.getElementById('registerAdminBtn');
    const errorMessage = document.getElementById('errorMessage');

    // Get form values
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('passwordConfirm').value;
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const phoneNumber = document.getElementById('phoneNumber').value.trim();

    // Validate passwords match
    if (password !== passwordConfirm) {
        errorMessage.textContent = 'Passwords do not match';
        errorMessage.style.display = 'block';
        return;
    }

    // Build admin data object
    const adminData = {
        username: username,
        email: email,
        password: password
    };

    // Add optional fields only if they have values
    if (firstName) adminData.first_name = firstName;
    if (lastName) adminData.last_name = lastName;
    if (phoneNumber) adminData.phone_number = phoneNumber;

    console.log('Registering Admin');

    // Show loading state
    registerAdminBtn.disabled = true;
    registerAdminBtn.textContent = 'Creating account...';
    errorMessage.style.display = 'none';

    try {
        const result = await API.registerAdmin(adminData);

        if (result.success) {
            alert('Admin account created successfully! Please login.');
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
        registerAdminBtn.disabled = false;
        registerAdminBtn.textContent = 'Create Admin Account';
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    await requireAdmin('/auth/dashboard'); // redirect non-admin users to /routes
});
