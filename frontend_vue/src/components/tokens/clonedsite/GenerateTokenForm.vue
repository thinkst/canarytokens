<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="clonedsite"
      type="text"
      placeholder="e.g. thinkst.com"
      label="Domain of protected website"
      full-width
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Cloned website token for https://thinkst.com"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
