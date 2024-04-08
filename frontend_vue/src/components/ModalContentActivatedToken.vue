<template>
  <img
    :src="getImageUrl(`token_icons/${tokenServices[tokenType].icon}`)"
    :alt="`${tokenServices[tokenType].label}`"
    class="w-[6rem] pb-16"
  />
  <h2 class="text-xl font-semibold leading-6 text-cente">
    {{ `Your ${tokenServices[tokenType].label} Token is active!` }}
  </h2>
  <p class="text-center">
    {{ tokenServices[tokenType].instruction }}
  </p>
  <div class="w-full px-32 mt-32">
    <component
      :is="dynamicComponent"
      :token-data="newTokenResponse"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';
import { tokenServices } from '@/utils/tokenServices';
import getImageUrl from '@/utils/getImageUrl';

const props = defineProps<{
  newTokenResponse: { token_type: string } & Record<string, unknown>;
}>();

const dynamicComponent = ref({
  props: {},
});
const tokenType = props.newTokenResponse.token_type;

async function loadComponent() {
  dynamicComponent.value = defineAsyncComponent(
    () => import(`@/components/tokens/${tokenType}/ActivatedToken.vue`)
  );
}

loadComponent();
</script>
