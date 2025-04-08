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
    <BaseFormSelect
      id="aws_region"
      label="AWS Region"
      :options="AWS_REGIONS"
      placeholder="Select AWS region"
      required
      searchable
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="A memo placeholder"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { AWS_REGIONS } from './constants';
</script>
