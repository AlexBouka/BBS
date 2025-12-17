<template>
  <div class="container">
    <div class="form-card">
      <h1 class="form-card__title">Update Route</h1>
      <p class="form-card__subtitle">Update an existing bus route in the system</p>

      <!-- Loading state -->
      <div v-if="loading" class="form-card__loading-state">
        <p class="loading-state__text">Loading route data...</p>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="handleUpdateRoute" class="form-card__form form">
        <input v-model="routeId" type="hidden">

        <!-- Basic Information -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Basic Information</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="routeNumber">Route Number *</label>
              <input
                v-model="form.routeNumber"
                type="text"
                id="routeNumber"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="routeName">Route Name</label>
              <input
                v-model="form.routeName"
                type="text"
                id="routeName"
              />
            </div>
          </div>
        </div>

        <!-- Route Details -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Route Details</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="originCity">Origin City *</label>
              <input
                v-model="form.originCity"
                type="text"
                id="originCity"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="destinationCity">Destination City *</label>
              <input
                v-model="form.destinationCity"
                type="text"
                id="destinationCity"
                required
              />
            </div>
          </div>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="distanceKm">Distance (km) *</label>
              <input
                v-model.number="form.distanceKm"
                type="number"
                id="distanceKm"
                min="1"
                step="1"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="durationMinutes">Duration (minutes) *</label>
              <input
                v-model.number="form.durationMinutes"
                type="number"
                id="durationMinutes"
                min="1"
                step="1"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="basePrice">Base Price *</label>
              <input
                v-model.number="form.basePrice"
                type="number"
                id="basePrice"
                min="0"
                step="0.1"
                required
              />
            </div>
          </div>
        </div>

        <!-- Intermediate Stops -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Intermediate Stops</h3>
          <p class="form-section__help-text">Add stops along the route (optional)</p>
          <div class="form-section__stops-container stops-container">
            <div
              v-for="(stop, index) in stops" :key="index" :data-stop-id="index + 1"
              class="stop-container__stop-item stop-item">
              <div class="stop-item__stop-header stop-header">
                <h4 class="stop-header__title">Stop {{ index + 1 }}</h4>
                <button @click="removeStop(index)" type="button" class="stop-header__remove-btn">
                  Remove
                </button>
              </div>
              <div class="stops-container__form-row form-row">
                <div class="form-row__form-group form-group">
                  <label>City</label>
                  <input
                    v-model="stop.city"
                    type="text"
                    class="stop-city"
                    required
                  />
                </div>
                <div class="form-row__form-group form-group">
                  <label>Stop Duration (minutes)</label>
                  <input
                    v-model.number="stop.stop_duration_minutes"
                    type="number"
                    class="stop-duration"
                    min="1"
                    required
                  />
                </div>
                <div class="form-row__form-group form-group">
                  <label>Distance from Origin (km)</label>
                  <input
                    v-model.number="stop.distance_from_origin_km"
                    type="number"
                    class="stop-distance"
                    min="0"
                    step="1"
                    required
                  />
                </div>
              </div>
            </div>
          </div>
          <button @click="addStop" type="button" class="form-section__add-stop-btn">+ Add Stop</button>
        </div>

        <!-- Departure Schedule -->
        <div class="form__form-section">
          <h3 class="form-section__title">Add Departure Schedule</h3>
          <p class="form-section__help-text">Add departure times for this route (optional)</p>
          <div class="form-section__departures-container departures-container" id="departuresContainer">
            <div
              v-for="(departure, index) in departures"
              :key="index"
              :data-departure-id="index + 1"
              :data-original-index="departure.originalIndex"
              class="departures-container__departure-item departure-item">
              <div class="departure-item__departure-header departure-header">
                <h4 class="departure-header__title">Departure {{ index + 1 }}</h4>
                <button @click="removeDeparture(index)" type="button" class="remove-departure-btn">
                  Remove
                </button>
              </div>
              <div class="departures-container__form-row form-row">
                <div class="form-row__form-group form-group">
                  <label>Departure Time *</label>
                  <input
                    v-model="departure.departure_time"
                    type="datetime-local"
                    class="departure-time"
                    required
                  />
                </div>
                <div class="form-row__form-group form-group">
                  <label></label>
                  <input
                    v-model="departure.arrival_time"
                    type="datetime-local"
                    class="arrival-time"
                  />
                </div>
                <div class="form-row__form-group form-group">
                  <label></label>
                  <input
                    v-model="departure.notes"
                    type="text"
                    class="departure-notes"
                    placeholder="Optional notes"
                  />
                </div>
              </div>
            </div>
          </div>
          <button @click="addDeparture" type="button" class="form-section__add-departure-btn">+ Add Departure</button>
        </div>

        <!-- Route Options -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Route Options</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="status">Status</label>
              <select v-model="form.status" id="status">
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
                <option value="SEASONAL">Seasonal</option>
                <option value="DELETED">Deleted</option>
              </select>
            </div>
          </div>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.isExpress" type="checkbox" id="isExpress">
                <span class="checkbox-group__text">Express Route</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.isOvernight" type="checkbox" id="isOvernight">
                <span class="checkbox-group__text">Overnight Route</span>
              </label>
            </div>
            <div class="form-row__form-group form-group checkbox-group">
              <label>
                <input v-model="form.operatesDaily" type="checkbox" id="operatesDaily">
                <span class="checkbox-group__text">Operates Daily</span>
              </label>
            </div>
            <div v-if="!form.operatesDaily" class="form-row__additional-section additional-section">
              <div class="additional-section__checkbox-group checkbox-group">
                <label v-for="day in daysOfWeek" :key="day">
                  <input
                    v-model="form.operatingDays"
                    type="checkbox"
                    :value="day.toLowerCase()"
                    name="operatingDay"
                  />
                  {{ day }}
                </label>
              </div>
            </div>
          </div>
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
              <textarea v-model="form.notes" id="notes" rows="2"></textarea>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          <p class="error-message__text">{{ error }}</p>
        </div>

        <!-- Form Actions -->
        <div class="form__form-actions form-actions">
          <button @click="router.go(-1)" type="button" class="form-actions__cancel-btn">Cancel</button>
          <button :disabled="submitting" type="submit" class="form-actions__submit-btn">
            {{ submitting ? 'Updating route...' : 'Update Route' }}
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
const routeId = ref(props.id);
const loading = ref(false);
const error = ref('');
const submitting = ref(false);
const stops = ref([]);
const departures = ref([]);
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const form = ref({
  routeNumber: '',
  routeName: '',
  originCity: '',
  destinationCity: '',
  distanceKm: null,
  durationMinutes: null,
  basePrice: null,
  status: 'ACTIVE',
  isExpress: false,
  isOvernight: false,
  operatesDaily: true,
  operatingDays: [],
  description: '',
  notes: ''
});

// Load route data on mount
onMounted(async () => {
  await requireAdmin('/routes'); // redirect non-admin users to /routes
  await loadRouteData();
});

/**
 * Loads route data from the API and prefills the form and intermediate stops/departures arrays.
 * Sets the loading state to true before making the request and false after receiving the response.
 * If an error occurs, sets the error message to the error reference.
 */
async function loadRouteData() {
  try {
    const routeData = await API.request(`/api/routes/${routeId.value}`, {method: 'GET'});

    // Prefill form
    form.value.routeNumber = routeData.route_number;
    form.value.routeName = routeData.route_name || '';
    form.value.originCity = routeData.origin_city;
    form.value.destinationCity = routeData.destination_city;
    form.value.distanceKm = routeData.distance_km;
    form.value.durationMinutes = routeData.duration_minutes;
    form.value.basePrice = routeData.base_price;
    form.value.status = routeData.status;
    form.value.isExpress = routeData.is_express;
    form.value.isOvernight = routeData.is_overnight;
    form.value.operatesDaily = routeData.operates_daily;
    form.value.operatingDays = routeData.operating_days || [];
    form.value.description = routeData.description || '';
    form.value.notes = routeData.notes || '';

    // Prefill intermediate stops
    if (routeData.intermediate_stops) {
      stops.value = routeData.intermediate_stops.map(stop => ({
        city: stop.city,
        stop_duration_minutes: stop.stop_duration_minutes,
        distance_from_origin_km: stop.distance_from_origin_km
      }));
    }

    // Prefill departures with original indices
    if (routeData.departures) {
      departures.value = routeData.departures.map((dep, index) => ({
        originalIndex: index,
        departure_time: dep.departure_time ? new Date(new Date(dep.departure_time).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '',
        arrival_time: dep.arrival_time ? new Date(new Date(dep.arrival_time).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '',
        notes: dep.notes || ''
      }));
    }

  } catch (err) {
    error.value = `Error loading route: ${err.message}`;
  } finally {
    loading.value = false;
  }
}

// Add intermediate stop
function addStop() {
  stops.value.push({
    city: '',
    stop_duration_minutes: null,
    distance_from_origin_km: null
  });
}

// Remove intermediate stop
function removeStop(index) {
  stops.value.splice(index, 1);
}

// Add departure
function addDeparture() {
  departures.value.push({
    originalIndex: -1, // new departure
    departure_time: '',
    arrival_time: '',
    notes: ''
  });
}

// Remove departure
function removeDeparture(index) {
  departures.value.splice(index, 1);
}

/**
 * Handles the route update form submission by preparing the intermediate stops and departures,
 * building the route update data, and calling the API to update the route.
 * If an error occurs, sets the error message to the error reference.
 * If the request is successful, shows a success alert and redirects the user to /routes.
 */
async function handleUpdateRoute() {
  submitting.value = true;
  error.value = '';

  try {
    // Prepare intermediate stops
    const preparedStops = stops.value.filter(
      stop => stop.city && stop.stop_duration_minutes && stop.distance_from_origin_km
    );

    // Prepare departures: filter valid entries, convert dates to UTC ISO strings, and clean undefined values
    const preparedDepartures = departures.value.filter(dep => dep.departure_time).map(
      dep => ({
        original_index: dep.originalIndex,
        departure_time: new Date(dep.departure_time).toISOString(),
        arrival_time: dep.arrival_time ? new Date(dep.arrival_time).toISOString() : null,
        notes: dep.notes.trim() || null
      })
    );

    // Build route update data
    const updateData = {
      route_number: form.value.routeNumber.trim(),
      route_name: form.value.routeName.trim() || null,
      origin_city: form.value.originCity.trim(),
      destination_city: form.value.destinationCity.trim(),
      distance_km: form.value.distanceKm,
      duration_minutes: form.value.durationMinutes,
      base_price: form.value.basePrice,
      intermediate_stops: preparedStops.length > 0 ? preparedStops : null,
      departures: preparedDepartures.length > 0 ? preparedDepartures : null,
      is_express: form.value.isExpress,
      is_overnight: form.value.isOvernight,
      operates_daily: form.value.operatesDaily,
      operating_days: form.value.operatesDaily ? null : form.value.operatingDays,
      description: form.value.description.trim() || null,
      notes: form.value.notes.trim() || null,
      status: form.value.status
    };

    // Call API
    await API.request(`/api/routes/${routeId.value}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    });

    alert('Route updated successfully!');
    router.push('/routes');

  } catch (err) {
    error.value = err.message || 'Error updating route. Please try again.';
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

.additional-section__checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.additional-section__checkbox-group label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.additional-section__checkbox-group input[type="checkbox"] {
  margin-right: 0.25rem;
}

.help-text {
  color: #666;
  font-size: 0.9rem;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}

.stop-item,
.departure-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  border: 1px solid #e0e0e0;
}

.stop-header,
.departure-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stop-header h4,
.departure-header h4 {
  margin: 0;
  color: #667eea;
  font-size: 1rem;
}

.btn-remove-stop,
.btn-remove-departure {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-remove-stop:hover,
.btn-remove-departure:hover {
  background: #c82333;
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

.loading-state__text {
  text-align: center;
  color: #666;
}
</style>