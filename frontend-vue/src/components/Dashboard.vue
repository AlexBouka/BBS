<template>
  <div class="container">
    <h1 class="title">Dashboard</h1>
    <div class="user-card">
      <h2 class="user-card__title">User Details</h2>
      <div class="user-card__details user-details-container">
        <p class="user-details__username">{{ user.username }}</p>
        <p class="user-details__email">{{ user.email }}</p>
        <p v-if="user.first_name && user.last_name" class="user-details__full-name">{{ user.first_name }} {{ user.last_name }}</p>
        <p class="user-details__role">{{ user.role.toLowerCase() }}</p>
        <p class="user-details__member-since">Member since: {{ user.created_at }}</p>
      </div>
      <div class="user-card__actions-wrapper">
        <button @click="updateProfile" type="button">Update Profile</button>
        <button type="button">Deactivate Account</button>
        <button type="button">Delete Account</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { API, requireAuth } from '../../../frontend/static/js/api.js';

const user = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: '',
  created_at: ''
});

onMounted(async () => {
  await requireAuth();
  const result = await API.getCurrentUser();
  console.log(result.data);
  if (result.success) {
    user.value = { ...user.value, ...result.data};
  } else {
    console.error('Failed to fetch user data:', result.error);
  }
});

const updateProfile = () => {
  router.push('/auth/update-profile');
}
</script>

<style scoped>
p {
  margin: 0;
  margin-bottom: 10px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.title {
  font-size: 26px;
  margin-bottom: 10px;
}

.user-card {
  display: flex;
  flex-direction: column;
  padding: 20px;
  border-radius: 5px;
  box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 24px;
  background-color: #fff;
}

.user-details-container {
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 15px;
}

.user-card__actions-wrapper {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 10px;
}
</style>