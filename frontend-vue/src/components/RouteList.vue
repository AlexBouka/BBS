<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-header__title">Routes</h1>
      <div class="header-actions">
        <button @click="$router.push('/routes/create/')" class="header-actions__btn">Create Route</button>
      </div>
    </div>

    <!-- Route filtering -->
    <div class="filter-card">
      <h3 class="filter-card__title">Filter Routes</h3>
      <div class="filter-card__filters filters">
        <div class="form-group">
          <label for="filterOriginCity">Origin City</label>
          <input v-model="filters.origin" type="text" id="filterOriginCity" placeholder="Enter origin city">
        </div>
        <div class="form-group">
          <label for="filterDestinationCity">Destination City</label>
          <input v-model="filters.destination" type="text" id="filterDestinationCity" placeholder="Enter destination city">
        </div>
        <div class="form-group">
          <label for="filterStatus">Status</label>
          <select v-model="filters.status" id="filterStatus">
            <option value="">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="SEASONAL">Seasonal</option>
            <option value="DELETED">Deleted</option>
          </select>
        </div>
        <div class="filter-card__actions actions">
          <button @click="applyFilters" class="btn btn-apply">Apply Filters</button>
          <button @click="clearFilters" class="btn btn-clear">Clear Filters</button>
        </div>
      </div>
    </div>

    <!-- Loading || No results || Routes -->
    <div v-if="loading" class="loading-state">
      <p class="loading-state__text">Loading routes...</p>
    </div>
    <div v-else-if="routes.length === 0" class="no-results">
      <p class="no-results__text">No routes found.</p>
    </div>
    <div v-else class="routes-container">

      <!--  Each route card -->
      <div v-for="route in routes" :key="route.id" class="route-card">
        <div class="route-card__header">
          <h2 class="route-card__title">{{ route.route_number }}</h2>
          <p class="route-card__path">{{ route.origin_city }} <span class="arrow">-></span> {{ route.destination_city }}</p>
        </div>
        <div class="route-card__badges badges">
          <span :class="`badge badge-status-${route.status}`">{{ route.status.toUpperCase() }}</span>
          <span v-if="route.is_express" class="badge badge-express">EXPRESS</span>
          <span v-if="route.is_overnight" class="badge badge-overnight">OVERNIGHT</span>
        </div>
        <div class="route-card__route-details route-details">
          <div class="route-detail-item">
            <span class="route-detail-item__label">Distance </span>
            <span class="route-detail-item__value">{{ route.distance_km }}</span>
          </div>
          <div class="route-detail-item">
            <span class="route-detail-item__label">Duration </span>
            <span class="route-detail-item__value">{{ route.estimated_duration_hours }}</span>
          </div>
          <div class="route-detail-item">
            <span class="route-detail-item__label">Price </span>
            <span class="route-detail-item__value">{{ route.base_price.toFixed(2) }}</span>
          </div>
          <div class="route-card__route-actions route-actions">
            <button @click="viewRoute(route.id)" class="route-actions__view-route-btn">View Details</button>
            <button @click="bookSeat(route.id)" class="route-actions__book-seat-btn">Book Now</button>
          </div>
        </div>
      </div>
    </div>
    <div class="pagination-container">
      <button :disabled="currentPage === 1" @click="loadRoutes(currentPage - 1)" class="pagination-btn previous-btn"><<</button>
      <span class="pagination-info">Page {{ currentPage }} | Showing {{ startItem }}-{{ endItem }}</span>
      <button :disabled="!hasMore" @click="loadRoutes(currentPage + 1)" class="pagination-btn next-btn">>></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { API, API_BASE_URL } from '../../../frontend/static/js/api.js';

const router = useRouter();
const routes = ref([]);
const loading = ref(true);
const currentPage = ref(1);
const pageSize = 10;
const hasMore = ref(false);
const filters = ref({
  origin: '',
  destination: '',
  status: ''
});

const startItem = computed(() => (currentPage.value - 1) * pageSize + 1);
const endItem = computed(() => startItem.value + pageSize - 1);

const loadRoutes = async (page = 1) => {
  loading.value = true;
  try {
    const offset = (page - 1) * pageSize;
    const params = new URLSearchParams({
      offset: offset.toString(),
      limit: pageSize.toString()
    });

    if (filters.value.origin) {
      params.append('origin_city', filters.value.origin);
    }
    if (filters.value.destination) {
      params.append('destination_city', filters.value.destination);
    }
    if (filters.value.status) {
      params.append('status', filters.value.status);
    }

    const response = await fetch(`${API_BASE_URL}/api/routes?${params.toString()}`);
    if (!response.ok) {
      throw new Error('Failed to fetch routes');
    }

    const data = await response.json();
    routes.value = data;
    currentPage.value = page;
    hasMore.value = data.length === pageSize;
  } catch (error) {
    console.error('Error loading routes:', error);
    routes.value = [];
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => {
  loadRoutes(1);
};

const clearFilters = () => {
  filters.value = { origin: '', destination: '', status: '' }
  loadRoutes(1);
};

const viewRoute = (routeId) => {
  router.push(`/routes/${routeId}`);
}

const bookSeat = (routeId) => {
  console.log(`Booking seat for route ID: ${routeId}`);
}

onMounted(async () => {
  await loadRoutes();
  document.title = 'Route List - Booking System';
})
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 10px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  color: white;
  font-size: 25px;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.header-actions__btn {
  padding: 10px 20px;
  background-color: #0b7a11;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
  transition: background-color 0.3s ease;
}

.header-actions__btn:hover {
  background-color: #0faa17;
}

.header-actions__btn:focus {
  outline: 2px #e0e6e0 solid;
}

.header-actions__btn:active {
  background-color: #064b0a;
}

.filter-card {
  background: rgb(78, 118, 150);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: white;
  font-size: 22px;
}

.filters {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.filters:last-child() {
  margin-left: auto;
}

/* .filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
} */

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 18px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
  font-size: 18px;
}

.form-group input:focus {
  outline: none;
  border-color: #021920
}

.actions {
  padding-top: 25px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.actions button {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 18px;
}

.btn-apply {
  background-color: #23c594;
  color: white;
  transition: background-color 0.2s ease-in-out;
}

.btn-apply:hover {
  background-color: #4fdfb4;
}

.btn-apply:focus {
  outline: 2px #e0e6e0 solid;
}

.btn-apply:active {
  background-color: #369679;
}

.loading-state,
.no-results {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.routes-container {
  display: grid;
  gap: 1rem;
}

.route-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.route-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.route-title {
  flex: 1;
}

.route-title h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.route-number {
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
}

.route-path {
  color: #666;
  font-size: 1.1rem;
  margin: 0.5rem 0;
}

.route-path .arrow {
  color: #667eea;
  margin: 0 0.5rem;
}

.route-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-status-active {
  background: #d4edda;
  color: #155724;
}

.badge-status-inactive {
  background: #f8d7da;
  color: #721c24;
}

.badge-express {
  background: #fff3cd;
  color: #856404;
}

.badge-overnight {
  background: #d1ecf1;
  color: #0c5460;
}

.route-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 5px;
}

.route-detail-item {
  text-align: center;
}

.route-detail-item .label {
  display: block;
  color: #666;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.route-detail-item .value {
  display: block;
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.route-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding: 1rem;
}

.pagination-info {
  margin: 0 1rem;
  color: #666;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #ccc;
  color: #ccc;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-number {
  padding: 0.5rem 0.75rem;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-number:hover {
  border-color: #667eea;
  color: #667eea;
}

.page-number.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}
</style>