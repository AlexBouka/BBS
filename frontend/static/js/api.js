// api.js - Core API communication with automatic token refresh

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Token Management
const TokenManager = {
    // Get access token from localStorage
    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    // Get refresh token from localStorage
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    // Save tokens to localStorage
    saveTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        console.log('Tokens saved successfully');
    },

    // Clear all tokens (logout)
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        console.log('Tokens cleared successfully');
    },

    // Check if user is logged in
    isLoggedIn() {
        return this.getAccessToken() !== null;
    }
};

// API client with automatic token refresh
const API = {
    // Login user
    async login(usernameOrEmail, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username_or_email: usernameOrEmail,
                    password: password
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();

            // Save tokens
            TokenManager.saveTokens(data.access_token, data.refresh_token);

            return {success: true, data};
        } catch (error) {
            console.error('Login error:', error);
            return {success: false, error: error.message};
        }
    },

    // Register new user
    async register(userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }

            const data = await response.json();
            return {success: true, data};
        } catch (error) {
            console.error('Registration error:', error);
            return {success: false, error: error.message};
        }
    },

    // Refresh access token
    async refreshToken() {
        try {
            const refreshToken = TokenManager.getRefreshToken();

            if (!refreshToken) {
                throw new Error('No refresh token available');
            }

            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({refresh_token: refreshToken})
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();

            // Save new tokens
            TokenManager.saveTokens(data.access_token, data.refresh_token);
            console.log('Token refreshed successfully');

            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            // Clear tokens and redirect to login
            TokenManager.clearTokens();
            window.location.href = '/auth/login';
            return false;
        }
    },

    // Make authenticated API request with automatic token refresh
    async request(endpoint, options = {}) {
        const accessToken = TokenManager.getAccessToken();

        if (!accessToken) {
            throw new Error('Not authenticated');
        }

        // Add authorization header
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`
        };

        try {
            // Make request
            let response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers
            });

            // If 401, try to refresh token and retry
            if (response.status === 401) {
                console.log('Access token expired, refreshing...');

                const refreshed = await this.refreshToken();

                if (refreshed) {
                    // Retry request with new token
                    const newAccessToken = TokenManager.getAccessToken();
                    headers['Authorization'] = `Bearer ${newAccessToken}`;

                    response = await fetch(`${API_BASE_URL}${endpoint}`, {
                        ...options,
                        headers
                    });
                } else {
                    throw new Error('Session expired. Please login again.');
                }
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();

        } catch (error) {
            console.log('API request error:', error);
            throw error;
        }
    },

    // Get current user info
    async getCurrentUser() {
        try {
            const data = await this.request('/auth/me', {method: 'GET'});
            return {success: true, data};
        } catch (error) {
            return {success: false, error: error.message};
        }
    },

    // Logout user
    async logout() {
        try {
            // Call logout endpoint
            await this.request('/auth/logout', {method: 'POST'});

            // Clear tokens
            TokenManager.clearTokens();

            // Redirect to login page
            window.location.href = '/auth/login';

            return {success: true};
        } catch (error) {
            // Even if API call fails, clear tokens and redirect to login page
            TokenManager.clearTokens();
            window.location.href = '/auth/login';
            return {success: false, error: error.message};
        }
    }
};

// Check authentication on protected pages
function requireAuth() {
    if (!TokenManager.isLoggedIn()) {
        console.log('Not authenticated, redirecting to login page...');
        window.location.href = '/auth/login';
    }
}

// Redirect to dashboard if already logged in (for login/ register pages)
function redirectIfAuthenticated() {
    if (TokenManager.isLoggedIn()) {
        console.log('Already authenticated, redirecting to main page...');
        window.location.href = '/auth/dashboard';
    }
}

// Export for use in other files
// Note: In browser, these are available globally:
window.API = API;
window.TokenManager = TokenManager;
window.requireAuth = requireAuth;
window.redirectIfAuthenticated = redirectIfAuthenticated;