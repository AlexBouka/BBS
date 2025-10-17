import { TokenManager, API, requireAuth } from "../api.js";

// Load user data dynamically (Javascript + API)
async function loadUserData() {
    try {
        const result = await API.getCurrentUser();
        console.log(result.success)
        console.log(result.data)

        if (result.success) {
            const user = result.data;
            const userInfo = document.getElementById('userInfo');
            userInfo.textContent = `${user.first_name || ''} ${user.last_name || ''} | ${user.username} (${user.role})`;

            const userDetails = document.getElementById('userDetails');
            userDetails.innerHTML = `
                <div class="user-card">
                    <h3>Account Information</h3>
                    <p>Username: ${user.username}</p>
                    <p>Email: ${user.email}</p>
                    <p>Full Name: ${user.first_name} ${user.last_name}</p>
                    <p>Role: ${user.role}</p>
                    <p>Account Status: ${user.is_active ? 'Active' : 'Inactive'}</p>
                    <p>Member Since: ${new Date(user.created_at).toLocaleDateString()}</p>
                </div>
            `;
        } else {
            TokenManager.clearTokens();
            window.location.href = '/auth/login';
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        TokenManager.clearTokens();
        window.location.href = '/auth/login';
    }
}

// JavaScript powered functions
async function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        await API.logout();
    }
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Require authentication
    requireAuth();
    loadUserData();
});
