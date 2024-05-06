<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <label
      for="radio-group-action"
      class="mb-8 ml-4 font-semibold text-center"
      >Upload your image</label
    >
    <BaseUploadFile
      id="web_image"
      info-allowed-file="JPG, JPEG, GIF or PNG"
    />
  </BaseGenerateTokenSettings>

  <GenerateTokenSettingsNotifications
    memo-helper-example="Image embedded in router X's admin interface"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
