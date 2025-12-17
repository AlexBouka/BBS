<template>
  <div class="container">
    <div class="bus-card">
      <h1 class="bus-card__title">Bus Details</h1>
      <div class="bus-card__bus bus">
        <p v-if="loading" class="bus__loading-text">Loading bus details...</p>
        <div v-else-if="error" class="error-message">
          <p class="error-message__text">{{ error }}</p>
        </div>
        <div v-else class="bus__details-wrapper bus-details">
          <h2 class="bus-details__title">{{ getBus.bus_number }} {{ bus.bus_name || 'Unnamed' }}</h2>
          <div class="bus-details__bus-info bus-info">
            <p class="bus-info__text">License Plate: {{ bus.license_plate }}</p>
            <p class="bus-info__text">Type: {{ bus.bus_type }}</p>
            <p class="bus-info__text">Capacity: {{ bus.capacity }}</p>
            <p class="bus-info__text">Manufacturer: {{ bus.manufacturer || 'N/A' }}</p>
            <p class="bus-info__text">Model: {{ bus.model || 'N/A' }}</p>
            <p class="bus-info__text">Year: {{ bus.year_manufactured || 'N/A' }}</p>
            <p class="bus-info__text">Status: {{ bus.status }}</p>
            <p class="bus-info__text">Accesible: {{ bus.is_accessible ? 'Yes' : 'No' }}</p>
          </div>
          <div class="bus-details__bus-info bus-info">
            <p class="bus-info__text">Amenities: {{ amenitiesFormatted }}</p>
          </div>
          <div class="bus-details__bus-info bus-info">
            <p class="bus-info__text">Description: {{ bus.description || 'N/A' }}</p>
            <p class="bus-info__text">Notes: {{ bus.notes || 'N/A' }}</p>
          </div>
          <div v-if="bus.departures && bus.departures.length" class="bus-details__bus-info bus-info">
            <h3 class="bus-info__title">Departures</h3>
            <ul class="bus-info__departures-list departures-list">
              <li v-for="departure in bus.departures" class="departures-list__departure-item departure-item">
                <p class="departure-item__route">
                  Route: {{ departure.route }} ({{ departure.origin_city }} - {{ departure.destination_city }})
                </p>
                <p class="departure-item__bus">
                  Bus: {{ departure.bus_number }}
                </p>
                <p class="departure-item__departure-time">
                  Departure: {{ formatLocalTime(departure.departure_time) }}
                </p>
                <p class="departure-item__arrival-time">
                  Arrival: {{ departure.arrival_time ? formatLocalTime(departure.arrival_time) : 'N/A' }}
                </p>
                <p class="departure-item__status">
                  Status: {{ departure.status }}
                </p>
                <p class="departure-item__is-full">
                  {{ departure.is_full ? 'Full' : 'Available' }}
                </p>
                <p class="departure-item__notes">
                  Notes: {{ departure.notes || 'None' }}
                </p>
              </li>
            </ul>
          </div>
        </div>
        <div class="bus__bus-actions bus-actions">
          <button @click="handleUpdate" class="bus-actions__btn-update">Update</button>
          <button @click="handleDelete" class="bus-actions__btn-delete">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { API, getBus, isUserAdmin } from '../../../frontend/static/js/api.js';

const router = useRouter();
const bus = ref({});
const loading = ref(true);
const error = ref('');

const busId = window.location.pathname.split('/').pop();

/**
 * Loads bus data by its ID and sets the bus state to the loaded data.
 * If there is an error, it sets the error state to the error message.
 * Finally, it sets the loading state to false.
 * @returns {Promise<void>} - A promise that resolves when the data is loaded.
 */
const loadBusData = async () => {
  try {
    const data = await getBus(busId);
    bus.value = data;
    loading.value = false;
  } catch (err) {
    error.value = err.message || 'Error fetching bus data';
    loading.value = false;
  }
};

const amenitiesFormatted = computed(() => {
  return bus.value.amenities_list ? bus.value.amenities_list.join(', ') : 'None';
});

/**
 * Returns a string representing the given UTC date string in the local timezone.
 * If the utcString is falsy, returns an empty string.
 * @param {string} utcString - The UTC date string to format
 * @returns {string} - The formatted local date string
 */
const formatLocalTime = (utcString) => {
  if (!utcString) {
    return '';
  }

  const utcDate = new Date(utcString);
  const offsetMs = new Date().getTimezoneOffset() * 60000;
  const localDate = new Date(utcDate.getTime() + offsetMs);
  return localDate.toLocaleString();
};

const handleUpdate = () => {
  router.push(`buses/update/${busId}`);
};

/**
 * Deletes a bus by its ID. If the deletion is successful, it will
 * display a success alert and redirect the user to /buses.
 * If there is an error during deletion, it will display an error
 * alert with the error message or a generic error message if the
 * error message is unavailable.
 * @returns {Promise<void>} - A promise that resolves when the deletion
 * is complete.
 */
const handleDelete = async () => {
  if (confirm('Are you sure you want to delete this bus?')) {
    try {
      await API.request(`/api/buses/${busId}`, { method: 'DELETE' });
      alert('Bus deleted successfully!');
      router.push('/buses');
    } catch (err) {
      alert(`Error deleting bus: ${error.message || 'Unknown error'}`)
    }
  }
};

onMounted(async () => {
  const adminCheck = await isUserAdmin();
  if (!adminCheck) {
    error.value = 'Access denied. Admin privileges required.';
    loading.value = false;
    return;
  }

  await loadBusData();
})
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.bus-card {
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
}

.bus-card__title {
  font-size: 24px; margin-bottom: 20px;
}

.bus-info {
  margin-bottom: 15px;
}

.bus-info__text {
  margin: 5px 0;
}

.bus-info__title {
  font-size: 18px;
  margin-bottom: 10px;
}

.bus-info__departures-list {
  list-style: none;
  padding: 0;
}

.departures-list__departure-item {
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.bus-actions {
  margin-top: 20px;
}

.bus-actions button {
  margin-right: 10px;
  padding: 10px 15px;
}

.error-message {
  color: red;
}
</style>