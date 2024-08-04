<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormImageSelect
      id="icon"
      label="Select App icon"
      :options="pwaIconService"
      class="mb-16"
      @image-selected="onImageSelected"
    />
    <BaseFormTextField
      id="app_name"
      type="text"
      placeholder="E.g. Password Manager"
      label="App name (optional)"
      helper-message="If you leave this blank, we'll use a reasonable default."
      full-width
      class="text-center"
      :value="appName"
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Fake Password Manager app on Alice's phone"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { pwaIconService } from './pwaIconService';

const appName = ref('test');

function onImageSelected(img: String) {
  const selectedImage = pwaIconService.find((e) => e.value === img);
  if (selectedImage?.label === undefined) return;
  appName.value = selectedImage.label;
}
</script>
