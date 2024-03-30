<template>
  <img
    :src="
      getImgUrl(`token_icons/${tokensOperations[props.selectedToken].icon}`)
    "
    :alt="`${tokensOperations[props.selectedToken].label}`"
    class="w-[6rem] pb-16"
  />
  <h2 class="text-xl font-semibold leading-4 text-center">
    {{ tokensOperations[props.selectedToken].label }}
  </h2>
  <p class="text-center">
    {{ tokensOperations[props.selectedToken].description }}
    <BaseLinkDocumentation
      :link="tokensOperations[props.selectedToken].documentationLink"
    />
  </p>
  <div class="flex flex-col gap-16 px-32 mt-32">
    <component :is="dynamicComponent" />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';
import { useTokens } from '@/composables/useTokens';
import useImage from '@/composables/useImage';

const props = defineProps<{
  selectedToken: string;
}>();

const { tokensOperations } = useTokens();
const { getImgUrl } = useImage();

const dynamicComponent = ref(null);

const loadComponent = async () => {
  dynamicComponent.value = defineAsyncComponent(
    () => import(`@/components/tokens/${props.selectedToken}/GenerateToken.vue`)
  );
};

loadComponent();
</script>
