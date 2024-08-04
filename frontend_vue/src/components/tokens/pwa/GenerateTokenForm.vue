<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormImageSelect
      id="icon"
      label="Select App icon"
      :options="pwaIconService"
      class="mb-16"
    />
    <BaseFormTextField
      id="app_name"
      type="text"
      placeholder="E.g. Password Manager"
      label="App name (optional)"
      helper-message="If you leave this blank, we'll use a reasonable default."
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
