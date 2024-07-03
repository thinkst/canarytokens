<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="expected_referrer"
      type="text"
      placeholder="e.g. thinkst.com"
      label="Domain of protected website"
      full-width
      required
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="For instance: CSS Cloned website token for https://thinkst.com"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
