<template>
  <img
    :src="
      getImgUrl(`token_icons/${tokensOperations[props.selectedToken].icon}`)
    "
    alt="Token logo"
    class="w-[6rem] pb-16"
  />
  <h2 class="text-xl font-semibold text-center">
    {{ tokensOperations[props.selectedToken].label }}
  </h2>
  <p class="text-center">
    {{ tokensOperations[props.selectedToken].description }}
    <BaseLinkDocumentation
      :link="tokensOperations[props.selectedToken].documentationLink"
    />
  </p>
  <component
    :is="dynamicComponent"
    class="flex gap-16"
  />
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';
import { useTokens } from '@/composables/useTokens';
import useImage from '@/composables/useImage';

const props = defineProps<{
  selectedToken: string;
}>();

// const emits = defineEmits(['create-token']);

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
