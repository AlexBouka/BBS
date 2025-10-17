import { API, requireAdmin, addStop, removeStop } from "../api.js";

const routeId = window.location.pathname.split('/').pop();
let stopCounter = 0;

async function loadRouteData() {
    const loadingState = document.getElementById('loadingState');
    const form = document.getElementById('updateRouteForm');
    const errorMessage = document.getElementById('errorMessage');

    try {
        console.log(`Loading route: ${routeId}`);

        const route = await API.request(`/api/routes/${routeId}`, {
            method: 'GET'
        });

        console.log('Route loaded:', route);

        loadingState.style.display = 'none';
        form.style.display = 'block';

        // Prefill basic Information
        document.getElementById('routeId').value = route.id;
        document.getElementById('routeNumber').value = route.route_number;
        document.getElementById('routeName').value = route.route_name || '';

        // Prefill route details
        document.getElementById('originCity').value = route.origin_city;
        document.getElementById('destinationCity').value = route.destination_city;
        document.getElementById('distanceKm').value = route.distance_km;
        document.getElementById('durationMinutes').value = route.duration_minutes;
        document.getElementById('basePrice').value = route.base_price;

        // Prefill status
        document.getElementById('status').value = route.status;

        // Prefill checkboxes
        document.getElementById('isExpress').checked = route.is_express;
        document.getElementById('isOvernight').checked = route.is_overnight;
        document.getElementById('operatesDaily').checked = route.operates_daily;

        // Prefill operating days
        if (route.operates_daily && route.operating_days) {
            document.getElementById('operatingDaysSection').style.display = 'block';
            route.operating_days.forEach(day => {
                const checkbox = document.querySelector(`input[value="${day}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Prefill intermediate stops
        if (route.intermediate_stops && route.intermediate_stops.length > 0) {
            route.intermediate_stops.forEach(stop => {
                addStop(stop);
            });
        }

        // Prefill Additional Information
        document.getElementById('description').value = route.description || '';
        document.getElementById('notes').value = route.notes || '';
    } catch (error) {
        console.error('Error loading route:', error);
        loadingState.innerHTML = `
            <div class="form__error-message error-message">
                <p class="error-message__text">Error loading route: ${error.message}</p>
                <button class="error-message__back-btn" onclick="window.location.href='/routes'">
                    Back to Routes
                </button>
            </div>
        `;
    }
}

document.getElementById('addStopBtn').addEventListener('click', () => addStop());
const stopsContainer = document.getElementById('stopsContainer');
stopsContainer.addEventListener('click', (event) => {
    if (event.target.classList.contains('btn-remove-stop')) {
        const stopId = event.target.closest('.stop-item').dataset.stopId;
        removeStop(stopId);
    }
});

// Toggle operating days
document.getElementById('operatesDaily').addEventListener('change', (e) => {
    document.getElementById('operatingDaysSection').style.display = 
        e.target.checked ? 'none' : 'block';
});

// Handle form submission
const updateRouteForm = document.getElementById('updateRouteForm');
updateRouteForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const updateRouteBtn = document.getElementById('updateRouteBtn');
    const errorMessage = document.getElementById('errorMessage');

    updateRouteBtn.disabled = true;
    updateRouteBtn.textContent = 'Updating route...';
    errorMessage.style.display = 'none';

    try {
        // Collect stops
        const stops = [];
        document.querySelectorAll('.stop-item').forEach((item) => {
            const city = item.querySelector('.stop-city').value.trim();
            const duration = parseInt(item.querySelector('.stop-duration').value);
            const distance = parseInt(item.querySelector('.stop-distance').value);

            if (city && duration && distance) {
                stops.push({
                    city: city,
                    stop_duration_minutes: duration,
                    distance_from_origin_km: distance
                });
            }
        });

        // Collect operating days
        let operatingDays = null;
        if (!document.getElementById('operatesDaily').checked) {
            operatingDays = [];
            document.querySelectorAll('input[name="operatingDay"]:checked').forEach((checkbox) => {
                operatingDays.push(checkbox.value);
            });
        }

        // Build update data
        const routeData = {
            route_number: document.getElementById('routeNumber').value.trim(),
            route_name: document.getElementById('routeName').value.trim() || null,
            origin_city: document.getElementById('originCity').value.trim(),
            destination_city: document.getElementById('destinationCity').value.trim(),
            distance_km: parseFloat(document.getElementById('distanceKm').value),
            duration_minutes: parseInt(document.getElementById('durationMinutes').value),
            base_price: parseFloat(document.getElementById('basePrice').value),
            intermediate_stops: stops.length > 0 ? stops : null,
            is_express: document.getElementById('isExpress').checked,
            is_overnight: document.getElementById('isOvernight').checked,
            operates_daily: document.getElementById('operatesDaily').checked,
            operating_days: operatingDays,
            description: document.getElementById('description').value.trim() || null,
            notes: document.getElementById('notes').value.trim() || null,
            status: document.getElementById('status').value
        };

        // Call API
        const response = await API.request(`/api/routes/${routeId}`, {
            method: 'PUT',
            body: JSON.stringify(routeData)
        });

        alert('Route updated successfully!');
        window.location.href = '/routes';
    } catch (error) {
        console.error('Error updating route:', error);
        errorMessage.textContent = error.message || 'Error updating route';
        errorMessage.style.display = 'block';
    } finally {
        // Reset button state
        updateRouteBtn.disabled = false;
        updateRouteBtn.textContent = 'Update Route';
    }
});

window.addEventListener('DOMContentLoaded', async () => {
    await requireAdmin('/routes'); // redirect non-admin users to /routes
    await loadRouteData();
});
