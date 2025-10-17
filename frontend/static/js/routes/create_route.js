import { API, requireAdmin } from "../api.js";

let stopCounter = 0;

// Add Intermediate Stop
const addStopBtn = document.getElementById('addStopBtn');
addStopBtn.addEventListener('click', () => {
    stopCounter++;
    const stopHtml = `
        <div class="stop-item" data-stop-id="${stopCounter}">
            <div class="stop-header">
                <h4 class=stop-item__title>Stop ${stopCounter}</h4>
                <button type="button" class="btn-remove-stop" onclick="removeStop(${stopCounter})">
                    Remove
                </button>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>City</label>
                    <input type="text" class="stop-city" required placeholder="Enter city or stop name">
                </div>
                <div class="form-group">
                    <label>Stop Duration (minutes)</label>
                    <input type="number" class="stop-duration" required min="1" placeholder="e.g., 15">
                </div>
                <div class="form-group">
                    <label>Distance from Origin (km)</label>
                    <input type="number" class="stop-distance" required min="0" step="1" placeholder="e.g., 85">
                </div>
            </div>
        </div>
    `;

    const stopsContainer = document.getElementById('stopsContainer');
    stopsContainer.insertAdjacentHTML('beforeend', stopHtml);
});

// Remove Intermediate Stop
window.removeStop = function(stopId) {
    const stopItem = document.querySelector(`[data-stop-id="${stopId}"]`);
    if (stopItem) {
        stopItem.remove();

        // Renumber remaining stops
        const remainingStops = document.querySelectorAll('.stop-item');
        remainingStops.forEach((stop, index) => {
            const header = stop.querySelector('.stop-header h4');
            header.textContent = `Stop ${index + 1}`;
        });
    }
};

// Toggle Operating days section
const operatesDaily = document.getElementById('operatesDaily');
operatesDaily.addEventListener('change', (event) => {
    const operatingDaysSection = document.getElementById('operatingDaysSection');
    operatingDaysSection.style.display = event.target.checked ? 'none' : 'block';
});

// Handle express route checkbox
const isExpress = document.getElementById('isExpress');
isExpress.addEventListener('change', (event) => {

    if (event.target.checked) {
        // Express route, disable stops
        addStopBtn.disabled = true;
        addStopBtn.style.opacity = '0.5';
        stopsContainer.style.opacity = '0.5';
        stopsContainer.style.pointerEvents = 'none';
    } else {
        // Regular route, enable stops
        addStopBtn.disabled = false;
        addStopBtn.style.opacity = '1';
        stopsContainer.style.opacity = '1';
        stopsContainer.style.pointerEvents = 'auto';
    }
});

// Handle form submission
const createRouteForm = document.getElementById('createRouteForm');
createRouteForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating route...';
    errorMessage.style.display = 'none';

    try {
        // Collect intermediate stops
        const stops = [];
        const stopItems = document.querySelectorAll('.stop-item');
        stopItems.forEach((stopItem) => {
            const city = stopItem.querySelector('.stop-city').value.trim();
            const duration = parseInt(stopItem.querySelector('.stop-duration').value);
            const distance = parseInt(stopItem.querySelector('.stop-distance').value);

            if (city && duration && distance) {
                stops.push({
                    city: city,
                    stop_duration_minutes: duration,
                    distance_from_origin_km: distance
                });
            }
        });

        // Collect operating days (if not daily)
        let operatingDays = null;
        if (!operatesDaily.checked) {
            operatingDays = [];
            document.querySelectorAll('input[name="operatingDay"]:checked').forEach((checkbox) => {
                operatingDays.push(checkbox.value);
            });

            if (operatingDays.length === 0) {
                errorMessage.textContent = 'Please select at least one operating day.';
                errorMessage.style.display = 'block';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Route';
                return;
            }
        }

        // Build route data
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
            status: "ACTIVE"
        };

        console.log('Creating route with data:', routeData);

        // Call API
        const response = await API.request('/api/routes/', {
            method: 'POST',
            body: JSON.stringify(routeData)
        });

        console.log('Route created:', response);

        alert('Route created successfully!');
        window.location.href = '/routes';

    } catch (error) {
        console.error('Error creating route:', error);
        errorMessage.textContent = error.message || 'Error creating route';
        errorMessage.style.display = 'block';
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Route';
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    await requireAdmin('/routes'); // redirect non-admin users to /routes
});
