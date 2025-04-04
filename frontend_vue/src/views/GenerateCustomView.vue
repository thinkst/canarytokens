<template>
  <AppLayoutOneColumn>
    <div v-if="isLoading">Loading...</div>
    <div v-if="isError">Oh no, an Error! :(</div>
    <component
      :is="GenerateTokenCustomFlow"
      v-else
      :token-data="tokenData"
    />
  </AppLayoutOneColumn>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, shallowRef } from 'vue';
import { useRoute } from 'vue-router';
import AppLayoutOneColumn from '@/layout/AppLayoutOneColumn.vue';
import { getTokenData } from '@/utils/dataService.ts';

const route = useRoute();
const GenerateTokenCustomFlow = shallowRef();
const isLoading = ref(false);
const isError = ref(false);
const selectedToken = ref(route.params['token'] || '');
const tokenData = ref({});

const loadComponent = async () => {
  try {
    isLoading.value = true;

    if (!selectedToken.value) {
      throw new Error('Invalid token');
    }
    tokenData.value = getTokenData();

    GenerateTokenCustomFlow.value = defineAsyncComponent(
      () =>
        import(
          `@/components/tokens/${selectedToken.value}/GenerateTokenCustomFlow.vue`
        )
    );
  } catch (error) {
    console.error('Error loading component:', error);
    isError.value = true;
  } finally {
    isLoading.value = false;
  }
};

loadComponent();
</script>
