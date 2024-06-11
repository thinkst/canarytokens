<template>
  <nav
    role="navigation"
    :class="
      !props.isMobile
        ? 'items-center justify-end hidden w-full pr-32 md:flex'
        : 'shadow-xl absolute transition-left ease-in-out duration-300 w-[80vw] text-right md:hidden bg-white/90 backdrop-blur-sm top-[93px] right-0 py-32 pr-32 h-auto z-50 motion-reduce:transition-none motion-reduce:hover:transform-none rounded-xl mr-8'
    "
  >
    <ul
      :class="
        !props.isMobile
          ? 'flex items-end pt-8 text-sm uppercase gap-x-16 lg:gap-x-32 font-regular'
          : 'flex flex-col gap-16 uppercase text-right'
      "
    >
      <li
        v-for="item in menuRouterItems"
        :key="item.name"
      >
        <RouterLink
          :to="item.path"
          :class="
            !props.isMobile
              ? 'transition-colors duration-100 text-green-100 hover:text-white desktop-link focus-visible:border-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-800'
              : 'text-grey-400 hover:text-white mobile-link'
          "
          @click="() => $emit('click-link')"
        >
          {{ item.name }}
        </RouterLink>
      </li>
      <li
        v-for="item in menuExternalLinkItems"
        :key="item.name"
      >
        <a
          :href="item.url"
          target="_blank"
          :class="
            !props.isMobile
              ? 'transition-colors duration-100 cursor-pointer text-green-100 hover:text-white desktop-link focus:border-none focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-800 flex flex-row gap-8 items-center'
              : 'text-grey-400 hover:text-white mobile-link flex flex-row gap-8 items-center justify-end'
          "
        >
          <font-awesome-icon
            v-if="item.icon"
            :icon="item.icon"
            class="w-[0.8rem]"
          />
          {{ item.name }}</a
        >
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ENV_MODE } from '@/constants.ts';

const props = defineProps({
  isMobile: Boolean,
});

defineEmits(['click-link']);

const route = useRoute();

const isDevEnv = import.meta.env.MODE === ENV_MODE.DEVELOPMENT;
const isExistingToken = ref(false);
const auth = ref(route.params.auth);
const token = ref(route.params.token);

onMounted(() => {
  isExistingToken.value = auth.value && token.value ? true : false;
});

const menuRouterItems = computed(() => {
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

const menuExternalLinkItems = computed(() => {
  const items = [
    {
      name: 'Documentation',
      url: 'https://docs.canarytokens.org/guide',
      icon: 'link',
    },
    {
      name: 'Github',
      url: 'https://github.com/thinkst/canarytokens',
      icon: 'fa-brands fa-github',
    },
  ];

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
/* there's a way to expose RouterLink classes for tailwind
 but it's quite cumbersome and I'd avoid it
 https://router.vuejs.org/guide/advanced/extending-router-link */

.desktop-link {
  &.router-link-active {
    @apply text-white;;
  }
}

.mobile-link {
  &.router-link-active {
    @apply text-green-600 
  }
}
</style>
