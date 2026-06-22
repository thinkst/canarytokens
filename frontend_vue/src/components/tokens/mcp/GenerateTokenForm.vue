<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormSelect
        id="mcp_alert_on"
        label="Alert on"
        :options="options"
        placeholder="Choose token alerting behaviour"
      />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="MCP config placed on build server"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import type { SelectOption } from '@/components/base/BaseFormSelect.vue';
const options: SelectOption[] = [
  {value: 'connect', label: 'Connection'},
  {value: 'tool_call', label: 'MCP Tool Call'},
  ];
</script>
