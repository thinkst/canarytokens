<template>
  <h2
    v-if="selectedTokenType && selectedTokenRef"
    class="mb-24 text-xl text-center text-grey-800"
  >
    {{ selectedTokenType }}: {{ selectedTokenRef }}
  </h2>
  <AppLayoutTwoColumns>
    <HistoryToken
      @update-token-title="(type, token) => handleTokenTitle(type, token)"
    />
  </AppLayoutTwoColumns>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppLayoutTwoColumns from '@/layout/AppLayoutTwoColumns.vue';
import HistoryToken from '@/components/HistoryToken.vue';
import { tokenServices } from '@/utils/tokenServices';

const selectedTokenType = ref('');
const selectedTokenRef = ref('');

function handleTokenTitle(type: string, token: string) {
  selectedTokenType.value = tokenServices[type].label;
  selectedTokenRef.value = token;
}
</script>
