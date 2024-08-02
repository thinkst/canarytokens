<template>
  <BaseGenerateTokenSettings
    setting-type="Canarytoken"
    class="flex gap-16"
  >
    <BaseFormImageSelect
      id="icon"
      label="Select App icon (optional)"
      :options="pwaIconService"
    />
    <BaseFormTextField
      id="app_name"
      type="text"
      placeholder="E.g. Password Manager"
      label="App name (optional)"
      full-width
      class="text-center"
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Fake Password Manager app on Alice's phone"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { pwaIconService } from './pwaIconService';
</script>
