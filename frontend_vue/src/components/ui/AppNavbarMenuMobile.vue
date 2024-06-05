<template>
  <button
    :aria-expanded="showMobileMenu"
    aria-controls="mobile_menu"
    class="bg-grey-100 md:hidden w-[36px] h-[36px] rounded-full self-center mr-16 overflow-hidden"
    @click="handleShowMobileMenu"
  >
    <Transition name="icon">
      <span
        v-if="showMobileMenu"
        class="duration-150 ease-in-out transition-margin"
        ><font-awesome-icon
          class="text-grey-500"
          icon="xmark"
      /></span>
      <span
        v-else
        class="duration-150 ease-in-out transition-margin"
        ><font-awesome-icon
          class="text-grey-500"
          icon="bars"
      /></span>
    </Transition>
  </button>
  <Transition>
    <AppNavbarLinks
      v-if="showMobileMenu"
      is-mobile
      @click-link="handleShowMobileMenu"
    />
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppNavbarLinks from './AppNavbarLinks.vue';

const showMobileMenu = ref(false);

function handleShowMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value;
}
</script>

<style scoped lang="scss">
.v-enter-to,
.v-leave-from {
  right: 0;
}

.v-enter-from,
.v-leave-to {
  right: -765px;
}

.icon-enter-to,
.icon-leave-from {
  margin-right: 0;
}

.icon-enter-from {
  margin-right: -15px;
}

.icon-leave-to {
  margin-left: -15px;
}

.icon-enter-active,
.icon-leave-active {
  opacity: 0;
}
</style>
