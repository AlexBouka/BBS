<template>
  <div class="container">
    <div class="form-card">
      <h1 class="form-card__title">Create Route</h1>
      <p class="form-card__subtitle">Add a new bus route to the system</p>
      <form @submit.prevent="handleCreateRoute" class="form-card__form form" id="createRouteForm">

        <!-- Basic Information-->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Basic Information</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="routeNumber" class="form__label">Route Number *</label>
              <input
                v-model="form.routeNumber"
                type="text"
                class="form__input"
                id="routeNumber"
                placeholder="Enter route number"
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="routeName" class="form__label">Route Name</label>
              <input
                v-model="form.routeName"
                type="text"
                class="form__input"
                id="routeName"
              />
            </div>
          </div>
        </div>

        <!-- Origin & Destination cities -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Route Details</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group form-group">
              <label for="originCity" class="form__label">Origin City *</label>
              <input
                v-model="form.originCity"
                type="text"
                id="originCity"
                class="form__input"
                placeholder="Enter origin city"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="destinationCity" class="form__label">Destination City *</label>
              <input
                v-model="form.destinationCity"
                type="text"
                id="destinationCity"
                class="form__input"
                placeholder="Enter destination city"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="distanceKm" class="form__label">Distance (km) *</label>
              <input
                v-model.number="form.distanceKm"
                type="number"
                id="distanceKm"
                class="form__input"
                placeholder="Enter distance"
                required
                min="1"
                step="1"
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="durationMinutes" class="form__label">Duration (minutes) *</label>
              <input
                v-model.number="form.durationMinutes"
                type="number"
                id="durationMinutes"
                class="form__input"
                placeholder="Enter trip duration in minutes"
                min="1"
                step="1"
                required
              />
            </div>
            <div class="form-row__form-group form-group">
              <label for="basePrice" class="form__label">Base Price *</label>
              <input
                v-model.number="form.basePrice"
                type="text"
                id="basePrice"
                class="form__input"
                placeholder="Enter base price"
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
          <div id="stopsContainer" class="form-section__stops-container">
            <div
              v-for="(stop, index) in stops"
              :key="index"
              :data-stop-id="index + 1"
              class="stops-container__stop-item"
            >
              <div class="stop-item__stop-header stop-header">
                <h4 class="stop-item__title">Stop {{ index + 1 }}</h4>
                <button @click="removeStop(index)" type="button" class="btn-remove-stop">
                  Remove
                </button>
              </div>
              <div class="form-section__form-row form-row">
                <div class="form-row__form-group form-group">
                  <label>City</label>
                  <input
                    v-model="stop.city"
                    type="text"
                    class="stop-city"
                    placeholder="Enter city or stop name"
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
                    placeholder="e.g., 15"
                    required
                  />
                </div>
                <div class="form-row__form-group form-group">
                  <label>Distance from Origin City (km)</label>
                  <input
                    v-model.number="stop.distance_from_origin_km"
                    type="number"
                    class="stop-distance"
                    min="0"
                    step="1"
                    placeholder="e.g., 85"
                    required
                  />
                </div>
              </div>
            </div>
          </div>
          <button
            @click="addStop"
            :disabled="form.isExpress"
            class="form__add-stop-btn"
            type="button">
            + Add Stop
          </button>
        </div>

        <!-- Route Options -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Route Options</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group checkbox-group">
              <label>
                <input v-model="form.isExpress" type="checkbox" id="isExpress" />
                <span>Express Route (no stops)</span>
              </label>
            </div>
            <div class="form-row__form-group checkbox-group">
              <label>
                <input v-model="form.isOvernight" type="checkbox" id="isOvernight" />
                <span>Overnight Route</span>
              </label>
            </div>
            <div class="form-row__form-group checkbox-group">
              <label>
                <input v-model="form.operatesDaily" type="checkbox" id="operatesDaily" />
                <span>Operates Daily</span>
              </label>
            </div>
          </div>

          <!-- Operating Days -->
          <div v-if="!form.operatesDaily" class="form-section__operating-days operating-days" id="operatingDaysSection">
            <h4 class="operating-days__title">Operating Days</h4>
            <div class="operating-days__checkbox-group-inline checkbox-group-inline">
              <label v-for="day in daysOfWeek" :key="day" class="checkbox-group-inline__label">
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

        <!-- Departures -->
        <div class="form__form-section">
          <h3 class="form-section__title">Add Departure Schedule</h3>
          <p class="form-section__help-text">Add departure times for this route (optional)</p>
          <div id="departuresContainer" class="form-section__departures departures">
            <div
              v-for="(departure, index) in departures"
              :key="index"
              :data-departure-id="index + 1"
              class="departures__departure-item"
            >
              <div class="departure-item__departure-header departure-header">
                <h4 class="departure-item__title">Departure {{ index + 1 }}</h4>
                <button @click="removeDeparture(index)" type="button" class="departure-item__remove-departure-btn remove-departure-btn">
                  Remove
                </button>
              </div>
              <div class="form-section__form-row form-row">
                <div class="form-row__form-group form-group">
                  <label>Departure Time</label>
                  <input v-model="departure.departure_time" type="datetime-local" class="departure-time" required />
                </div>
                <div class="form-row__form-group form-group">
                  <label>Arrival Time (optional)</label>
                  <input v-model="departure.arrival_time" type="datetime-local" class="arrival-time" />
                </div>
                <div class="form-row__form-group form-group">
                  <label>Notes</label>
                  <input v-model="departure.notes" type="text" class="departure-notes" placeholder="Optional notes" />
                </div>
              </div>
            </div>
          </div>
          <button @click="addDeparture" type="button" class="form__add-departure-btn">
            + Add Departure
          </button>
        </div>

        <!-- Additional Information -->
        <div class="form__form-section form-section">
          <h3 class="form-section__title">Additional Information</h3>
          <div class="form-section__form-row form-row">
            <div class="form-row__form-group">
              <label for="description">Description</label>
              <textarea v-model="form.description" id="description" rows="3"></textarea>
            </div>
            <div class="form-row__form-group">
              <label for="notes">Internal Notes</label>
              <textarea v-model="form.notes" id="notes" rows="2"></textarea>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="error-message">
          <p class="error-message__text">{{ error }}</p>
        </div>

        <!-- Submit & Cancel buttons -->
        <div class="form__form-actions form-actions">
          <button @click="$router.go(-1)" class="form__cancel-btn">Cancel</button>
          <button type="submit" :disabled="loading" class="form__submit-btn" id="submitBtn">
            {{ loading ? 'Creating route...' : 'Create Route' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { API, requireAdmin } from '../../../frontend/static/js/api.js';

const router = useRouter();
const form = ref({
  routeNumber: '',
  routeName: '',
  originCity: '',
  destinationCity: '',
  distanceKm: null,
  durationMinutes: null,
  basePrice: null,
  isExpress: false,
  isOvernight: false,
  operatesDaily: true,
  operatingDays: [],
  description: '',
  notes: ''
});
const stops = ref([]);
const departures = ref([]);
const loading = ref(false);
const error = ref('');
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

// Check if user is admin
onMounted(async () => {
  await requireAdmin('/routes');
});

// Add stop
const addStop = () => {
  if (!form.value.isExpress) {
    stops.value.push({
      city: '',
      stop_duration_minutes: null,
      distance_from_origin_km: null
    });
  }
};

// Remove stop
const removeStop = (index) => {
  stops.value.splice(index, 1);
};

// Add departure
const addDeparture = () => {
  departures.value.push({
    departure_time: '',
    arrival_time: '',
    notes: ''
  });
};

// Remove departure
const removeDeparture = (index) => {
  departures.value.splice(index, 1);
};

// Handle form submission
const handleCreateRoute = async () => {
  loading.value = true;
  error.value = '';

  try {
    // Validate operating days
    if (!form.value.operatesDaily && form.value.operatingDays.length === 0) {
      error.value = 'Please select at least one operating day or choose "Operates Daily".';
      loading.value = false;
      return;
    }

    // Prepare intermadiate stops
    const preparedStops = stops.value.filter(
      stop => stop.city && stop.stop_duration_minutes && stop.distance_from_origin_km
    ).map(stop => ({
      city: stop.city.trim(),
      stop_duration_minutes: stop.stop_duration_minutes,
      distance_from_origin_km: stop.distance_from_origin_km
    }));

    // Prepare departures: filter valid entries, convert dates to UTC ISO strings, and clean undefined values
    const preparedDepartures = departures.value.filter(dep => dep.departure_time).map(dep => ({
      departure_time: new Date(dep.departure_time).toISOString(),
      arrival_time: dep.arrival_time ? new Date(dep.arrival_time).toISOString() : null,
      notes: dep.notes.trim() || null
    })).map(dep => {
      const cleaned = { ...dep };
      Object.keys(cleaned).forEach(key => {
        if (cleaned[key] === null) {
          delete cleaned[key];
        }
      });
      return cleaned;
    });

    // Build route data
    const routeData = {
      route_number: form.value.routeNumber.trim(),
      route_name: form.value.routeName.trim() || null,
      origin_city: form.value.originCity.trim(),
      destination_city: form.value.destinationCity.trim(),
      distance_km: form.value.distanceKm,
      duration_minutes: form.value.durationMinutes,
      base_price: form.value.basePrice,
      intermediate_stops: preparedStops.length > 0 ? preparedStops : null,
      is_express: form.value.isExpress,
      is_overnight: form.value.isOvernight,
      operates_daily: form.value.operatesDaily,
      operatingDays: form.value.operatesDaily ? null : form.value.operatingDays,
      description: form.value.description.trim() || null,
      notes: form.value.notes.trim() || null,
      status: 'ACTIVE',
      departures: preparedDepartures.length > 0 ? preparedDepartures : null
    };

    // Call API
    await API.request('/api/routes', {
      method: 'POST',
      body: JSON.stringify(routeData)
    });

    alert('Route created successfully!');
    router.push('/routes');
  } catch (err) {
    error.value = err.message || 'Failed to create route. Please try again.';
    console.error('Create route error:', err);
  } finally {
    loading.value = false;
  }
};
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

.checkbox-group-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.checkbox-group-inline label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-group-inline input[type="checkbox"] {
  margin-right: 0.25rem;
}

.help-text {
  color: #666;
  font-size: 0.9rem;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}

/* Stop Item Styles */
.stop-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
  border: 1px solid #e0e0e0;
}

.stop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stop-header h4 {
  margin: 0;
  color: #667eea;
  font-size: 1rem;
}

.btn-remove-stop {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-remove-stop:hover {
  background: #c82333;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}
</style>