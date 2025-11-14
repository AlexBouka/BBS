<template>
  <div class="container">
    <div class="auth-card">
      <h1 class="auth-card__title">Login</h1>

      <!-- This form is handled by JavaScript-->
      <form @submit.prevent="handleLogin" id="loginForm" class="auth-card__form">
        <div class="form-group">
          <label for="usernameOrEmail" class="form__label">Username or Email</label>
          <input v-model="usernameOrEmail" type="text" id="usernameOrEmail" class="form__input" required>
        </div>
        <div class="form-group">
          <label for="password" class="form__label">Password</label>
          <input v-model="password" type="password" id="password" class="form__input" required>
        </div>
        <div v-if="error" class="error-message" id="errorMessage">{{ error }}</div>
        <button :disabled="loading" type="submit" class="form__submit-btn" id="loginBtn">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { API, redirectIfAuthenticated } from '../../../frontend/static/js/api.js';

const router = useRouter();
const usernameOrEmail = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

// Check if user is already authenticated on component mount
onMounted(() => {
  redirectIfAuthenticated();
  document.title = 'Login - Bus Management System';
});

const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  try {
    const result = await API.login(usernameOrEmail.value, password.value);
    if (result.success) {
      router.push('/auth/dashboard');
    } else {
      error.value = result.error || 'Login failed. Please try again.';
      loading.value = false;
    }
  } catch (err) {
    error.value = err.message || 'An unexpected error occurred.';
    loading.value = false;
  }
}
</script>

<style scoped>
.container {
  margin: 0 auto;
  max-width: 600px;
  background-color: #045d74;
  border-radius: 0px 0px 10px 10px;
}

.auth-card {
  padding: 20px;
}

.auth-card__title {
  font-size: 28px;
  margin-bottom: 20px;
  color: white;
}

.form-group {
  padding: 0;
  margin-bottom: 10px;
}

.form__label {
  display: block;
  margin-bottom: 5px;
  color: white;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
}

.form__input:not(:placeholder-shown) {
  background-color: rgb(220, 235, 247);
}

.form__input:hover {
  border-color: rgb(121, 187, 241);
  box-shadow: rgba(218, 222, 226, 0.2) 0px 8px 24px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form__submit-btn {
  padding: 5px 10px;
  background-color: rgb(26, 147, 247);
  font-size: 20px;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.form__submit-btn:hover {
  background-color: rgb(33, 133, 214);
  box-shadow: rgba(230, 232, 235, 0.2) 0px 8px 24px;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.form__submit-btn:active {
  background-color: rgb(8, 72, 124);
  box-shadow: rgba(232, 234, 236, 0.2) 0px 8px 24px;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
}

.form__submit-btn:disabled {
  background-color: rgb(113, 114, 116);
  cursor: not-allowed;
}

.error-message {
  padding: 8px;
  margin-bottom: 10px;
  color: white;
  background-color: salmon;
  border-radius: 5px;
  border-color: red;
}
</style>