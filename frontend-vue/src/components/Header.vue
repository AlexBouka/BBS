<template>
  <header class="header">
    <nav class="nav">
      <div class="nav__logo">
        <h1>Bus Booking System</h1>
      </div>
      <ul class="nav__links">
        <li v-if="isAuthenticated">
          <a href="#" @click.prevent="logout">Logout</a>
        </li>
        <li v-else>
          <router-link to="/auth/login">Login</router-link>
        </li>
        <li><router-link to="/routes">Routes</router-link></li>
        <!-- Add more links as needed -->
      </ul>
    </nav>
  </header>
</template>

<script>
import { ref, onMounted } from 'vue';
import { API, TokenManager } from '../../../frontend/static/js/api.js';

export default {
  name: 'Header',
  setup() {
    const isAuthenticated = ref(false);

    const checkAuth = () => {
      isAuthenticated.value = TokenManager.isLoggedIn();
    };

    const logout = async () => {
      try {
        await API.logout();
        checkAuth();
        window.location.href = '/auth/login'; // Redirect after logout
      } catch (error) {
        console.error('Logout failed:', error);
      }
    };

    onMounted(() => {
      checkAuth();
    });

    return {
      isAuthenticated,
      logout
    };
  }
};
</script>

<style scoped>
.header {
  background-color: #021924;
  color: white;
  padding: 1rem;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav__logo h1 {
  margin: 0;
}

.nav__links {
  list-style: none;
  display: flex;
  gap: 1rem;
}

.nav__links a {
  padding: 10px;
  border-radius: 8px;
  color: white;
  text-decoration: none;
  font-size: 18px;
  transition: background-color 0.2 ease;
}

.nav__links a:hover {
  background-color: #074355;
}

.nav__links a:focus {
  background-color: #074355;
  outline: 2px solid rgb(97, 190, 233);
}

.nav__links a.router-link-active {
  background-color: #033442;
}
</style>