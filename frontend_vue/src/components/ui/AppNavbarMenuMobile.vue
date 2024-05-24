<template>
  <button
    :aria-expanded="showMobileMenu"
    aria-controls="mobile_menu"
    class="bg-grey-100 md:hidden w-[36px] h-[36px] rounded-full self-center mr-16 overflow-hidden hover:bg-grey-200 active:bg-green focus:bg-grey-200"
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
    <nav
      v-if="showMobileMenu"
      id="mobile_menu"
      role="navigation"
      class="absolute transition-left ease-in-out duration-300 w-full text-center md:hidden bg-green top-[93px] py-32 min-h-svh z-50 motion-reduce:transition-none motion-reduce:hover:transform-none"
    >
      <ul class="uppercase">
        <li
          v-for="item in menuItems"
          :key="item.name"
          class="py-8"
        >
          <RouterLink
            :to="item.path"
            class="text-green-200 hover:text-white mobile-link"
            @click="handleShowMobileMenu"
          >
            {{ item.name }}
          </RouterLink>
        </li>
        <li
          class="py-8 text-green-200 cursor-pointer hover:text-white mobile-link"
        >
          <a href="#">
            <font-awesome-icon
              icon="link"
              class="w-[0.8rem] pr-8"
            />Documentation
          </a>
        </li>
      </ul>
    </nav>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import type { PropType } from 'vue';

type menuItemsType = {
  name: string;
  path: string;
};

defineProps({
  menuItems: {
    type: Array as PropType<menuItemsType[]>,
    required: true,
  },
});

const showMobileMenu = ref(false);

function handleShowMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value;
}
</script>

<style scoped lang="scss">
.mobile-link {
  &.router-link-active {
    color: hsl(0, 0%, 100%);
    position: relative;
  }
}

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
