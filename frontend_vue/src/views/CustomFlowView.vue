<template>
  <AppLayoutOneColumn>
    <div v-if="isLoading">
      <BaseSpinner
        height="5rem"
        class="mt-24"
      />
    </div>
    <template v-if="isError">
      <div class="flex flex-col items-center">
        <h2 class="text-red font-semibold">
          Oh no! Something didn't work as expected.
        </h2>
        <img
          :src="getImageUrl('icons/errorIcon.svg')"
          alt="success-icon"
          class="w-[15rem] h-[15rem]"
        />
      </div>
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
import { useRoute, useRouter } from 'vue-router';
import AppLayoutOneColumn from '@/layout/AppLayoutOneColumn.vue';
import { getTokenData } from '@/utils/dataService.ts';
import getImageUrl from '@/utils/getImageUrl';

const route = useRoute();
const router = useRouter();
const customComponent = shallowRef();
const customComponentName = ref('');
const isLoading = ref(false);
const isError = ref(false);
const selectedToken = ref(route.params['tokentype'] || '');
const tokenData = ref();

const customComponentNameMap = {
  'generate-custom': 'GenerateTokenCustom',
  'manage-custom': 'ManageTokenCustom',
};

onMounted(() => {
  tokenData.value = getTokenData();
  selectedToken.value = route.params['tokentype'];

  if (!selectedToken.value) {
    router.push({ name: 'error' });
    return;
  }

  if (!tokenData.value) {
    router.push({ name: 'error' });
    return;
  }

  customComponentName.value =
    customComponentNameMap[route.name as keyof typeof customComponentNameMap];

  if (!customComponentName.value) {
    router.push({ name: 'error' });
    return;
  }

  loadComponent();
});

const loadComponent = async () => {
  try {
    isLoading.value = true;

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
