<template>
  <img
    :src="
      getImgUrl(`token_icons/${tokensOperations[newTokenData.token_type].icon}`)
    "
    :alt="`${tokensOperations[newTokenData.token_type].label}`"
    class="w-[6rem] pb-16"
  />
  <h2 class="text-xl font-semibold leading-4 text-center">
    {{
      `Your ${tokensOperations[newTokenData.token_type].label} Token is active!`
    }}
  </h2>
  <p class="text-center">
    {{ tokensOperations[newTokenData.token_type].instruction }}
  </p>
  <div class="w-full px-32 mt-32">
    <component
      :is="dynamicComponent"
      :new-token-data="newTokenData"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';
import { useTokens } from '@/composables/useTokens';
import useImage from '@/composables/useImage';

const props = defineProps<{
  newTokenData: { token_type: string } & Record<string, unknown>;
}>();

const { tokensOperations } = useTokens();
const { getImgUrl } = useImage();

const dynamicComponent = ref(null);

const loadComponent = async () => {
  dynamicComponent.value = defineAsyncComponent(
    () =>
      import(
        `@/components/tokens/${props.newTokenData.token_type}/ActiveToken.vue`
      )
  );
};

loadComponent();
</script>
