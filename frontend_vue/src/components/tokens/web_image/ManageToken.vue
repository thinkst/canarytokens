<template>
  <div v-if="!tokenUrl">Error loading</div>
  <TokenDisplay
    v-else
    :token-url="tokenUrl"
  />
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { ManageTokenBackendType } from '@/components/tokens/types.ts';
import consoleImg from '@/assets/wise_man';

const props = defineProps<{
  tokenBackendResponse: ManageTokenBackendType;
}>();

onMounted(() => {
  consoleImg;
});

const tokenUrl = ref(props.tokenBackendResponse.canarydrop?.generated_url);
</script>
