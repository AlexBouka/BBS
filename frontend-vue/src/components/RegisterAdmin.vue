<template>
  <div class="container">
    <div class="auth-card">
      <h1 class="auth-card__title">Register Admin</h1>
      <form @submit.prevent="handleRegisterAdmin" class="auth-card__form form" id="registerAdminForm">
        <div class="form-group">
          <label for="username" class="form__label">Username *</label>
          <input
            v-model="form.username"
            type="text"
            class="form__input"
            id="username"
            required
          />
        </div>
        <div class="form-group">
          <label for="email" class="form__label">Email *</label>
          <input 
            v-model="form.email"
            type="email"
            class="form__input"
            id="email"
            required
          />
        </div>
        <div class="form-group">
          <label for="firstName" class="form__label">First Name</label>
          <input
            v-model="form.firstName"
            type="text"
            class="form__input"
            id="firstName"
            placeholder="Enter your first name (optional)"
          />
        </div>
        <div class="form-group">
          <label for="lastName" class="form__label">Last Name</label>
          <input
            v-model="form.lastName"
            type="text"
            class="form__input"
            id="lastName"
            placeholder="Enter your last name (optional)"
          />
        </div>
        <div class="form-group">
          <label for="phoneNumber" class="form__label">Phone Number</label>
          <input
            v-model="form.phoneNumber"
            type="text"
            class="form__input"
            id="phoneNumber"
            placeholder="Enter your phone number (optional)"
          />
        </div>
        <div class="form-group">
          <label for="password" class="form__label">Password *</label>
          <input
            v-model="form.password"
            @input="validatePassword"
            type="password"
            class="form__input"
            id="password"
            placeholder="Minimum 12 characters"
            minlength="12"
            required
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword" class="form__label">Confirm Password *</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="form__input"
            id="confirmPassword"
            placeholder="Confirm password (minimum 12 characters)"
            minlength="12"
            required
          />
        </div>
        <div v-if="error" class="error-message" id="errorMessage">
          <p class="error-message__text">{{ error }}</p>
        </div>
        <div class="form-actions">
          <button :disabled="loading" class="form__submit-btn">
            {{ loading ? 'Registering admin...' : 'Register Admin' }}
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
const form = ref({
  username: '',
  email: '',
  firstName: '',
  lastName: '',
  phoneNumber: '',
  password: ''
});
const confirmPassword = ref('');
const loading = ref(false);
const error = ref('');

// Check if user is admin
onMounted(async () => {
  await requireAdmin('/auth/dashboard');
})

// Real-time password validation
const validatePassword = () => {
  const password = form.value.password;
  const feedback = [];

  if (password.length < 12) {
    feedback.push('Password must be at least 12 characters long.');
  }
  if (!/[A-Z]/.test(password)) {
    feedback.push('Password must contain at least one uppercase letter.');
  }
  if (!/[a-z]/.test(password)) {
    feedback.push('Password must contain at least one lowercase letter.');
  }
  if (!/\d/.test(password)) {
    feedback.push('Password must contain at least one digit.');
  }

  error.value = feedback.length > 0 ? feedback.join(', ') : '';
};


/**
 * Handles the registration form submission for admin.
 * Validates passwords match, trims and cleans up the form data,
 * and makes a POST request to the /api/auth/register/admin endpoint.
 * If the registration is successful, redirects the user to /auth/dashboard.
 * If there is an error, displays an error message to the user.
 */
const handleRegisterAdmin = async () => {
  if (form.value.password !== confirmPassword.value) {
    error.value = 'Passwords do not match.';
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    const adminData = {
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      first_name: form.value.firstName.trim() || undefined,
      last_name: form.value.lastName.trim() || undefined,
      phone_number: form.value.phoneNumber.trim() || undefined,
    }

    Object.keys(adminData).forEach(key => {
      if (adminData[key] === undefined) {
        delete adminData[key];
      }
    });

    const result = await API.registerAdmin(adminData);
    if (result.success) {
      alert('Admin registered successfully. \nYou can now log in with the new admin credentials.');
      router.push('/auth/dashboard');
    } else {
      error.value = result.error || 'Registration failed. Please try again.';
    }
  } catch (err) {
    error.value = 'Network error. Please try again.';
    console.log('Registration error:', err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  margin: 0 auto;
  max-width: 600px;
}

.auth-card {
  padding: 20px;
}

.auth-card__title {
  font-size: 28px;
  margin-bottom: 20px;
}

.form-group input {
  width: 100%;
  margin-bottom: 10px;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 5px;
}

.form__submit-btn {
  padding: 5px 10px;
  background-color: blue;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.error-message {
  margin-bottom: 10px;
  background-color: salmon;
  padding: 10px;
  border-radius: 5px;
  border-color: red;
}

.error-message__text {
  margin: 0;
  padding: 0;
  color: white;
}

.existing-account {
  margin-top: 20px;
}

.existing-account__text {
  text-align: center;
}
</style>