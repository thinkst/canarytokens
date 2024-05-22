<template>
  <li
    class="flex flex-row flex-wrap items-center justify-between px-16 py-8 mb-8 bg-white rounded-xl shadow-solid-shadow-grey"
  >
    <p class="text-sm text-grey-500">Download list</p>
    <div class="flex flex-row">
      <BaseButton
        variant="text"
        icon="file"
        :loading="isCsvLoading"
        @click="handleDownloadList(INCIDENT_LIST_EXPORT.CSV)"
        >CSV</BaseButton
      >
      <BaseButton
        variant="text"
        icon="file-excel"
        :loading="isJsonLoading"
        @click="handleDownloadList(INCIDENT_LIST_EXPORT.JSON)"
        >JSON</BaseButton
      >
    </div>
  </li>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { downloadAsset } from '@/api/main';
import { INCIDENT_LIST_EXPORT } from '@/components/constants';

const route = useRoute();

const isCsvLoading = ref(false);
const isJsonLoading = ref(false);

function handleDownloadList(type: string) {
  // Set loading state
  if (type === INCIDENT_LIST_EXPORT.CSV) {
    isCsvLoading.value = true;
  } else {
    isJsonLoading.value = true;
  }

  const params = {
    fmt: type,
    auth: route.params.auth as string,
    token: route.params.token as string,
  };
  downloadAsset(params)
    .then((res) => {
      window.location.href = res.request.responseURL;
    })
    .catch((err) => {
      console.log(err, 'err');
    })
    .finally(() => {
      // Removes loading state
      isCsvLoading.value = false;
      isJsonLoading.value = false;
      console.log('You downloaded the file, yay!');
    });
}
</script>
