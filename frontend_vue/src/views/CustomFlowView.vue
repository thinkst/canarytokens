<template>
  <AppLayoutOneColumn>
    <div v-if="isLoading">
      <BaseSpinner
        height="5rem"
        class="mt-24"
      />
    </div>
    <template v-if="isError">
      <h2 class="text-red font-semibold">
        Oh no! Something didn't work as expected
      </h2>
      <img
        :src="getImageUrl('icons/errorIcon.svg')"
        alt="success-icon"
        class="w-[15rem] h-[15rem]"
      />
    </template>
    <component
      :is="customComponent"
      v-else
      :token-data="tokenData"
    />
  </AppLayoutOneColumn>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, shallowRef, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import AppLayoutOneColumn from '@/layout/AppLayoutOneColumn.vue';
import { getTokenData } from '@/utils/dataService.ts';
import getImageUrl from '@/utils/getImageUrl';

const route = useRoute();
const customComponent = shallowRef();
const customComponentName = ref('');
const isLoading = ref(false);
const isError = ref(false);
const selectedToken = ref(route.params['tokentype'] || '');
const tokenData = ref({});

const customComponentNameMap = {
  'generate-custom': 'GenerateTokenCustom',
  'manage-custom': 'ManageTokenCustom',
};

onMounted(() => {
  selectedToken.value = route.params['tokentype'];
  if (!selectedToken.value) {
    isError.value = true;
    return;
  }

  customComponentName.value =
    customComponentNameMap[route.name as keyof typeof customComponentNameMap];

  if (!customComponentName.value) {
    isError.value = true;
    isLoading.value = false;
    return;
  }

  loadComponent();
});

const loadComponent = async () => {
  try {
    isLoading.value = true;
    tokenData.value = getTokenData() || {};

    customComponent.value = defineAsyncComponent(
      () =>
        import(
          `@/components/tokens/${selectedToken.value}/${customComponentName.value}.vue`
        )
    );
  } catch (error) {
    console.error('Error loading component:', error);
    isError.value = true;
  } finally {
    isLoading.value = false;
  }
};
</script>