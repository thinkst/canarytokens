<template>
  <svg
    viewBox="0 0 52 39"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M0.642383 38.1777C0.418066 37.865 0.285645 37.4814 0.285645 37.067V33.0276V7.19802C0.285645 6.28191 1.02823 5.53876 1.94491 5.53876H3.19777C4.46034 5.53876 5.48375 4.51534 5.48375 3.25278C5.48375 1.99021 6.50716 0.966797 7.76973 0.966797H20.7721C21.6249 0.966797 22.4068 1.44112 22.8001 2.19797L23.8983 4.30872C24.2921 5.06501 25.0735 5.5399 25.9263 5.5399H40.9801C41.8962 5.5399 42.6393 6.28248 42.6393 7.19916V16.6992L0.642383 38.1777Z"
      fill="#18884F"
      :class="{ 'is-file-folder-animation': hasFile }"
    />
    <path
      d="M5 14C5 12.3431 6.34315 11 8 11H36C37.6569 11 39 12.3431 39 14V34C39 35.6569 37.6569 37 36 37H8C6.34315 37 5 35.6569 5 34V14Z"
      :class="[{ 'is-file-animation': hasFile }]"
      class="file"
      fill="#F6F7FA"
    />
    <path
      d="M9.66834 18.0504C10.0371 17.2279 10.855 16.6982 11.7563 16.6982H49.8639C51.1619 16.6982 52.0283 18.0362 51.4975 19.2205L43.3753 37.3343C42.9278 38.3326 41.9358 38.9753 40.8416 38.9753H6.23395H2.19453C1.55469 38.9753 0.989042 38.6608 0.642578 38.1779L0.64429 38.1767L5.28018 27.837L9.66834 18.0504Z"
      fill="#38D47F"
      :class="{ 'is-file-folder-animation': hasFile }"
    />
  </svg>
</template>

<script setup lang="ts">
defineProps<{
  hasFile?: string;
}>();
</script>

<style>
.file {
  transform: translateY(-4rem);
}

@keyframes fadeIn {
  from {
    transform: translateY(-4rem);
  }
  to {
    transform: translateY(0rem);
    opacity: 1;
  }
}

@keyframes bounce {
  0% {
    transform: scaleY(0.9);
  }
  50% {
    transform: scaleY(1.1);
  }
  80% {
    transform: scaleY(1);
  }
}

.is-file-animation {
  animation: fadeIn 300ms forwards;
}

.is-file-folder-animation {
  animation: bounce 600ms;
  animation-delay: 350ms forwards;
}
</style>
