<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormSelect
        id="webdav_fs_type"
        label="Folder Contents"
        :options="options"
        placeholder="Select dummy folder content"
      />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Machine and drive letter on which this Network Folder was mapped."
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import type { SelectOption } from '@/components/base/BaseFormSelect.vue';
const options: SelectOption[] = [
          {value: 'security', label: 'Cyber Security'},
          {value: 'defense', label: 'Defense'},
          {value: 'it', label: 'IT'},
          {value: 'medical', label: 'Medical'},
          {value: 'testing', label: 'Test Server'},
          ];
</script>
