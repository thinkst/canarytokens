<template>
  <div class="z-50 flex justify-between w-full gap-24 sm:justify-center">
    <div class="flex flex-row lg:w-[80vw] sm:w-full">
      <AppLogo class="px-24 py-16" />
      <nav
        role="navigation"
        class="items-center justify-end hidden w-full pr-32 md:flex"
      >
        <ul
          class="flex items-end pt-8 text-sm uppercase gap-x-24 lg:gap-x-32 font-regular"
        >
          <li
            v-for="item in menuItems"
            :key="item.name"
          >
            <RouterLink
              :to="item.path"
              class="transition-colors duration-100 text-grey-400 hover:text-green desktop-link focus-visible:border-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500"
            >
              {{ item.name }}
            </RouterLink>
          </li>
          <li>
            <a
              href="https://docs.canarytokens.org/guide"
              target="_blank"
              class="transition-colors duration-100 cursor-pointer text-grey-400 hover:text-green desktop-link focus:border-none focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <font-awesome-icon
                icon="link"
                class="w-[0.8rem] pr-8"
              />Documentation
            </a>
          </li>
        </ul>
      </nav>
    </div>
    <AppNavbarMenuMobile
      :menu-items="menuItems"
      class="w-full"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { ENV_MODE } from '@/constants.ts';
import { useRoute } from 'vue-router';
import AppLogo from './AppLogo.vue';
import AppNavbarMenuMobile from './AppNavbarMenuMobile.vue';

const route = useRoute();

const isDevEnv = import.meta.env.MODE === ENV_MODE.DEVELOPMENT;
const isExistingToken = ref(false);
const auth = ref(route.params.auth);
const token = ref(route.params.token);

const menuItems = computed(() => {
  const items = [];

  if (isDevEnv) {
    items.push({ name: 'Components Preview', path: '/components' });
  }

  if (isExistingToken.value) {
    items.push(
      { name: 'New token', path: '/' },
      { name: 'Token History', path: `/history/${auth.value}/${token.value}` },
      { name: 'Manage Token', path: `/manage/${auth.value}/${token.value}` }
    );
  }

  return items;
});

watch(
  () => route.params,
  (newParams) => {
    auth.value = newParams.auth;
    token.value = newParams.token;
    isExistingToken.value = auth.value && token.value ? true : false;
  }
);
</script>

<style scoped lang="scss">
// there's a way to expose RouterLink classes for tailwind
// but it's quite cumbersome and I'd avoid it
// https://router.vuejs.org/guide/advanced/extending-router-link
.desktop-link {
  &.router-link-active {
    color: hsl(152, 59%, 48%);
    position: relative;
  }
}
</style>
