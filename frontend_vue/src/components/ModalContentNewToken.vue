<template>
  <img
    :src="getImgUrl(`token_icons/${tokensOperations[tokenType].icon}`)"
    :alt="`${tokensOperations[tokenType].label}`"
    class="w-[6rem] pb-16"
  />
  <h2 class="text-xl font-semibold leading-4 text-center">
    {{ `Your ${tokensOperations[tokenType].label} Token is active!` }}
  </h2>
  <p class="text-center">
    {{ tokensOperations[tokenType].instruction }}
  </p>
  <div class="w-full px-32 mt-32">
    <component
      :is="dynamicComponent"
      :token-snippet-data="tokenSnippetData"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from 'vue';
import { useTokens } from '@/composables/useTokens';
import useImage from '@/composables/useImage';
import { onMounted } from 'vue';

const props = defineProps<{
  newTokenResponse: { token_type: string } & Record<string, unknown>;
}>();

const { tokensOperations } = useTokens();
const { getImgUrl } = useImage();

const dynamicComponent = ref({
  props: {},
});
const tokenSnippetData = ref();
const tokenType = props.newTokenResponse.token_type;

onMounted(() => {
  if (
    tokenType !== undefined &&
    tokensOperations.value[tokenType]?.getNewTokenData
  ) {
    tokenSnippetData.value = tokensOperations.value[tokenType].getNewTokenData(
      props.newTokenResponse
    );
  }
});

async function loadComponent() {
  dynamicComponent.value = defineAsyncComponent(
    () => import(`@/components/tokens/${tokenType}/ActivatedToken.vue`)
  );
  dynamicComponent.value.props = {
    tokenSnippetData: tokenSnippetData.value,
  };
}

loadComponent();
</script>
