<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="postgresql_username"
      label="PostgreSQL Username"
      placeholder="e.g. postgres"
      required
    />
  </BaseGenerateTokenSettings>

  <GenerateTokenSettingsNotifications
    memo-helper-example="PostgreSQL credentials on wiki.internal"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
