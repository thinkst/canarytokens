<template>
  <div class="relative">
    <TokenIcon
      :title="tokenServices[tokenType].label"
      :logo-img-url="tokenServices[tokenType].icon"
      class="w-[6rem] pb-16"
      :has-animation="true"
      :has-shadow="true"
    />
    <img
      alt="active token"
      :src="getImageUrl('icons/active_token_badge.png')"
      class="absolute bottom-16 right-0 w-[1.5rem]"
    />
  </div>
  <h2 class="mb-8 text-xl font-semibold leading-tight text-center">
    {{ `Your ${tokenServices[tokenType].label} Canarytoken is active!` }}
  </h2>
  <p class="leading-tight text-center">
    {{ tokenServices[tokenType].instruction }}
  </p>
  <div class="w-full mt-32 sm:px-32">
    <component
      :is="dynamicComponent"
      :token-data="newTokenResponse"
      @how-to-use="$emit('howToUse')"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, shallowRef } from 'vue';
import { tokenServices } from '@/utils/tokenServices';
import getImageUrl from '@/utils/getImageUrl';
import TokenIcon from '@/components/icons/TokenIcon.vue';
import { launchConfetti } from '@/utils/confettiEffect';

const props = defineProps<{
  newTokenResponse: { token_type: string } & Record<string, unknown>;
}>();

defineEmits(['howToUse']);

const dynamicComponent = shallowRef();

const tokenType = props.newTokenResponse.token_type;

async function loadComponent() {
  dynamicComponent.value = defineAsyncComponent(
    () => import(`@/components/tokens/${tokenType}/ActivatedToken.vue`)
  );
  // When defining an async component
  // Vue adds an __asyncLoader() method to the component instance.
  // This method returns a promise that resolves when the component finishes loading.
  await dynamicComponent.value.__asyncLoader();

  launchConfetti(tokenType)
}

loadComponent();
</script>
