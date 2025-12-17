<template>
  <div class="container">
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-state__text">Loading bus data...</p>
    </div>

    <!-- Form -->
    <div v-else class="form-card">
      <h1 class="form-card__title">Update Bus</h1>
      <form @submit.prevent="handleUpdateBus" class="form">
        <input v-model="busId" type="hidden">

        <!-- Basic Info -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Basic Information</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="busNumber">Bus Number *</label>
              <input
                v-model="form.busNumber"
                type="text"
                id="busNumber"
                class="form__input"
                placeholder="Enter bus number"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="licensePlate">License Plate *</label>
              <input
                v-model="form.licensePlate"
                type="text"
                id="licensePlate"
                class="form__input"
                placeholder="Enter license plate"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="busName">Bus Name</label>
              <input
                v-model="form.busName"
                type="text"
                id="busName"
                placeholder="Enter bus name"
              />
            </div>
          </div>
        </div>

        <!-- Bus Specifications -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Bus Specifications</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="busType">Bus Type *</label>
              <select v-model="form.busType" id="busType" class="form__select" required>
                <option value="STANDARD" selected>Standard</option>
                <option value="MINIBUS">Minibus</option>
                <option value="LUXURY">Luxury</option>
                <option value="SLEEPER">Sleeper</option>
                <option value="MINIBUS_LUXURY">Minibus Luxury</option>
              </select>
            </div>
            <div class="form-row__form-group form-group">
              <label for="capacity">Capacity *</label>
              <input
                v-model.number="form.capacity"
                type="number"
                id="capacity"
                class="form__input"
                min="1"
                placeholder="Enter capacity"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="manufacturer">Manufacturer</label>
              <input
                v-model="form.manufacturer"
                type="text"
                id="manufacturer"
                class="form__input"
                placeholder="Enter manufacturer"
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="model">Model</label>
              <input
                v-model="form.model"
                type="text"
                id="model"
                class="form__input"
                placeholder="Enter model"
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="yearManufactured">Year Manufactured</label>
              <input
                v-model.number="form.yearManufactured"
                type="number"
                id="yearManufactured"
                class="form__input"
                min="1900"
                max="2100"
                placeholder="Enter year"
              />
            </div>
          </div>

          <!-- Seats -->
          <div class="form-section__form-row form-row">
            <h4 class="form-row__title">Seats</h4>
            <p class="form-row__text">Modify seats by pressing the Add Row button and filling the seat count per row</p>
            <div v-for="(row, index) in rows" :key="index" class="row-item">
              <label>Row {{ index + 1 }} - Number of seats:</label>
              <input
                v-model.number="row.seats_in_row"
                type="number"
                class="row-seat-count"
                min="1"
                max="6"
                required
              />
              <button @click="removeRow(index)" type="button" class="remove-row-btn">Remove</button>
            </div>
            <button @click="addRow" type="button" class="form-row__add-row-btn">Add Row</button>
          </div>
        </div>

        <!-- Amenities -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Amenities</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.hasWifi" type="checkbox" id="hasWifi">
                <span>Wifi</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.hasAc" type="checkbox" id="hasAc">
                <span>Air Conditioning</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.hasTv" type="checkbox" id="hasTv">
                <span>TV</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.hasChargingPorts" type="checkbox" id="hasChargingPorts">
                <span>Charging Ports</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.hasRefreshments" type="checkbox" id="hasRefreshments">
                <span>Refreshments</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.hasRestroom" type="checkbox" id="hasRestroom">
                <span>Restroom(s)</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.isAccessible" type="checkbox" id="isAccessible">
                <span>Wheelchair Accessible</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Operational Status -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Operational Status</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="status">Status *</label>
              <select v-model="form.status" id="status" class="form__select" required>
                <option value="ACTIVE" selected>Active</option>
                <option value="MAINTENANCE">Maintenance</option>
                <option value="INACTIVE">Inactive</option>
                <option value="DELETED">Deleted</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Assign to route
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Assign to Route</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="routesSelect">Select Route</label>
              <select v-model="form.routeId" @change="onRouteChange" id="routesSelect" class="form__select">
                <option value="">No Route Assigned</option>
                <option v-for="route in routes" :key="route.id" :value="route.id">
                  {{ route.route_number }} ({{ route.origin_city }} - {{ route.destination_city }})
                </option>
              </select>
            </div>
            <div class="form-row__form-group form-group">
              <label for="departuresSelect">Select Departure</label>
              <select v-model="form.departureId" id="departuresSelect" class="form__select">
                <option value="">No Departure Assigned</option>
                <option v-for="departure in departures" :key="departure.id" :value="departure.id">
                  {{ new Date(departure.departure_time).toLocaleString() }} | Status: {{ departure.status }}
                </option>
              </select>
            </div>
          </div>
        </div> -->

        <!-- Assign to routes and departures -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Assign to Routes and Departures</h3>
          <div v-for="(assignment, index) in assignments" :key="index" class="assignment-item">
            <div class="assignment-header">
              <h4 class="assignment-header__title">Assignment {{ index + 1 }}</h4>
              <button @click="removeAssignment(index)" type="button" class="assignment-header__remove-btn">
                Remove
              </button>
            </div>
            <div class="form-section__form-row form-row">
              <div class="form-row__form-group form-group">
                <label for="routeSelect">Select Route</label>
                <select v-model="assignment.routeId" @change="onRouteChange(index)" id="routeSelect-${index}" class="form__select">
                  <option value="">Select Route</option>
                  <option v-for="route in routes" :key="route.id" :value="route.id">
                    {{ route.route_number }} ({{ route.origin_city }} - {{ route.destination_city }})
                  </option>
                </select>
              </div>
              <div class="form-row__form-group form-group">
                <label for="depsSelect">Select Departures</label>
                <select v-if="assignment.routeId" v-model="assignment.departureIds" multiple id="depsSelect" class="form__select">
                  <option v-if="assignment.loading" disabled>Loading Departures...</option>
                  <option v-for="departure in assignment.departures" :key="departure.id" :value="departure.id">
                    {{ new Date(departure.departure_time).toLocaleString() }} | Status: {{ departure.status }}
                  </option>
                </select>
                <div v-if="assignment.error" class="departures-select-error-wrapper">
                  <p class="departure-select-error__text">{{ assignment.error }}</p>
                </div>
              </div>
            </div>
          </div>
          <button @click="addAssignment" type="button" class="add-assignment-btn">Add Route</button>
        </div>

        <!-- Additional Information -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Additional Information</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="description">Description</label>
              <textarea v-model="form.description" id="description" rows="3"></textarea>
            </div>
            <div class="form-row__form-group form-group">
              <label for="notes">Internal Notes</label>
              <textarea v-model="form.notes" id="notes" rows="2" placeholder="Staff notes, special instructions, etc."></textarea>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          <p class="error-message__text">{{ error }}</p>
        </div>

        <!-- Submit & Cancel buttons -->
        <div class="form__form-actions">
          <button @click="$router.go(-1)" type="button" class="form__cancel-btn">Cancel</button>
          <button :disabled="submitting" type="submit" class="form__submit-btn">
            {{ submitting ? 'Updating bus...' : 'Update Bus' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { API, requireAdmin } from '../../../frontend/static/js/api.js';

const props = defineProps({
  id: {
    type: String,
    required: true
  }
});

const router = useRouter();
const busId = ref(props.id);
const loading = ref(false);
const error = ref('');
const submitting = ref(false);
const rows = ref([]);
const routes = ref([]);

const form = ref({
  busNumber: '',
  licensePlate: '',
  busName: '',
  busType: 'STANDARD',
  capacity: null,
  manufacturer: '',
  model: '',
  yearManufactured: null,
  hasWifi: false,
  hasAc: false,
  hasTv: false,
  hasChargingPorts: false,
  hasRefreshments: false,
  hasRestroom: false,
  isAccessible: false,
  status: 'ACTIVE',
  description: '',
  notes: ''
});

const assignments = ref([]);

// Load bus data on mount
onMounted(async () => {
  await requireAdmin('/buses'); // Redirect non-admins
  await loadBusData();
});

function addAssignment() {
  assignments.value.push({ routeId: '', departureIds: [], departures: [] });
}

function removeAssignment(index) {
  assignments.value.splice(index, 1);
}

async function onRouteChange(index) {
  const assignment = assignments.value[index];
  assignment.departures = [];
  assignment.loading = true;
  assignment.error = '';
  if (assignment.routeId) {
    try {
      const data = await API.request(`/api/departures/by_route_id/${assignment.routeId}`);
      assignment.departures = data;
    } catch (err) {
      console.error('Error loading departures:', err);
      assignment.error = 'Failed to load departures. Please try again.';
      assignment.departures = [];
    }
  }
  assignment.loading = false;
}

/**
 * Loads bus data and prefills form with it.
 * Also loads routes and sets current selection, if available.
 * If bus data has route_ids and departure_ids, it will load the corresponding 
 * departures for each route and set the current selection.
 * If bus data has rows, it will prefill the rows with it.
 * Error is caught and displayed if there is an error loading bus data.
 * Finally, it sets loading to false.
 */
async function loadBusData() {
  try {
    const busData = await API.request(`/api/buses/${busId.value}`, { method: 'GET' });

    // Prefill form
    form.value.busNumber = busData.bus_number;
    form.value.licensePlate = busData.license_plate;
    form.value.busName = busData.bus_name || '';
    form.value.busType = busData.bus_type;
    form.value.capacity = busData.capacity;
    form.value.manufacturer = busData.manufacturer || '';
    form.value.model = busData.model || '';
    form.value.yearManufactured = busData.year_manufactured || null;
    form.value.hasWifi = busData.has_wifi;
    form.value.hasAc = busData.has_ac;
    form.value.hasTv = busData.has_tv;
    form.value.hasChargingPorts = busData.has_charging_ports;
    form.value.hasRefreshments = busData.has_refreshments;
    form.value.hasRestroom = busData.has_restroom;
    form.value.isAccessible = busData.is_accessible;
    form.value.status = busData.status;
    form.value.description = busData.description || '';
    form.value.notes = busData.notes || '';

    // Load routes and set current selection
    await loadRoutes();

    if (busData.route_ids && busData.route_ids.length > 0) {
      const allDepartures = [];

      for (const routeId of busData.route_ids) {
        try {
          const departuresForRoute = await API.request(`/api/departures/by_route_id/${routeId}`);
          allDepartures.push(...departuresForRoute.map(dep => ({ ...dep, routeId })));
        } catch (err) {
          console.error(`Error loading departures for route ${routeId}:`, err);
        }
      }

      for (const routeId of busData.route_ids) {
        const matchingDepartures = allDepartures.filter(
          dep => dep.id && busData.departure_ids.includes(dep.id) && dep.routeId === routeId);
        const departureIdsForRoute = matchingDepartures.map(dep => dep.id);

        assignments.value.push({
          routeId: routeId,
          departureIds: departureIdsForRoute,
          departures: matchingDepartures,
          loading: false,
          error: ''
        });
      }
    }

    // Prefill rows if available (assuming rows are in busData.rows)
    if (busData.rows) {
      rows.value = busData.rows.map(row => ({
        row_number: row.row_number,
        seats_in_row: row.seat_count
      }));
    }
  } catch (err) {
    error.value = `Error loading bus data: ${err.message}`;
    console.error('Error loading bus data:', err);
  } finally {
    loading.value = false;
  }
}

/**
 * Loads all active routes from the API and sets the current selection if selectedRouteId is provided.
 * If an error occurs while loading the routes, it will be logged to the console.
 * @param {string} selectedRouteId - The route ID to select after loading the routes (optional).
 */
async function loadRoutes(selectedRouteId = null) {
  try {
    const params = new URLSearchParams({ status: 'ACTIVE' });
    const data = await API.request(`/api/routes/?${params.toString()}`);
    routes.value = data;
    if (selectedRouteId) {
      form.value.routeId = selectedRouteId;
    }
  } catch (err) {
    console.error('Error loading routes:', err);
  }
}

// Add row
function addRow() {
  rows.value.push({ seats_in_row: null });
}

// Remove row
function removeRow(index) {
  rows.value.splice(index, 1);
}

/**
 * Handles the bus update form submission by preparing the rows, checking for duplicate routes and departures, building the bus data, and calling the API to update the bus.
 * If an error occurs during the API call, it will be logged to the console and displayed to the user.
 * If the bus is updated successfully, the user will be redirected to /buses.
 */
async function handleUpdateBus() {
  submitting.value = true;
  error.value = '';

  try {
    // Prepare rows
    const preparedRows = rows.value.filter(row => row.seats_in_row).map((row, index) => ({
      row_number: index + 1,
      seat_count: row.seats_in_row
    }));

    const routeIds = assignments.value.map(a => a.routeId).filter(id => id);
    const departureIds = assignments.value.flatMap(a => a.departureIds);

    // Check for duplicate routes
    if (routeIds.length > 0 &&new Set(routeIds).size !== routeIds.length) {
      error.value = 'Duplicate routes are not allowed accross assignments.';
      submitting.value = false;
      return;
    }

    // Check for duplicate departures
    if (departureIds.length > 0 && new Set(departureIds).size !== departureIds.length) {
      error.value = 'Duplicate departures are not allowed accross assignments.';
      submitting.value = false;
      return;
    }

    // Build bus data
    const busData = {
      bus_number: form.value.busNumber.trim(),
      license_plate: form.value.licensePlate.trim(),
      bus_name: form.value.busName.trim() || null,
      bus_type: form.value.busType,
      capacity: form.value.capacity,
      manufacturer: form.value.manufacturer.trim() || null,
      model: form.value.model.trim() || null,
      year_manufactured: form.value.yearManufactured || null,
      has_wifi: form.value.hasWifi,
      has_ac: form.value.hasAc,
      has_tv: form.value.hasTv,
      has_charging_ports: form.value.hasChargingPorts,
      has_refreshments: form.value.hasRefreshments,
      has_restroom: form.value.hasRestroom,
      is_accessible: form.value.isAccessible,
      status: form.value.status,
      description: form.value.description.trim() || null,
      notes: form.value.notes.trim() || null,
      route_ids: routeIds,
      departure_ids: departureIds,
      rows: preparedRows
    };

    // Call API
    await API.request(`/api/buses/${busId.value}`, {
      method: 'PUT',
      body: JSON.stringify(busData)
    });

    alert('Bus updated successfully!');
    router.push('/buses');
  } catch (err) {
    error.value = `Error updating bus: ${err.message}`;
    console.error('Error updating bus:', err);
  } finally {
    submitting.value = false;
  }
}

</script>

<style scoped>
.form-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  max-width: 900px;
  margin: 2rem auto;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h3 {
  margin-bottom: 1rem;
  color: #333;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.row-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.btn-remove-row {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.loading-state {
  text-align: center;
  color: #666;
}

.assignment-item {
  border: 1px solid #e0e0e0;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 5px;
}

.assignment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.assignment-header__remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  cursor: pointer;
}

.departures-select-error-wrapper {
  background: #f8d7da;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.departure-select-error__text {
  margin: 0;
  color: #721c24;
}
</style>