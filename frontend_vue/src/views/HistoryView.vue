<template>
  <div
    v-if="selectedTokenType && selectedTokenRef && selectedTokenLogo"
    class="flex flex-col items-center gap-8 mt-16"
  >
    <img
      :src="selectedTokenLogo"
      class="h-[4rem]"
      aria-hidden="true"
      :alt="`${selectedTokenType} logo`"
    />
    <div class="mb-24 text-xl text-center text-grey-500">
      <h2>
        <span class="text-grey-300"
          >{{ selectedTokenType }} Canarytoken Id: </span
        ><span class="font-semibold">{{ selectedTokenRef }}</span>
      </h2>
    </div>
  </div>
  <AppLayoutTwoColumns>
    <HistoryToken
      @update-token-title="(type, token) => handleTokenTitle(type, token)"
    />
  </AppLayoutTwoColumns>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { tokenServices } from '@/utils/tokenServices';
import AppLayoutTwoColumns from '@/layout/AppLayoutTwoColumns.vue';
import HistoryToken from '@/components/HistoryToken.vue';

const selectedTokenType = ref('');
const selectedTokenRef = ref('');
const selectedTokenLogo = ref('');

function handleTokenTitle(type: string, token: string) {
  selectedTokenType.value = tokenServices[type].label;
  selectedTokenLogo.value = getImageUrl(
    `token_icons/${tokenServices[type].icon}`
  );
  selectedTokenRef.value = token;
}
</script>
