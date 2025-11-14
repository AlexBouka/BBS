<template>
  <div id="app">
    <Header />  <!-- Global header displayed on all pages -->
    <router-view />  <!-- This is where routed components will be displayed -->
  </div>
</template>

<script>
import Header from './components/Header.vue';

export default {
  name: 'App',
  components: {
    Header
  }
};
</script>

<style>
/* Add global styles if needed */
</style>
