import { API, getRoute, isUserAdmin } from "../api";


async function loadRouteData() {
    const routeId = window.location.pathname.split('/').pop();
    try {
        const route = await getRoute(routeId);
        const isAdmin = await isUserAdmin();

        const loadingText = document.getElementById('loadingText');
        loadingText.style.display = 'none';
        const routeContainer = document.getElementById('routeContainer');
        routeContainer.innerHTML = `
            <h2>${route.route_number} - ${route.route_name}</h2>
            <div class="route-info">
                <p class="route-info__text">From: ${route.origin_city}</p>
                <p class="route-info__text">To: ${route.destination_city}</p>
                <p class="route-info__text">Distance: ${route.distance_km} km</p>
                <p class="route-info__text">Duration: ${route.estimated_duration_hours} hours</p>
                <p class="route-info__text">Stops: ${route.total_stops}</p>
                <p class="route-info__text">Base Price: ${route.base_price}</p>
            </div>
            <div class="route-info">
                <p class="route-info__text">Express: ${route.is_express ? 'Yes' : 'No'}</p>
                <p class="route-info__text">Overnight: ${route.is_overnight ? 'Yes' : 'No'}</p>
                <p class="route-info__text">Operates Daily: ${route.operates_daily ? 'Yes' : 'No'}</p>
                <p class="route-info__text">Operating Days: ${route.operating_days.join(', ')}</p>
            </div>
            <div class="route-info">
                <p class="route-info__text">Description: ${route.description || 'N/A'}</p>
                <p class="route-info__text">Notes: ${route.notes || 'N/A'}</p>
                <p class="route-info__text">Status: ${route.status}</p>
            </div>
            ${
                isAdmin
                    ? `
                    <div class="route-actions">
                        <button id="updateBtn" class="route-actions__btn-update">Update</button>
                        <button id="deleteBtn" class="route-actions__btn-delete">Delete</button>
                    </div>`
                    : ''
            }
        `;
    } catch (error) {
        console.error('Error fetching route data:', error);
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = error.message || 'Error fetching route data';
        errorMessage.style.display = 'block';
    }
}

async function handleUpdate() {
    const routeId = window.location.pathname.split('/').pop();
    window.location.href = `/routes/update/${routeId}`;
}

async function handleDelete() {
    const routeId = window.location.pathname.split('/').pop();
    const confirmed = confirm('Are you sure you want to delete this route?');
    if (confirmed) {
        try {
            await API.request(`/api/routes/${routeId}`, { method: 'DELETE' });
            alert('Route deleted successfully!');
            window.location.href = '/routes';
        } catch (error) {
            console.error('Error deleting route:', error);
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.textContent = error.message || 'Error deleting route';
            errorMessage.style.display = 'block';
        }
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    await loadRouteData();

    const updateBtn = document.getElementById('updateBtn');
    const deleteBtn = document.getElementById('deleteBtn');

    if (updateBtn) {
        updateBtn.addEventListener('click', async () => {
            await handleUpdate();
        });
    }

    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            await handleDelete();
        });
    }
});
