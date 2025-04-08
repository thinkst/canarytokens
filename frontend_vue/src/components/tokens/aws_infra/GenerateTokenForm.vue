<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="aws_account_number"
      type="text"
      placeholder="e.g. 123456"
      label="AWS account number"
      full-width
      required
    />
    <!-- TODO: Add region dropdown values -->
    <BaseFormTextField
      id="aws_region"
      type="text"
      placeholder="e.g. mordor-west-1"
      label="AWS Region"
      full-width
      required
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="A memo placeholder"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
