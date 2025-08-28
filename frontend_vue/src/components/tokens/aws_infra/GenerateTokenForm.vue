<template>
  <BaseGenerateTokenSettings
    ref="awsFormRef"
    setting-type="Canarytoken"
  >
    <BaseFormTextField
      id="aws_account_number"
      type="text"
      placeholder="e.g. 012345678901"
      label="AWS account ID"
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
  <GenerateTokenFormInyoni :aws-form-ref="awsFormRef" />
  <GenerateTokenSettingsNotifications
    memo-helper-example="A memo placeholder"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { AWS_REGIONS } from './constants';
import GenerateTokenFormInyoni from './GenerateTokenFormInyoni.vue';

const awsFormRef = ref();
</script>
