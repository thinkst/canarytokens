<template>
  <AppLayoutOneColumn>
    <div>Content</div>
    <div
      v-if="loading"
      class="loading"
    >
      Loading...
    </div>

    <div
      v-if="error"
      class="error"
    >
      {{ error }}
    </div>
    <div v-else>
      {{ token }}
    </div>
  </AppLayoutOneColumn>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import AppLayoutOneColumn from '@/layout/AppLayoutOneColumn.vue';
import { manageToken } from '@/api/main';

const route = useRoute();
const loading = ref(false);
const error = ref(null);

const token = ref({});

watch(() => route.params.token, fetchTokenData, { immediate: true });

async function fetchTokenData() {
  loading.value = true;

  const params = {
    auth: route.params.auth,
    token: route.params.token,
  };
  try {
    token.value = await manageToken(params);
  } catch (err: any) {
    error.value = err.toString();
  } finally {
    loading.value = false;
  }
}
</script>

<style></style>
