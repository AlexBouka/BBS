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
            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
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
            const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
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

    // Register new admin
    async registerAdmin(adminData) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/register/admin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(adminData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Admin registration failed');
            }

            const data = await response.json();
            return {success: true, data};
        } catch (error) {
            console.error('Admin registration error:', error);
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

            const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
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
            const data = await this.request('/api/auth/me', {method: 'GET'});
            return {success: true, data};
        } catch (error) {
            return {success: false, error: error.message};
        }
    },

    // Logout user
    async logout() {
        try {
            // Call logout endpoint
            await this.request('/api/auth/logout', {method: 'POST'});

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


/**
 * Check if user is authenticated. If not authenticated, redirect to login page.
 * This function should be called at the beginning of a page to ensure that only authenticated users can access the page.
 */
function requireAuth() {
    if (!TokenManager.isLoggedIn()) {
        console.log('Not authenticated, redirecting to login page...');
        window.location.href = '/auth/login';
    }
}

/**
 * Check if user is authenticated and is admin. If not authenticated, redirect to login page.
 * If authenticated but not an admin, redirect to routes page and display an access denied alert.
 * If the API call to get the current user fails, clear tokens and redirect to login page.
 */
async function requireAdmin(path) {
    if (!TokenManager.isLoggedIn()) {
        console.log('Not authenticated, redirecting to login page...');
        window.location.href = '/auth/login';
        return;
    }

    // Check if user is admin by fetching current user
    const result = await API.getCurrentUser();
    if (result.success && result.data.role === 'ADMIN') {
        return;
    } else {
        console.log('User is not admin, redirecting...');
        alert('Access denied. Admin Priviliges required.');
        window.location.href = path;
        return;
    }
    // API.getCurrentUser().then(result => {
    //     if (result.success && result.data.role) {
    //         if (result.data.role !== 'admin') {
    //             console.log('User is not admin, redirecting to rotes page...');
    //             alert('Access denied. Admin Priviliges required.');
    //             window.location.href = path;
    //         }
    //     } else {
    //         TokenManager.clearTokens();
    //         window.location.href = '/auth/login';
    //     }
    // }).catch(() => {
    //     TokenManager.clearTokens();
    //     window.location.href = '/auth/login';
    // });
}


/**
 * Redirect to main page if already authenticated.
 * This function checks if the user is already authenticated using the TokenManager.
 * If authenticated, it redirects the user to the main page.
 * This function is useful to prevent authenticated users from accessing login pages.
 */
function redirectIfAuthenticated() {
    if (TokenManager.isLoggedIn()) {
        console.log('Already authenticated, redirecting to main page...');
        window.location.href = '/auth/dashboard';
    }
}


/**
 * Adds a new intermediate stop to the page.
 * If stopData is provided, it will fill in the city, duration, and distance fields.
 * Otherwise, it will leave the fields blank.
 * @param {Object} stopData - Optional object with city, stop_duration_minutes, and distance_from_origin_km properties.
 */
function addStop(stopData = null) {
    const stopsContainer = document.getElementById('stopsContainer');
    const currentStops = stopsContainer.querySelectorAll('.stop-item');
    const stopNumber = currentStops.length + 1;
    
    const city = stopData?.city || '';
    const duration = stopData?.stop_duration_minutes || '';
    const distance = stopData?.distance_from_origin_km || '';
    
    const stopHtml = `
        <div class="stop-item" data-stop-id="${stopNumber}">
            <div class="stop-header">
                <h4>Stop ${stopNumber}</h4>
                <button type="button" class="btn-remove-stop">
                    Remove
                </button>
            </div>
            <div class="form-section__form-row form-row">
                <div class="form-row__form-group form-group">
                    <label>City</label>
                    <input type="text" class="stop-city" value="${city}" required>
                </div>
                <div class="form-row__form-group form-group">
                    <label>Stop Duration (minutes)</label>
                    <input type="number" class="stop-duration" value="${duration}" required min="1">
                </div>
                <div class="form-row__form-group form-group">
                    <label>Distance from Origin (km)</label>
                    <input type="number" class="stop-distance" value="${distance}" required min="0" step="0.1">
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('stopsContainer').insertAdjacentHTML('beforeend', stopHtml);
}


/**
 * Removes a stop item from the DOM and renumbers the remaining stops.
 * @param {string} stopId - The ID of the stop item to be removed.
 */
function removeStop(stopId) {
    const stopElement = document.querySelector(`[data-stop-id="${stopId}"]`);
    if (stopElement) {
        stopElement.remove();

        // Renumber remaining stops
        const remainingStops = document.querySelectorAll('.stop-item');
        remainingStops.forEach((stop, index) => {
            const header = stop.querySelector('.stop-header h4');
            header.textContent = `Stop ${index + 1}`;
        });
    }
}


/**
 * Checks if the user is authenticated and is an admin, and
 * activates or deactivates a button accordingly.
 *
 * @param {string} buttonId - The ID of the button to activate or deactivate.
 * @returns {Promise<void>} - Resolves when the button has been activated or deactivated.
 */
async function checkAdminStatusForBtnActivation(buttonId) {
    const button = document.getElementById(buttonId);
    if (!TokenManager.isLoggedIn()) {
        if (button) button.style.display = "none";
        return;
    }

    const result = await API.getCurrentUser();
    if (result.success && result.data.role === "ADMIN") {
        if (button) button.style.display = "block";
    } else {
        if (button) button.style.display = "none";
    }
}


async function isUserAdmin() {
    if (!TokenManager.isLoggedIn()) return false;

    const result = await API.getCurrentUser();
    return result.success && result.data.role === "ADMIN";
}


/**
 * Retrieves a route by its ID.
 *
 * @param {string} routeId - The ID of the route to retrieve.
 * @returns {Promise<object>} - The retrieved route.
 */

async function getRoute(routeId) {
    response = await fetch(`${API_BASE_URL}/api/routes/${routeId}`);
    data = await response.json();
    return data;
}

// Export for use in other files
// Note: In browser, these are available globally:
// window.API = API;
// window.TokenManager = TokenManager;
// window.requireAuth = requireAuth;
// window.requireAdmin = requireAdmin;
// window.redirectIfAuthenticated = redirectIfAuthenticated;

export { 
    API, API_BASE_URL, TokenManager, requireAuth, requireAdmin, isUserAdmin,
    redirectIfAuthenticated, checkAdminStatusForBtnActivation, addStop, removeStop, getRoute };