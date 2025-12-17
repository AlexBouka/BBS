
<template>
  <div class="container">
    <h1 class="title">Departures</h1>
    
    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label for="routeSelect">Select Route:</label>
        <select v-model="selectedRouteId" @change="loadRoutes" id="routeSelect">
          <option value="">Select Route</option>
          <option v-for="route in routes" :key="route.id" :value="route.id">
            {{ route.route_number }} ({{ route.origin_city }} - {{ route.destination_city }})
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label for="viewType">View Type:</label>
        <select v-model="viewType" @change="loadDepartures" id="viewType">
          <option value="upcoming">Upcoming (7 days)</option>
          <option value="daily">Specific Day</option>
        </select>
      </div>
      <div v-if="viewType === 'daily'" class="filter-group">
        <label for="datePicker">Select Date:</label>
        <input v-model="selectedDate" type="date" @change="loadDepartures" id="datePicker">
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-state__text">Loading departures...</p>
    </div>

    <!-- Departures List -->
    <div v-else-if="departures && departures.length" class="departures-list">
      <div v-for="departure in departures" :key="departure.id" class="departure-item">
        <h3 class="departure-info__date-title">{{ formatDateFull(departure.departure_time) }}</h3>
        <div class="departure-info">
          <div class="departure-info__departure-times">
            <h4 class="departure-times__title">{{ departure.origin_city }}</h4>
            <p class="departure-date">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 7V3M16 7V3M7 11H17M5 21H19C20.1046 21 21 20.1046 21 19V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V19C3 20.1046 3.89543 21 5 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ formatDate(departure.departure_time) }}
            </p>
            <p class="departure-time">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ formatTime(departure.departure_time) }}
            </p>
          </div>
          <div class="departure-info__arrow-section arrow-section">
            <p class="arrow-section__duration">
              {{ calculateDuration(departure.departure_time, departure.arrival_time) }}
            </p>
            <div class="arrow-section__arrow">
              <svg width="100" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="departure-info__arrival-times">
            <h4 class="arrival-times__title">{{ departure.destination_city }}</h4>
            <p v-if="departure.arrival_time" class="arrival-date">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 7V3M16 7V3M7 11H17M5 21H19C20.1046 21 21 20.1046 21 19V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V19C3 20.1046 3.89543 21 5 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ formatDate(departure.arrival_time) }}
            </p>
            <p v-if="departure.arrival_time" class="arrival-time">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ formatTime(departure.arrival_time) }}
            </p>
            <p v-else class="arrival-na">Arrival: N/A</p>
          </div>
          <div class="departure-item__amenities-wrapper amenities-wrapper">
            <ul class="amenities-wrapper__amenities-list amenities-list">
              <li class="amenities-list__amenities-item amenities-item">
                <span :class="departure.has_wifi ? 'amenities-item__text-active' : 'amenities-item__text-inactive'">
                  <svg width="36px" height="36px" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1.33309 8.07433C0.92156 8.44266 0.886539 9.07485 1.25487 9.48638C1.62319 9.89791 2.25539 9.93293 2.66691 9.5646L1.33309 8.07433ZM21.3331 9.5646C21.7446 9.93293 22.3768 9.89791 22.7451 9.48638C23.1135 9.07485 23.0784 8.44266 22.6669 8.07433L21.3331 9.5646ZM12 19C11.4477 19 11 19.4477 11 20C11 20.5523 11.4477 21 12 21V19ZM12.01 21C12.5623 21 13.01 20.5523 13.01 20C13.01 19.4477 12.5623 19 12.01 19V21ZM14.6905 17.04C15.099 17.4116 15.7315 17.3817 16.1031 16.9732C16.4748 16.5646 16.4448 15.9322 16.0363 15.5605L14.6905 17.04ZM18.0539 13.3403C18.4624 13.7119 19.0949 13.682 19.4665 13.2734C19.8381 12.8649 19.8082 12.2324 19.3997 11.8608L18.0539 13.3403ZM7.96372 15.5605C7.55517 15.9322 7.52524 16.5646 7.89687 16.9732C8.2685 17.3817 8.90095 17.4116 9.3095 17.04L7.96372 15.5605ZM4.60034 11.8608C4.19179 12.2324 4.16185 12.8649 4.53348 13.2734C4.90511 13.682 5.53756 13.7119 5.94611 13.3403L4.60034 11.8608ZM2.66691 9.5646C5.14444 7.34716 8.41371 6 12 6V4C7.90275 4 4.16312 5.54138 1.33309 8.07433L2.66691 9.5646ZM12 6C15.5863 6 18.8556 7.34716 21.3331 9.5646L22.6669 8.07433C19.8369 5.54138 16.0972 4 12 4V6ZM12 21H12.01V19H12V21ZM12 16C13.0367 16 13.9793 16.3931 14.6905 17.04L16.0363 15.5605C14.9713 14.5918 13.5536 14 12 14V16ZM12 11C14.3319 11 16.4546 11.8855 18.0539 13.3403L19.3997 11.8608C17.4466 10.0842 14.8487 9 12 9V11ZM9.3095 17.04C10.0207 16.3931 10.9633 16 12 16V14C10.4464 14 9.02872 14.5918 7.96372 15.5605L9.3095 17.04ZM5.94611 13.3403C7.54544 11.8855 9.66815 11 12 11V9C9.15127 9 6.55344 10.0842 4.60034 11.8608L5.94611 13.3403Z" fill="#000000"/>
                  </svg>
                </span>
              </li>
              <li class="amenities-list__amenities-item amenities-item">
                <span :class="departure.has_ac ? 'amenities-item__text-active' : 'amenities-item__text-inactive'">
                  <svg width="30px" height="30px" viewBox="0 0 1024 1024" fill="#000000" class="icon"  version="1.1" xmlns="http://www.w3.org/2000/svg">
                    <path d="M383.2 941.6c-4 0-6.4-0.8-9.6-2.4-14.4-9.6-82.4-60-25.6-160 15.2-27.2 19.2-48.8 13.6-66.4-6.4-20-27.2-28-27.2-28-9.6-4-14.4-15.2-10.4-24.8 3.2-8 9.6-12.8 17.6-12.8 2.4 0 4.8 0.8 7.2 1.6 3.2 0 36.8 14.4 50.4 50.4 10.4 28.8 4.8 62.4-16.8 100-40 70.4 2.4 101.6 11.2 107.2 8.8 4.8 12 16.8 7.2 26.4-4.8 6.4-12 8.8-17.6 8.8z m129.6-42.4c-4 0-6.4-0.8-9.6-2.4-28.8-16.8-69.6-68.8-24-150.4 13.6-24.8 17.6-44.8 12-60-5.6-17.6-24-24.8-24-24.8-10.4-4-15.2-14.4-11.2-24.8 3.2-8 9.6-12.8 17.6-12.8 2.4 0 4.8 0.8 7.2 1.6 8 3.2 36 16 47.2 48 9.6 27.2 4.8 58.4-15.2 92.8-38.4 68.8 8 96.8 10.4 97.6 4 2.4 7.2 6.4 8.8 11.2 1.6 4.8 0.8 10.4-1.6 15.2-4.8 6.4-12 8.8-17.6 8.8z m-265.6 0c-4 0-6.4-0.8-9.6-2.4-28.8-16.8-69.6-68.8-24-150.4 13.6-24.8 17.6-44.8 12-60-5.6-17.6-24-24.8-24-24.8-10.4-4-15.2-14.4-11.2-24.8 3.2-8 9.6-12.8 17.6-12.8 2.4 0 4.8 0.8 7.2 1.6 8 3.2 36 16.8 47.2 48 9.6 27.2 4 58.4-15.2 93.6-38.4 68.8 8 96.8 10.4 97.6 4 2.4 7.2 6.4 8.8 11.2 1.6 4.8 0.8 10.4-1.6 15.2-4 5.6-12 8-17.6 8z m487.2-71.2c-6.4 0-11.2-2.4-15.2-6.4s-6.4-9.6-6.4-15.2c0-8.8 5.6-16.8 13.6-20.8h0.8v-43.2l-40.8 23.2v0.8c0 6.4-2.4 14.4-10.4 18.4-3.2 2.4-7.2 3.2-11.2 3.2-8 0-15.2-4-18.4-10.4-3.2-5.6-4-11.2-2.4-16.8 1.6-5.6 4.8-10.4 10.4-12.8 3.2-2.4 7.2-3.2 10.4-3.2 4 0 8 0.8 11.2 3.2l36.8-20.8-36-20.8c-4.8 1.6-8.8 2.4-12 2.4-4 0-7.2-0.8-10.4-2.4-9.6-6.4-13.6-20-8-29.6 4-6.4 11.2-10.4 19.2-10.4 4 0 8 0.8 11.2 3.2 6.4 4 10.4 10.4 10.4 18.4v0.8L728 712v-43.2h-0.8c-8-4-13.6-12-13.6-20.8 0-12 9.6-21.6 21.6-21.6 6.4 0 12 2.4 16 6.4s6.4 9.6 6.4 15.2c0 7.2-4 14.4-11.2 18.4H744v41.6l35.2-20v-0.8c0-6.4 2.4-14.4 10.4-18.4 3.2-2.4 7.2-3.2 11.2-3.2 8 0 15.2 4 18.4 10.4 3.2 5.6 4 11.2 2.4 16.8-1.6 5.6-4.8 10.4-10.4 12.8-3.2 2.4-7.2 3.2-10.4 3.2-4 0-8-0.8-11.2-3.2l-36.8 20.8 36 20.8c4.8-1.6 8.8-2.4 12-2.4 4 0 7.2 0.8 10.4 2.4 9.6 6.4 13.6 20 8 29.6-4 6.4-11.2 10.4-19.2 10.4-4 0-8-0.8-11.2-3.2-6.4-4-10.4-10.4-10.4-18.4v-0.8L744 745.6v41.6h0.8c7.2 3.2 11.2 10.4 11.2 18.4 0 12.8-9.6 22.4-21.6 22.4zM152 575.2c-60.8 0-109.6-48.8-109.6-109.6V204.8c0-60.8 48.8-109.6 109.6-109.6h721.6c60.8 0 109.6 48.8 109.6 109.6v260.8c0 60.8-48.8 109.6-109.6 109.6H152z m-11.2-432c-28.8 0-52 24-52 54.4v278.4c0 29.6 23.2 54.4 52 54.4h743.2c28.8 0 52-24 52-54.4V197.6c0-29.6-23.2-54.4-52-54.4H140.8z m21.6 312c-10.4 0-19.2-8.8-19.2-19.2 0-10.4 8.8-19.2 19.2-19.2h682.4c10.4 0 19.2 8.8 19.2 19.2 0 10.4-8.8 19.2-19.2 19.2H162.4z m0-80.8c-10.4 0-19.2-8.8-19.2-19.2S152 336 162.4 336h682.4c10.4 0 19.2 8.8 19.2 19.2 0 10.4-8.8 19.2-19.2 19.2H162.4z" fill="" />
                  </svg>
                </span>
              </li>
              <li class="amenities-list__amenities-item amenities-item">
                <span :class="departure.has_tv ? 'amenities-item__text-active' : 'amenities-item__text-inactive'">
                  <div class="svg-wrapper">
                    <svg width="36px" height="36px" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M7 21L12 17L17 21M7.8 17H16.2C17.8802 17 18.7202 17 19.362 16.673C19.9265 16.3854 20.3854 15.9265 20.673 15.362C21 14.7202 21 13.8802 21 12.2V7.8C21 6.11984 21 5.27976 20.673 4.63803C20.3854 4.07354 19.9265 3.6146 19.362 3.32698C18.7202 3 17.8802 3 16.2 3H7.8C6.11984 3 5.27976 3 4.63803 3.32698C4.07354 3.6146 3.6146 4.07354 3.32698 4.63803C3 5.27976 3 6.11984 3 7.8V12.2C3 13.8802 3 14.7202 3.32698 15.362C3.6146 15.9265 4.07354 16.3854 4.63803 16.673C5.27976 17 6.11984 17 7.8 17Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                </span>
              </li>
              <li class="amenities-list__amenities-item amenities-item">
                <span :class="departure.has_charging_ports ? 'amenities-item__text-active' : 'amenities-item__text-inactive'">
                  <svg width="30px" height="30px" viewBox="-0.5 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7.37583 7.99997H3C2.72 7.99997 2.5 8.21997 2.5 8.49997V16.5C2.5 16.78 2.72 17 3 17H9.30747M11.3075 7.99994L17.65 7.99997C17.93 7.99997 18.15 8.21997 18.15 8.49997V16.5C18.15 16.78 17.92 17 17.65 17H13.322" stroke="#0F0F0F" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M20.38 10.81H21C21.28 10.81 21.5 11.03 21.5 11.31V13.69C21.5 13.97 21.28 14.19 21 14.19H20.38" stroke="#0F0F0F" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M10.325 6L7.47871 12.0142C7.36924 12.24 7.53343 12.5 7.78659 12.5H12.8634C13.1166 12.5 13.2808 12.76 13.1713 12.9858L10.325 19" stroke="#0F0F0F" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </li>
              <li class="amenities-list__amenities-item amenities-item">
                <span :class="departure.has_refreshments ? 'amenities-item__text-active' : 'amenities-item__text-inactive'">
                  <svg fill="#000000" height="30px" width="30px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
                    viewBox="0 0 512 512" xml:space="preserve">
                    <g>
                      <g>
                        <path d="M236.36,264.268h-3.09c-6.607,0-11.963,5.356-11.963,11.963c0,6.607,5.356,11.963,11.963,11.963h3.09
                          c6.607,0,11.963-5.356,11.963-11.963C248.322,269.624,242.967,264.268,236.36,264.268z"/>
                      </g>
                    </g>
                    <g>
                      <g>
                        <path d="M448.273,211.297h-31.138h-33.136c0.324-2.747,0.502-5.52,0.502-8.314c0-17.124-6.217-33.439-17.31-46.142l91.073-138.297
                          c3.634-5.518,2.107-12.936-3.412-16.57c-5.516-3.635-12.936-2.105-16.57,3.412l-89.76,136.303
                          c-7.027-3.926-14.69-6.624-22.646-7.959c0.227-2.304,0.354-4.625,0.354-6.96c0-38.726-31.506-70.232-70.232-70.232
                          c-38.726,0-70.232,31.506-70.232,70.232c0,2.335,0.128,4.655,0.354,6.959c-33.219,5.551-58.624,34.484-58.624,69.255
                          c0,2.794,0.178,5.567,0.502,8.314H94.863H63.725c-6.607,0-11.963,5.356-11.963,11.963s5.356,11.963,11.963,11.963h27.017
                          l37.162,29.045h-24.571c-6.607,0-11.963,5.356-11.963,11.963s5.356,11.963,11.963,11.963h53.979
                          c46.991,41.387,60.205,74.337,60.869,152.268l-75.3,49.587c-4.413,2.906-6.396,8.363-4.88,13.424
                          c1.517,5.061,6.175,8.528,11.459,8.528h213.077c5.284,0,9.942-3.467,11.459-8.528c1.517-5.061-0.468-10.519-4.88-13.424
                          l-75.298-49.586c0.664-77.931,13.878-110.881,60.868-152.268h53.98c6.606,0,11.963-5.356,11.963-11.963
                          s-5.357-11.963-11.963-11.963h-24.572l37.162-29.045h27.019c6.606,0,11.963-5.356,11.963-11.963S454.88,211.297,448.273,211.297z
                          M312.021,156.732c0.746-0.037,1.493-0.056,2.249-0.056c10.924,0,21.517,3.869,29.827,10.893c0.004,0.004,0.008,0.006,0.012,0.01
                          c10.466,8.825,16.469,21.729,16.469,35.403c0,2.81-0.249,5.588-0.742,8.314h-91.133v0.001c-0.493-2.725-0.742-5.504-0.742-8.314
                          c0-4.912,0.758-9.722,2.265-14.325C276.121,170.481,292.907,157.651,312.021,156.732z M255.999,80.462
                          c25.534,0,46.307,20.773,46.307,46.307c0,2.403-0.184,4.781-0.545,7.12c-18.708,3.409-35.245,14.368-45.764,29.932
                          c-10.525-15.573-27.063-26.529-45.76-29.934c-0.36-2.339-0.544-4.716-0.544-7.119C209.692,101.237,230.465,80.462,255.999,80.462z
                          M197.729,156.677c0.756,0,1.503,0.019,2.273,0.057c19.09,0.918,35.876,13.747,41.779,31.952
                          c1.495,4.576,2.255,9.386,2.255,14.298c0,2.811-0.249,5.588-0.742,8.314h-91.131c-0.493-2.725-0.742-5.503-0.742-8.314
                          C151.422,177.45,172.195,156.677,197.729,156.677z M322.621,488.076H189.377l44.38-29.225h44.484L322.621,488.076z
                          M361.019,251.937c-5.593,4.371-10.604,8.431-15.225,12.332h-74.209c-6.606,0-11.963,5.356-11.963,11.963
                          c0,6.607,5.357,11.963,11.963,11.963h48.519c-17.024,17.892-28.252,35.214-35.949,54.907c-9.276,23.74-13.531,50.9-14.197,91.823
                          h-27.921c-0.666-40.924-4.921-68.085-14.197-91.823c-7.695-19.693-18.925-37.015-35.949-54.908h5.837
                          c6.607,0,11.963-5.356,11.963-11.963c0-6.607-5.356-11.963-11.963-11.963h-31.527c-4.618-3.897-9.629-7.957-15.225-12.332
                          l-21.383-16.713h13.49h109.29h7.249h109.289h13.49L361.019,251.937z"/>
                      </g>
                    </g>
                  </svg>
                </span>
              </li>
              <li class="amenities-list__amenities-item amenities-item">
                <span :class="departure.is_accessible ? 'amenities-item__text-active' : 'amenities-item__text-inactive'">
                  <svg fill="#000000" width="36px" height="36px" viewBox="-7.5 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg">
                    <title>accessibility</title>
                    <path d="M10.64 21.2c-0.44-0.12-0.88 0.16-1 0.6-0.48 1.76-2.080 3-3.92 3-2.24 0-4.040-1.8-4.040-4.040 0-1.56 0.88-2.96 2.28-3.64 0.4-0.2 0.6-0.72 0.4-1.12s-0.72-0.6-1.12-0.4c-1.96 0.96-3.2 2.92-3.2 5.12 0 3.16 2.56 5.72 5.72 5.72 2.6 0 4.88-1.76 5.52-4.28 0.080-0.4-0.2-0.84-0.64-0.96zM16.64 22.040c-0.2-0.4-0.72-0.56-1.12-0.36l-1 0.52-2.32-4c-0.16-0.24-0.44-0.4-0.72-0.4h-3.88l-0.12-1.040h3.080c0.44 0 0.84-0.36 0.84-0.84s-0.36-0.84-0.84-0.84h-3.24l-0.32-3.12c-0.040-0.44-0.44-0.8-0.92-0.76-0.44 0.040-0.8 0.44-0.76 0.92l0.68 6.6c0.040 0.44 0.4 0.76 0.84 0.76h4.16l2.48 4.28c0.16 0.28 0.44 0.4 0.72 0.4 0.12 0 0.24-0.040 0.4-0.080l1.72-0.88c0.36-0.24 0.52-0.76 0.32-1.16zM5.84 10.36c1.32 0 2.4-1.080 2.4-2.4s-1.080-2.4-2.4-2.4c-1.32 0-2.4 1.080-2.4 2.4s1.080 2.4 2.4 2.4zM5.84 7.2c0.4 0 0.72 0.32 0.72 0.72s-0.32 0.72-0.72 0.72c-0.4 0-0.72-0.32-0.72-0.72s0.32-0.72 0.72-0.72z"></path>
                  </svg>
                </span>
              </li>
            </ul>
          </div>
        </div>
        <div class="departure-item__status-and-book-wrapper">
          <div class="departure-item__departure-status-wrapper">
            <p :class="['departure-status', getStatusClass(departure.status)]">{{ departure.status }}</p>
            <p class="departure-item__bus-type">{{ departure.bus_type }}</p>
          </div>
          <div class="departure-item__book-btn-wrapper">
            <button v-if="isAvailable(departure)" @click="bookDeparture(departure)" class="departure-item__book-btn">Book Now</button>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-else class="no-results">
      <p class="no-results__text">No departures found for the selected criteria.</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-message">
      <p class="error-message__text">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { API } from '../../../frontend/static/js/api.js';

const routes = ref([]);
const departures = ref([]);
const loading = ref(false);
const error = ref('');
const selectedRouteId = ref('');
const viewType = ref('upcoming');
const selectedDate = ref(new Date().toISOString().split('T')[0]); // Today's date

// Load routes on mount
onMounted(async () => {
  await loadRoutes();
});

// Load routes
async function loadRoutes() {
  try {
    const params = new URLSearchParams({ status: 'ACTIVE' });
    const data = await API.request(`/api/routes/?${params.toString()}`);
    routes.value = data;
  } catch (err) {
    console.error('Error loading routes:', err);
  }
}

// Load departures based on view type
async function loadDepartures() {
  if (!selectedRouteId.value) return;

  loading.value = true;
  error.value = '';

  try {
    let endpoint = '';
    if (viewType.value === 'upcoming') {
      endpoint = `/api/departures/by_route/${selectedRouteId.value}/upcoming`;
    } else if (viewType.value === 'daily') {
      const [year, month, day] = selectedDate.value.split('-');
      endpoint = `/api/departures/by_route/${selectedRouteId.value}/daily/${year}/${month}/${day}`;
    }

    const data = await API.request(endpoint);
    departures.value = data;
  } catch (err) {
    error.value = `Error loading departures: ${err.message}`;
    console.error('Error loading departures:', err);
  } finally {
    loading.value = false;
  }
}

// Helper functions for formatting
const formatDate = (utcString) => {
  if (!utcString) return '';
  const utcDate = new Date(utcString);
  const offsetMs = new Date().getTimezoneOffset() * -60 * 1000;
  const localDate = new Date(utcDate.getTime() - offsetMs);
  return localDate.toLocaleDateString();
};

const formatDateFull = (date) => {
  const parsedDate = new Date(date);
  return parsedDate.toLocaleDateString(
    'en-US',
    {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }
  )
};

const formatTime = (utcString) => {
  if (!utcString) return '';
  const utcDate = new Date(utcString);
  const offsetMs = new Date().getTimezoneOffset() * -60 * 1000;
  const localDate = new Date(utcDate.getTime() - offsetMs);
  return localDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const calculateDuration = (departureTime, arrivalTime) => {
  if (!departureTime || !arrivalTime) return 'Trip duration: N/A';
  const dep = new Date(departureTime);
  const arr = new Date(arrivalTime);
  const diffMs = arr - dep;
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  return `${hours}h ${minutes}m`;
};

const getStatusClass = (status) => {
  switch (status) {
    case 'SCHEDULED':
      return 'status-scheduled';
    case 'DELAYED':
      return 'status-delayed';
    case 'CANCELLED':
      return 'status-cancelled';
    case 'ARRIVED':
      return 'status-arrived';
    case 'DEPARTED':
      return 'status-departed';
    default:
      return '';
  }
};

const isAvailable = (departure) => {
  const now = new Date();
  const depTime = new Date(departure.departure_time);
  
  return !departure.is_cancelled &&
        departure.status !== 'CANCELLED' &&
        !departure.is_full &&
        depTime > now &&
        departure.status !== 'ARRIVED';
};
</script>

<style scoped>

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.title {
  font-size: 28px;
  margin-bottom: 2rem;
  color: white;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  padding: 10px;
  flex-wrap: wrap;
  background-color: #fff;
  border-radius: 10px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #333;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.departures-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.departure-item {
  border: 1px solid #e0e0e0;
  padding: 1rem;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.departure-info__date-title {
  margin: 0;
  margin-bottom: 10px;
}

.departure-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.departure-info__departure-times,
.departure-info__arrival-times {
  border: 1px solid #0374b6;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(178, 205, 230, 0.7);
}

.departure-info__arrow-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.arrow-section__duration {
  margin: 0;
  color: #666;
}

.departure-times__title,
.arrival-times__title {
  margin: 0;
  margin-bottom: 10px;
  padding: 5px;
  border-radius: 5px;
  background-color: rgb(178, 205, 230);
}

.departure-date,
.arrival-date,
.departure-time,
.arrival-time {
  display: flex;
  align-items: center;
  margin: 0;
  margin-bottom: 5px;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.amenities-list {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  list-style: none;
}

.amenities-item__text-active,
.amenities-item__text-inactive {
  margin: 0;
}

.svg-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.departure-item__status-and-book-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.departure-item__departure-status-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.departure-status {
  margin: 0;
  font-size: 0.9rem;
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 2px solid transparent; /* Default transparent */
}

.status-scheduled {
  background-color: rgb(152, 219, 152);
  border-color: green;
}

.status-delayed {
  background-color: rgb(226, 203, 159);
  border-color: orange;
}

.status-departed {
  background-color: rgb(210, 235, 174);
  border-color: greenyellow;
}

.status-cancelled {
  background-color: rgb(218, 148, 148);
  border-color: red;
}

.status-arrived {
  background-color: rgb(178, 205, 230);
  border-color: blue;
}

.departure-item__bus-type {
  margin: 0;
  padding: 0.25rem 0.5rem;
  background-color: rgb(178, 205, 230);
  border: 2px solid #155ea3;
  border-radius: 5px;
  font-size: 0.9rem;
}

.arrival-na {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #666;
}

.departure-item__book-btn {
  background-color: #266cc9;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.no-results {
  text-align: center;
  color: #666;
  margin-top: 2rem;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 2rem;
}

.loading-state {
  text-align: center;
  color: #666;
  margin-top: 2rem;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
