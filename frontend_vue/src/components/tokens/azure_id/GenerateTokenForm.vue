<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="azure_id_cert_file_name"
      type="text"
      placeholder="File Name"
      label="Azure ID certificate name"
      full-width
      helper-message="Add a .pem extension, e.g Code_Sign_Server_3.pem"
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Azure Service Principal Login details on Code Sign Server 3"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
