<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseLabel
      id="web_image"
      class="text-center"
      >Upload your image</BaseLabel
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
