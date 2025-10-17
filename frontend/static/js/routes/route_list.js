import { API, API_BASE_URL, checkAdminStatusForBtnActivation } from "../api.js";

// Pagination state
let currentPage = 1;
const pageSize = 10;
let totalRoutes = 0;
let currentFilters = {};

// Check if user is admin for create route button activation
checkAdminStatusForBtnActivation('createRouteBtn');

async function loadRoutes(page = 1) {
    const loadingState = document.getElementById('loadingState');
    const routesContainer = document.getElementById('routesContainer');
    const noResults = document.getElementById('noResults');
    const paginationContainer = document.getElementById('paginationContainer');

    loadingState.style.display = 'block';
    routesContainer.innerHTML = '';
    noResults.style.display = 'none';
    paginationContainer.innerHTML = '';

    try {
        const offset = (page - 1) * pageSize;
        const limit = pageSize;

        // Build query params
        const params = new URLSearchParams({
            offset: offset,
            limit: limit
        });

        // Add filters if present
        if (currentFilters.origin) {
            params.append('origin_city', currentFilters.origin);
        }
        if (currentFilters.destination) {
            params.append('destination_city', currentFilters.destination);
        }
        if (currentFilters.status) {
            params.append('status', currentFilters.status);
        }

        const response = await fetch(`${API_BASE_URL}/api/routes?${params.toString()}`);
        if (!response.ok) {
            throw new Error('Failed to fetch routes');
        }

        const routes = await response.json();
        loadingState.style.display = 'none';

        if (routes.length === 0) {
            noResults.style.display = 'block';
            return;
        }

        routes.forEach(route => {
            routesContainer.appendChild(createRouteCard(route));
        });

        currentPage = page;
        renderPagination(routes.length === pageSize);

    } catch (error) {
        console.error('Error loading routes:', error);
        loadingState.style.display = 'none';
        noResults.innerHTML = '<p>Error loading routes. Please try again.</p>';
        noResults.style.display = 'block';
    }
}

// Create route card element
function createRouteCard(route) {
    const card = document.createElement('div');
    card.className = 'route-card';

    let statusBadge = `<span class="badge badge-status-${route.status}">${route.status.toUpperCase()}</span>`;
    let badges = statusBadge;

    if (route.is_express) {
        badges += `<span class="badge badge-express">EXPRESS</span>`;
    }
    if (route.is_overnight) {
        badges += `<span class="badge badge-overnight">OVERNIGHT</span>`;
    }
    
    card.innerHTML = `
            <div class="route-header">
                <div class="route-title">
                    <div class="route-number">${route.route_number}</div>
                    <h3>${route.full_route_name}</h3>
                    <div class="route-path">
                        ${route.origin_city} 
                        <span class="arrow">→</span> 
                        ${route.destination_city}
                    </div>
                </div>
                <div class="route-badges">
                    ${badges}
                </div>
            </div>
            
            <div class="route-details">
                <div class="route-detail-item">
                    <span class="label">Distance</span>
                    <span class="value">${route.distance_km} km</span>
                </div>
                <div class="route-detail-item">
                    <span class="label">Duration</span>
                    <span class="value">${route.estimated_duration_hours} hrs</span>
                </div>
                <div class="route-detail-item">
                    <span class="label">Price</span>
                    <span class="value">$${route.base_price.toFixed(2)}</span>
                </div>
            </div>
            
            <div class="route-actions">
                <button id="viewRouteBtn" class="view-route-btn" data-route-id="${route.id}">
                    View Details
                </button>
                <button class="btn btn-primary btn-small" onclick="bookRoute('${route.id}')">
                    Book Now
                </button>
            </div>
        `;

    return card;
}

function renderPagination(hasMore) {
    const container = document.getElementById('paginationContainer');
    const startItem = (currentPage - 1) * pageSize + 1;
    const endItem = startItem + pageSize - 1;

    container.innerHTML = `
            <button 
                class="pagination-btn" 
                ${currentPage === 1 ? 'disabled' : ''}
                onclick="loadRoutes(${currentPage - 1})"
            >
                ← Previous
            </button>
            
            <span class="pagination-info">
                Page ${currentPage} | Showing ${startItem}-${endItem}
            </span>
            
            <button 
                class="pagination-btn" 
                ${!hasMore ? 'disabled' : ''}
                onclick="loadRoutes(${currentPage + 1})"
            >
                Next →
            </button>
        `;
}

function applyFilters() {
    currentFilters = {
        origin: document.getElementById('filterOriginCity').value.trim(),
        destination: document.getElementById('filterDestinationCity').value.trim(),
        status: document.getElementById('filterStatus').value
    };
    
    loadRoutes(1);
}

function clearFilters() {
    document.getElementById('filterOriginCity').value = '';
    document.getElementById('filterDestinationCity').value = '';
    document.getElementById('filterStatus').value = '';
    currentFilters = {};
    loadRoutes(1);
}

function viewRoute(routeId) {
    window.location.href = `/routes/${routeId}`;
}

const routesContainer = document.getElementById('routesContainer');

routesContainer.addEventListener('click', (event) => {
    if (event.target.classList.contains('view-route-btn')) {
        const routeId = event.target.dataset.routeId;
        viewRoute(routeId);
    }
})

window.addEventListener('DOMContentLoaded', () => {
    loadRoutes(1);

    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    document.getElementById('clearFiltersBtn').addEventListener('click', clearFilters);
});
