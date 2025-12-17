<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-header__title">Buses</h1>
      <div class="page-header__actions">
        <button @click="$router.push('/buses/create/')" class="actions__create-btn">Create Bus</button>
      </div>
    </div>

    <!-- Bus Filtering -->
    <div class="filter-card">
      <h3 class="filter-card__title">Filter Buses</h3>
      <div class="filter-card__filters filters">
        <div class="filters__form-group form-group">
          <label for="filterBusNumber">Bus Number</label>
          <input
            v-model="filters.bus_number"
            type="text"
            id="filterBusNumber"
            placeholder="Enter bus number"
          />
        </div>
        <div class="filters__form-group form-group">
          <label for="filterManufacturer">Manufacturer</label>
          <input
            v-model="filters.manufacturer"
            type="text"
            id="filterManufacturer"
            placeholder="Enter manufacturer"
          />
        </div>
        <div class="filters__form-group form-group">
          <label for="filterModel">Model</label>
          <input
            v-model="filters.model"
            type="text"
            id="filterModel"
            placeholder="Enter model"
          />
        </div>
        <div class="filters__form-group form-group">
          <label for="filterBusType">Bus Type</label>
          <select v-model="filters.bus_type" id="filterBusType">
            <option value="">All types</option>
            <option value="STANDARD">Standard</option>
            <option value="MINIBUS">Minibus</option>
            <option value="LUXURY">Luxury</option>
            <option value="SLEEPER">Sleeper</option>
            <option value="MINIBUS_LUXURY">Minibus Luxury</option>
          </select>
        </div>
        <div class="filters__form-group form-group">
          <label for="filterStatus">Status</label>
          <select v-model="filters.status" id="filterStatus">
            <option value="">All statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="MAINTENANCE">Maintenance</option>
            <option value="INACTIVE">Inactive</option>
            <option value="DELETED">Deleted</option>
          </select>
        </div>
        <div class="filters__form-group form-group">
          <button @click="applyFilters" class="filter__apply-btn">Apply Filters</button>
          <button @click="clearFilters" class="filter__clear-btn">Clear Filters</button>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <p class="loading-state__text">Loading buses...</p>
    </div>

    <!-- No results -->
    <div v-else-if="buses.length === 0" class="no-results">
      <p class="no-results__text">No buses found.</p>
    </div>

    <!-- Buses -->
    <div v-else class="buses-container">
      <div v-for="bus in buses" class="bus-card">
        <div class="bus-card__header bus-header">
          <h2 class="bus-header__title">{{ bus.bus_number }}</h2>
          <p class="bus-header__license">{{ bus.license_plate }}</p>
        </div>
        <div class="bus-card__badges badges">
          <span :class="`bus-badges__badge-status-${bus.status.toLowerCase()}`">{{ bus.status }}</span>
          <span v-if="bus.is_accessible" class="bus-badges__badge-accessible">ACCESSIBLE</span>
        </div>
        <div class="bus-card__bus-details bus-details">
          <div class="bus-detail-item">
            <span class="bus-detail-item__label">Type</span>
            <span class="bus-detail-item__value">{{ bus.bus_type }}</span>
          </div>
          <div class="bus-detail-item">
            <span class="bus-detail-item__label">Capacity</span>
            <span class="bus-detail-item__value">{{ bus.capacity }}</span>
          </div>
          <div class="bus-detail-item">
            <span class="bus-detail-item__label">Amenities</span>
            <span class="bus-detail-item__value">{{ bus.amenities_list.join(', ') || 'None' }}</span>
          </div>
        </div>
        <div class="bus-card__bus-actions bus-actions">
          <button @click="viewBus(bus.id)" class="bus-actions__view-bus-btn">View Details</button>
        </div>
      </div>
    </div>
    <div class="pagination-container">
      <button :disabled="currentPage === 1" @click="loadBuses(currentPage - 1)" class="pagination-btn previous-btn"><<<</button>
      <span class="pagination-info">Page {{ currentPage }} | Showing {{ startItem }}-{{ endItem }}</span>
      <button :disabled="!hasMore" @click="loadBuses(currentPage + 1)" class="pagination-btn next-btn">>>></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { API, requireAdmin } from '../../../frontend/static/js/api.js';

const router = useRouter();
const buses = ref([]);
const loading = ref(true);
const currentPage = ref(1);
const pageSize = 16;
const hasMore = ref(false);
const isAdmin = ref(false);
const filters = ref({
  bus_number: '',
  manufacturer: '',
  model: '',
  bus_type: '',
  status: ''
});

const startItem = computed(() => (currentPage.value - 1) * pageSize + 1);
const endItem = computed(() => startItem.value + pageSize - 1);

/**
 * Loads a page of buses.
 * @param {number} [page=1] - The page of buses to load.
 * @returns {Promise<void>} - A promise that resolves when the buses have been loaded.
 */
const loadBuses = async (page = 1) => {
  loading.value = true;
  try {
    const offset = (page - 1) * pageSize;
    const params = new URLSearchParams({
      offset: offset.toString(),
      limit: pageSize.toString()
    });

    if (filters.value.bus_number) {
      params.append('bus_number', filters.value.bus_number);
    }
    if (filters.value.manufacturer) {
      params.append('manufacturer', filters.value.manufacturer);
    }
    if (filters.value.model) {
      params.append('model', filters.value.model);
    }
    if (filters.value.bus_type) {
      params.append('type', filters.value.bus_type);
    }
    if (filters.value.status) {
      params.append('status', filters.value.status);
    }

    const data = await API.request(`/api/buses/?${params.toString()}`);
    buses.value = data;
    currentPage.value = page;
    hasMore.value = data.length === pageSize;
  } catch (err) {
    console.error('Error loading buses:', err);
    buses.value = [];
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => loadBuses(1);

const clearFilters = () => {
  filters.value = {
    bus_number: '',
    manufacturer: '',
    model: '',
    bus_type: '',
    status: ''
  };
  loadBuses(1);
};

const viewBus = (busId) => router.push(`/buses/${busId}`);

onMounted(async () => {
  await requireAdmin('/dashboard');
  await loadBuses();
});
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
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.filter-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-apply {
  background: #28a745;
  color: white;
}

.btn-clear {
  background: #dc3545;
  color: white;
}

.loading-state, .no-results {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.buses-container {
  display: grid;
  gap: 1rem;
}

.bus-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.bus-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.bus-card__header {
  margin-bottom: 1rem;
}

.bus-card__title {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.bus-card__license {
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
}

.badges {
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

.badge-status-maintenance {
  background: #fff3cd;
  color: #856404;
}

.badge-status-inactive {
  background: #f8d7da;
  color: #721c24;
}

.badge-accessible {
  background: #d1ecf1;
  color: #0c5460;
}

.bus-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem; margin: 1rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 5px;
}

.bus-detail-item {
  text-align: center;
}

.bus-detail-item__label {
  display: block;
  color: #666;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.bus-detail-item__value {
  display: block;
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.bus-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

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

</style>