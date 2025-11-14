<template>
  <div class="container">
    <div class="auth-card">
      <h1 class="auth-card__title">Register</h1>
      <form @submit.prevent="handleRegister" class="auth-card__form form" id="registerForm">
        <div class="form-group">
          <label for="username" class="form__label">Username *</label>
          <input
            v-model="form.username"
            type="text"
            class="form__input"
            id="username"
            minlength="5"
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
            placeholder="Enter your email"
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
          <label for="lastName" class="form__label"></label>
          <input
            v-model="form.lastName"
            type="text"
            class="form__input"
            id="LastName"
            placeholder="Enter your last name (optional)"
          />
        </div>
        <div class="form-group">
          <label for="phoneNumber" class="form__label"></label>
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
            placeholder="Minimum 8 characters"
            minlength="8"
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
            placeholder="Minimum 8 characters"
            minlength="8"
            required
          />
        </div>
        <div v-if="error" class="error-message" id="errorMessage">
          <p class="error-message__text">{{ error }}</p>
        </div>
        <div class="form-actions">
          <button :disabled="loading" type="submit" class="form__submit-btn" id="registerBtn">
            {{ loading ? 'Creating account...' : 'Register' }}
          </button>
        </div>
      </form>
      <div class="existing-account">
        <p class="existing-account__text">
          Already have an account? <router-link to="/auth/login">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { API, redirectIfAuthenticated } from '../../../frontend/static/js/api.js';

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
const error = ref('');
const loading = ref(false);

// Check if already authenticated on mount
onMounted(() => {
  redirectIfAuthenticated();
});

// Real-time password validation
const validatePassword = () => {
  const password = form.value.password;
  const feedback = [];

  if (password.length < 8) {
    feedback.push('Password must be at least 8 characters long.');
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
 * Handles the registration form submission.
 * Validates passwords match, trims and cleans up the form data,
 * and makes a POST request to the /api/auth/register endpoint.
 * If the registration is successful, redirects the user to /auth/login.
 * If there is an error, displays an error message to the user.
 */
const handleRegister = async () => {
  // Validate passwords match
  if (form.value.password !== confirmPassword.value) {
    error.value = 'Passwords do not match.';
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    const formData = {
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      first_name: form.value.firstName.trim() || undefined,
      last_name: form.value.lastName.trim() || undefined,
      phone_number: form.value.phoneNumber.trim() || undefined
    };

    // Clean undefined values
    Object.keys(formData).forEach(key => {
      if (formData[key] === undefined) {
        delete formData[key];
      }
    });

    const result = await API.register(formData);

    if (result.success) {
      alert('Account created successfully! Please log in.');
      router.push('/auth/login');
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