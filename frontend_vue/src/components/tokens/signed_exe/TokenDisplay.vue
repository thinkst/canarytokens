<template>
  <div class="flex justify-center">
    <base-button
      class="mt-16"
      :href="href"
      :download="download"
      @click="handleDownloadCustomExeFile"
      >Download {{ props.tokenData.file_name }}</base-button
    >
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

type CustomEXEDataType = {
  file_name: string;
  file_contents: string;
};

const props = defineProps<{
  tokenData: CustomEXEDataType;
}>();

const href = ref(`${props.tokenData?.file_name}`);
const download = ref(props.tokenData?.file_contents);

function handleDownloadCustomExeFile() {
  download.value = `${props.tokenData?.file_name}`;
  href.value = props.tokenData?.file_contents;
}
</script>
