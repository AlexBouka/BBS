<template>
  <div class="container">
    <div class="route-card">
      <div class="route-card__title-wrapper">
        <h1 class="route-card__title">Route Details</h1>
      </div>
      <div class="route-card__route route">
        <p v-if="loading" class="route__loading-text">Loading route details...</p>
        <div v-else-if="error" class="error-message">{{ error }}</div>
        <div v-else>
          <div class="route__title-wrapper">
            <h2>{{ route.route_number }} - {{ route.route_name }}</h2>
          </div>

          <!-- Route wrapper -->
          <div class="route-wrapper">
            <div class="route-details-wrapper">
              <div class="route-info__basic-route-info">
                <p class="route-info__text">
                  From: {{ route.origin_city }}
                </p>
                <p class="route-info__text">
                  To: {{ route.destination_city }}
                </p>
                <p class="route-info__text">
                  Distance: {{ route.distance_km }} km
                </p>
                <p class="route-info__text">
                  Duration: {{ route.estimated_duration_hours }} hours
                </p>
                <p class="route-info__text">
                  Stops: {{ route.total_stops }}
                </p>
                <p class="route-info__text">
                  Base Price: {{ route.base_price }}
                </p>
                <div v-if="route.intermediate_stops" class="route-info__intermediate-stops intermediate-stops">
                  <div
                    v-for="stop in route.intermediate_stops"
                    :key="stop.city"
                    class="intermediate-stops__intermediate-stop-item intermediate-stop-item">
                    <p class="intermediate-stop__item-city">
                      Stop at {{ stop.city }}
                    </p>
                    <p class="intermediate-stop__item-distance">
                      {{ stop.distance_from_origin_km }} km
                    </p>
                    <p class="intermediate-stop__item-duration">
                      {{ stop.stop_duration_minutes }} minutes
                    </p>
                  </div>
                </div>
                <div class="route-info__additional-options-wrapper additional-options">
                  <div class="additional-options__express-wrapper">
                    <p :class="route.is_express ? 'route-info__express-true' : 'route-info__express-false'">
                      Express
                      <svg v-if="route.is_express" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </p>
                  </div>
                  <div class="additional-options__overnight-wrapper">
                    <p :class="route.is_overnight ? 'route-info__overnight-true' : 'route-info__overnight-false'">
                      Overnight
                      <svg v-if="route.is_overnight" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </p>
                  </div>
                </div>
              </div>
              <div class="route-info__calendar calendar">
                <div class="calendar__header">
                  <button @click="changeMonth(-1)" class="calendar__header-btn-prev"><</button>
                  <h4 class="calendar__header-month">{{ formatMonth(currentMonth) }}</h4>
                  <button @click="changeMonth(1)" class="calendar__header-btn-next">></button>
                </div>
                <div class="calendar__calendar-body calendar-body">
                  <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="calendar-body__day-header">
                    <span class="calendar-body__day">{{ day }}</span>
                  </div>
                  <!-- Empty cells for days before month starts -->
                  <div v-for="empty in startDayOffset" :key="'empty-' + empty" class="calendar-body__empty-cell"></div>
                  <div
                    v-for="day in daysInMonth"
                    :key="day"
                    :class="{ 'has-departures': hasDepartures(new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)) }"
                    @click="selectDate(new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day))"
                    class="calendar-body__calendar-day">
                      {{ day }}
                  </div>
                </div>

                <!-- Selected date departures -->
                <div v-if="selectedDate" class="calendar__day-departures day-departures">
                  <h4 class="day-departures-title">Departures for {{ formatDate(selectedDate) }}</h4>
                  <div v-if="loadingDay" class="day-departures__loading-state">
                    <p class="day-departures__loading-state-text">Loading departures...</p>
                  </div>
                  <div v-else-if="selectedDateDepartures.length === 0" class="day-departures__no-results">
                    <p class="day-departures__no-results-text">No departures found.</p>
                  </div>
                  <div v-else class="day-departures__list">
                    <div v-for="departure in selectedDateDepartures" :key="departure.id" class="calendar__departure-item">
                      {{ formatTime(departure.departure_time) }} - {{ departure.status }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- <div class="route-info">
              <p class="route-info__text">
                Express: {{ route.is_express ? 'Yes' : 'No' }}
              </p>
              <p class="route-info__text">
                Overnight: {{ route.is_overnight ? 'Yes' : 'No' }}
              </p>
              <p class="route-info__text">
                Operates Daily: {{ route.operates_daily ? 'Yes' : 'No' }}
              </p>
              <div class="route-info__operating-days">
                <p class="route-info__operating-days-title">Operating Days:</p>
                <ul class="routes__days-list">
                  <li v-for="day in operatingDays" :key="day" class="routes__days-list-day">{{ day }}</li>
                </ul>
              </div>
            </div> -->
            <div v-if="upcomingDeparturesSection" class="route-info__upcoming-departures upcoming-departures">
              <div v-if="upcomingDeparturesLoading" class="route-info__departures-loading-state">
                <p class="departures-loading-state__text">Loading departures...</p>
              </div>
              <div v-else-if="upcomingDepartures && upcomingDepartures.length" class="route-info__upcoming-departures upcoming-departures-wrapper">
                <h3 class="upcoming-departures__title">Departures for upcoming week</h3>
                <ul class="upcoming-departures__departures-list">
                  <li v-for="departure in upcomingDepartures" :key="departure.id" class="departures-list__departures-item departure-item">
                    <div class="departure-item__departure-arrival-datetime-wrapper departure-arrival-datetime-wrapper">
                      <div class="departure-datetime-wrapper">
                        <h5 class="departure-item__title">Departure</h5>
                        <p class="departure-item__departure-date">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8 7V3M16 7V3M7 11H17M5 21H19C20.1046 21 21 20.1046 21 19V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V19C3 20.1046 3.89543 21 5 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          {{ formatLocalDate(departure.departure_time) }}
                        </p>
                        <p class="departure-item__departure-time">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                            <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          {{ formatLocalTime(departure.departure_time) }}
                        </p>
                      </div>
                      <div class="arrival-datetime-wrapper">
                        <h5 class="departure-item__title">Arrival</h5>
                        <p class="departure-item__arrival-date">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8 7V3M16 7V3M7 11H17M5 21H19C20.1046 21 21 20.1046 21 19V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V19C3 20.1046 3.89543 21 5 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          {{ departure.arrival_time ? formatLocalDate(departure.arrival_time) : 'N/A' }}
                        </p>
                        <p class="departure-item__arrival-time">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                            <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          {{ departure.arrival_time ? formatLocalTime(departure.arrival_time) : 'N/A' }}
                        </p>
                      </div>
                    </div>
                    <div class="departure-item__status-wrapper">
                      <p class="departures-item__status">
                        Status: {{ departure.status }}
                      </p>
                      <p :class="departure.is_full ? 'departure-item__available-false' : 'departure-item__available-true'">
                        {{ departure.is_full ? 'Full' : 'Available' }}
                      </p>
                    </div>
                  </li>
                </ul>
              </div>
              <div v-else class="route-info__departures-no-result">
                <p class="departures-no-result__text">No upcoming departures found.</p>
              </div>
            </div>
            <div class="route-info">
              <p class="route-info__text">
                Description: {{ route.description || 'N/A' }}
              </p>
              <p class="route-info__text">
                Notes: {{ route.notes || 'N/A' }}
              </p>
              <p class="route-info__text">
                Status: {{ route.status }}
              </p>
            </div>
          </div>
          <div v-if="isAdmin" class="route-actions">
            <button @click="handleUpdate" class="route-actions__btn-update">Update</button>
            <button @click="handleDelete" class="route-actions__btn-delete">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { API, API_BASE_URL, getRoute, isUserAdmin } from '../../../frontend/static/js/api.js';

const router = useRouter();
const route = ref({});
const upcomingDepartures = ref([]);
const loading = ref(true);
const error = ref('');
const isAdmin = ref(false);
const operatingDays = ref([]);
const upcomingDeparturesLoading = ref(true);
const upcomingDeparturesSection = ref(true);

// Calendar related data
const currentMonth = ref(new Date());
const departureDates = ref([]);
const selectedDate = ref(null);
const loadingDay = ref(false);
const selectedDateDepartures = ref([]);

const routeId = window.location.pathname.split('/').pop();

// Computed properties for calendar
const startDayOffset = computed(() => {
  const firstDay = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth(), 1);
  return firstDay.getDay(); // 0 = Sunday, 1 = Monday, etc.
});

const daysInMonth = computed(() => {
  const year = currentMonth.value.getFullYear();
  const month = currentMonth.value.getMonth();
  return new Date(year, month + 1, 0).getDate();
});

/**
 * Fetches route data from the API and updates the component state accordingly.
 *
 * If the fetch is successful, it updates the route, isAdmin, and operatingDays state.
 * If the fetch fails, it sets the error state to the error message.
 * In either case, it sets the loading state to false.
 */
const loadRouteData = async () => {
  try {
    const data = await getRoute(routeId);
    route.value = data;
    isAdmin.value = await isUserAdmin();

    const allDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    operatingDays.value = route.value.operating_days && route.value.operating_days.length
      ? route.value.operating_days
      : allDays;

    loading.value = false;
  } catch (err) {
    error.value = err.message || 'Error fetching route data';
    loading.value = false;
  }
};

/**
 * Fetches the upcoming departures for a route from the API and updates the component state accordingly.
 * If the fetch is successful, it updates the upcomingDepartures state with the fetched data and sets the upcomingDeparturesLoading state to false.
 * If the fetch fails, it logs an error message to the console.
 */
const loadUpcomingDepartures = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/departures/by_route/${routeId}/upcoming`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    upcomingDepartures.value = data;
    upcomingDeparturesLoading.value = false;
  } catch (err) {
    console.error('Error loading upcoming departures:', err);
  }
};


/**
 * Fetches the departure dates for a route from the API for a specific year and month.
 * Updates the component state with the fetched data.
 * If the fetch is successful, it updates the departureDates state with the fetched data.
 * If the fetch fails, it logs an error message to the console.
 * @param {number} year - The year for which to fetch the departure dates
 * @param {number} month - The month for which to fetch the departure dates
 */
const fetchCalendarDates = async (year, month) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/departures/by_route/${routeId}/calendar/${year}/${month + 1}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    departureDates.value = data.departure_dates.map(date => new Date(date));
  } catch (err) {
    console.error('Error fetching calendar dates:', err);
  }
};

/**
 * Changes the current month for the calendar by the specified direction.
 * @param {number} direction - The direction to change the month (1 for next month, -1 for previous month)
 * @returns {Promise<void>} - A promise that resolves when the month has been changed and the calendar dates have been fetched.
 */

const changeMonth = async (direction) => {
  const newDate = new Date(currentMonth.value);
  newDate.setMonth(newDate.getMonth() + direction);
  currentMonth.value = newDate;

  const year = newDate.getFullYear();
  const month = newDate.getMonth();
  await fetchCalendarDates(year, month);
  // Clearing selected date when changing months
  selectedDate.value = null;
  selectedDateDepartures.value = [];
};

/**
 * Checks if there are any departures for a given date.
 * @param {Date} date - The date to check for departures
 * @returns {boolean} - True if there are departures for the date, false otherwise
 */
const hasDepartures = (date) => {
  return departureDates.value.some(departureDate => departureDate.toDateString() === date.toDateString());
};

/**
 * Selects a date and fetches the departures for that date.
 * @param {Date} date - The date to select
 * @returns {Promise<void>} - A promise that resolves when the selected date has been changed and the daily departures have been fetched.
 * @throws {Error} - If there is an error fetching the daily departures
 */
const selectDate = async (date) => {
  selectedDate.value = date;
  selectedDateDepartures.value = [];
  loadingDay.value = true;

  try {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    const response = await fetch(
      `${API_BASE_URL}/api/departures/by_route/${routeId}/daily/${year}/${month}/${day}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    selectedDateDepartures.value = data;
  } catch (err) {
    console.error('Error fetching daily departures:', err);
    selectedDateDepartures.value = [];
  } finally {
    loadingDay.value = false;
  }
};

/**
 * Returns a string representing the month of the given date in long format (e.g. 'January', 'February', etc.).
 * @param {Date} date - The date to format
 * @returns {string} - The formatted month string
 */
const formatMonth = (date) => {
  return date.toLocaleDateString(
    'en-US',
    {
      year: 'numeric',
      month: 'long'
    }
  );
};

/**
 * Returns a string representing the given date in the format 'Weekday, Month Day, Year'.
 * @param {Date} date - The date to format
 * @returns {string} - The formatted date string
 */
const formatDate = (date) => {
  return date.toLocaleDateString(
    'en-US',
    {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }
  )
};

/**
 * Returns a string representing the given date in the format 'HH:MM'.
 * @param {string} dateString - The date string to format
 * @returns {string} - The formatted time string
 */
const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString(
    'en-US',
    {
      hour: '2-digit',
      minute: '2-digit'
    }
  )
};

/**
 * Returns a string representing the given UTC date string in the local timezone.
 * If the utcString is falsy, returns an empty string.
 * @param {string} utcString - The UTC date string to format
 * @returns {string} - The formatted local date string
 */
const formatLocalDateTime = (utcString) => {
  if (!utcString) return '';
  const utcDate = new Date(utcString);
  const offsetMs = new Date().getTimezoneOffset() * -60 * 1000;
  const localDate = new Date(utcDate.getTime() - offsetMs);
  return localDate.toLocaleString();
};

const formatLocalDate = (utcString) => {
  if (!utcString) return '';
  const utcDate = new Date(utcString);
  const offsetMs = new Date().getTimezoneOffset() * -60 * 1000;
  const localDate = new Date(utcDate.getTime() - offsetMs);
  return localDate.toLocaleDateString();
};

const formatLocalTime = (utcString) => {
  if (!utcString) return '';
  const utcDate = new Date(utcString);
  const offsetMs = new Date().getTimezoneOffset() * -60 * 1000;
  const localDate = new Date(utcDate.getTime() - offsetMs);
  return localDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const handleUpdate = () => {
  router.push(`/routes/update/${routeId}`);
};

/**
 * Deletes the route with the given ID.
 *
 * @returns {Promise<void>} - A promise that resolves when the route has been deleted successfully.
 * @throws {Error} - If an error occurs during the deletion process.
 */
const handleDelete = async () => {
  if (confirm('Are you sure you want to delete this route?')) {
    try {
      await API.request(`/api/routes/${routeId}`, { method: 'DELETE' });
      alert('Route deleted successfully!');
      router.push('/routes');
    } catch (err) {
      alert(`Error deleting route: ${err.message || 'Unknown error'}`)
    }
  }
};

onMounted(async () => {
  await loadRouteData();
  await loadUpcomingDepartures();

  // Initializing calendar data when componenet mounts without showing it yet
  const year = currentMonth.value.getFullYear();
  const month = currentMonth.value.getMonth();
  await fetchCalendarDates(year, month);

  watch(route, async (newRoute) => {
    if (newRoute.route_number) {
      document.title = `Route ${newRoute.route_number} - Bus Management System`;
    }
  }, { immediate: true });
});
</script>

<style scoped>
/* Add your CSS here, e.g., from route.css */
.error-message { color: red; }

.route-card__title-wrapper {
  padding: 10px;
  margin-bottom: 10px;
  background-color: #022725;
  border-radius: 10px;
}

.route-card__title {
  margin: 0;
  color: rgb(255, 255, 255);
}

.route {
  background-color: #f7f7ed;
  padding: 10px;
}

.route-wrapper {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
}

.route-details-wrapper {
  width: 100%;
  margin-bottom: 20px;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  gap: 20px;
}

.route-info__basic-route-info {
  background-color: #fff;
  min-width: calc(50%);
  height: 100%;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.route-info__text {
  margin: 0;
  margin-bottom: 15px;
  border-bottom: 1px solid #ddd;
  font-size: 20px;
}

.route-info__additional-options-wrapper {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  background-color: #f6f9fa;
  border: 1px solid #d9dde0;
  border-radius: 5px;
}

.additional-options__express-wrapper {
  margin: 0;
}

.route-info__express-true,
.route-info__overnight-true,
.route-info__express-false,
.route-info__overnight-false {
  margin: 0;
  padding: 8px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border-radius: 4px;
  color: white;
  font-size: 20px;
}

.route-info__express-true, .route-info__overnight-true {
  background-color: green;
}

.route-info__express-false, .route-info__overnight-false {
  background-color: red;
}

.intermediate-stops {
  padding: 5px;
  border: 1px solid #022725;
  border-radius: 5px;
}

.intermediate-stop__item-city,
.intermediate-stop__item-distance,
.intermediate-stop__item-duration {
  margin: 0;
  margin-bottom: 5px;
  font-size: 18px;
}

.intermediate-stop__item-city {
  font-size: 20px;
  font-weight: 600;
}

.intermediate-stop__item-duration {
  margin-bottom: 0;
}

/* Calendar Container */
.calendar {
  min-width: calc(50% - 20px);
  margin: 0;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Calendar Header */
.calendar__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar__header h4 {
  margin: 0;
  color: #333;
  font-size: 22px;
  font-weight: 600;
}

.calendar__header button {
  background: #f8f9fa;
  border: 1px solid #041829;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: #495057;
  font-size: 1rem;
  transition: all 0.2s;
}

.calendar__header button:hover {
  background: #e9ecef;
  border-color: #041829;
}

/* Calendar Grid */
.calendar-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  margin-bottom: 1rem;
}

/* Day Headers */
.calendar-body__day-header {
  text-align: center;
  font-weight: 600;
  color: #6c757d;
  padding: 0.75rem 0.5rem;
  font-size: 0.875rem;
}

/* Calendar Days */
.calendar-body__day {
  display: block;
  padding: 4px 8px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  color: #495057;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.calendar-body__day:hover {
  background-color: #f8f9fa;
  border-color: #adb5bd;
}

/* Days without departures */
.calendar-body__calendar-day {
  padding: 3px;
  background-color: #c3e1f3;
  border: 1px solid #bbdefb;
  border-radius: 4px;
  outline: 1px solid #041829;
  font-weight: 600;
}

/* Days with departures */
.calendar-body__calendar-day.has-departures {
  padding: 3px;
  background-color: #083758;
  color: #e3e6e9;
  font-weight: 600;
  border: 1px solid #bbdefb;
  border-radius: 4px;
  outline: 1px solid #041829;
  cursor: pointer;
}

.calendar-body__calendar-day.has-departures:hover {
  background-color: #bbdefb;
}

/* Empty cells */
.calendar-day.empty {
  background-color: #f8f9fa;
  cursor: default;
  border-color: transparent;
}

/* Selected day */
.calendar-body__calendar-day.selected {
  background-color: #1976d2;
  color: white;
  border-color: #1565c0;
}

/* Selected date departures section */
.day-departures {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.day-departures-title {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
  font-weight: 600;
}

.day-departures__loading-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.day-departures__no-results {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  font-style: italic;
}

.upcoming-departures {
  margin: 0;
}

.upcoming-departures-wrapper {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.upcoming-departures__title {
  margin: 0;
  font-size: 20px;
}

.upcoming-departures__departures-list {
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  list-style: none;
}

.departure-item {
  padding: 10px;
  border: 1px solid white;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  cursor: pointer;
  transition: all 0.2s;
}

.departure-arrival-datetime-wrapper {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
}

.departure-datetime-wrapper,
.arrival-datetime-wrapper {
  padding: 5px;
  background-color: #bbdefb;
  border-radius:  5px;
}

.departure-item__title,
.departure-item__departure-date,
.departure-item__departure-time,
.departure-item__arrival-date,
.departure-item__arrival-time,
.departure-item__status {
  margin: 0;
  margin-bottom: 10px;
  font-size: 18px;
}

.departure-item__departure-time,
.departure-item__arrival-time {
  margin-bottom: 0;
  font-weight: 600;
}

.departure-item__status-wrapper {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 10px;
}

.departures-item__is-full {
  margin: 0;
}

.departure-item__available-false,
.departure-item__available-true {
  margin: 0;
  padding: 5px;
  color: white;
  border-radius: 5px;
}

.departure-item__available-false {
  background-color: red;
}

.departure-item__available-true {
  background-color: green;
}

.departure-item:hover {
  background-color: #f1f3f5;
  border: 1px solid #bad1e5;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
