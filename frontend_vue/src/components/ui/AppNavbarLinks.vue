<template>
  <nav
    role="navigation"
    :class="
      !props.isMobile
        ? 'items-center justify-end hidden w-full pr-32 md:flex'
        : 'absolute transition-left ease-in-out duration-300 w-[70vw] text-right md:hidden bg-green top-[93px] right-0 py-32 pr-32 min-h-svh z-50 motion-reduce:transition-none motion-reduce:hover:transform-none'
    "
  >
    <ul
      :class="
        !props.isMobile
          ? 'flex items-end pt-8 text-sm uppercase gap-x-16 lg:gap-x-32 font-regular'
          : 'flex flex-col gap-16 uppercase'
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
              ? 'transition-colors duration-100 text-grey-400 hover:text-green desktop-link focus-visible:border-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500'
              : 'text-green-200 hover:text-white mobile-link'
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
              ? 'transition-colors duration-100 cursor-pointer text-grey-400 hover:text-green desktop-link focus:border-none focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
              : 'text-green-200 hover:text-white mobile-link'
          "
        >
          <font-awesome-icon
            v-if="item.icon"
            :icon="item.icon"
            class="w-[0.8rem] pr-4"
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
    color: hsl(152, 59%, 48%);
    position: relative;
  }
}

.mobile-link {
  &.router-link-active {
    color: hsl(0, 0%, 100%);
    position: relative;
  }
}
</style>
