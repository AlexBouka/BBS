<template>
  <div class="container">
    <div class="form-card">
      <h1 class="form-card__title">Create Bus</h1>
      <p class="form-card__subtitle">Add a new bus to the system</p>
      <form @submit.prevent="handleBusCreation" class="form" id="createBusForm">

        <!-- Basic Info -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Basic Information</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="busNumber">Bus Number *</label>
              <input
                v-model="form.busNumber"
                type="text"
                class="form__input"
                id="busNumber"
                placeholder="Enter bus number"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="licensePlate">License Plate *</label>
              <input
                v-model="form.licensePlate"
                type="text"
                class="form__input"
                id="licensePlate"
                placeholder="Enter license plate"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="busName">Bus Name</label>
              <input
                v-model="form.busName"
                type="text"
                class="form__input"
                id="busName"
                placeholder="Enter bus name (optional)"
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
                placeholder="Enter year"
                min="1900"
                max="2100"
                required
              />
            </div>
          </div>

          <!-- Seats -->
          <div class="form-section__form-row form-row">
            <h4 class="form-row__title">Seats</h4>
            <p class="form-row__help-text">Add seats by pressing the Add Row button and filling the seat count per row</p>
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
              <input v-model="form.hasWifi" type="checkbox" id="hasWifi" />
              <span>Wifi</span>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <input v-model="form.hasAc" type="checkbox" id="hasAc" />
              <span>Air Conditioning</span>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <input v-model="form.hasTv" type="checkbox" id="hasTv" />
              <span>TV</span>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <input v-model="form.hasChargingPorts" type="checkbox" id="hasChargingPorts" />
              <span>Charging Ports</span>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <input v-model="form.hasRefreshments" type="checkbox" id="hasRefreshments" />
              <span>Refreshments</span>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <input v-model="form.hasRestroom" type="checkbox" id="hasRestroom" />
              <span>Restroom(s)</span>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <input v-model="form.isAccessible" type="checkbox" id="isAccessible">
              <span>Wheelchair Accessible</span>
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

        <!-- Assign to route and departure -->
        <!-- <div class="form__form-section form-section">
          <h3 class="form-section__title">Assign to Route and Departure</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="routeSelect">Select a Route</label>
              <select v-model="form.routeId" @change="fetchDeparturesForRoute" id="routeSelect" class="form__select">
                <option value="">Select a Route</option>
                <option v-for="route in routes" :key="route.id" :value="route.id">
                  {{ route.route_number }} ({{ route.origin_city }} - {{ route.destination_city }})
                </option>
              </select>
            </div>
            <div class="form-row__form-group form-group">
              <label for="departureSelect">Select a Departure</label>
              <select v-model="form.departureId" id="departureSelect" class="form__select">
                <option value="">Select a Departure</option>
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
                <select v-model="assignment.routeId" @change="onRouteChange(index)" id="routeSelect" class="form__select">
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
              <label for="notes">Notes</label>
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
            {{ submitting ? 'Creating bus...' : 'Create Bus' }}
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

const router = useRouter();
const submitting = ref(false);
const error = ref('');
const rows = ref([]);
const routes = ref([]);
// const departures = ref([]);

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

// Loda routes on mount
onMounted(async () => {
  await requireAdmin('/buses'); // Redirect non-admins
  await loadRoutes();
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

// Add row
function addRow() {
  rows.value.push({ seats_in_row: null });
}

// Remove row
function removeRow(index) {
  rows.value.splice(index, 1);
}

// Load routes
async function loadRoutes() {
  try {
    const params = new URLSearchParams({ status: 'ACTIVE' });
    const data = await API.request(`/api/routes/?${params.toString()}`);
    routes.value = data;
  } catch (err) {
    console.error('Error loading routes:', err)
  }
}

// Fetch departures for a route on change
// async function fetchDeparturesForRoute() {
//   departures.value = [];
//   if (form.value.routeId) {
//     try {
//       const data = await API.request(`/api/departures/by_route_id/${form.value.routeId}`);
//       departures.value = data;
//     } catch (err) {
//       console.error('Error loading departures for selected route:', err);
//     }
//   }
// }

// Handle form submission
async function handleBusCreation() {
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
    if (routeIds.length > 0 && new Set(routeIds).size !== routeIds.length) {
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
    await API.request('/api/buses/', {
      method: 'POST',
      body: JSON.stringify(busData)
    });

    alert('Bus created successfully!');
    router.push('/buses');
  } catch (err) {
    console.error('Error creating bus:', err);
    error.value = 'An error occurred while creating the bus. Please try again.';
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

.remove-row-btn {
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