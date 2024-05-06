<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <label
      for="radio-group-action"
      class="mb-8 ml-4 font-semibold text-center"
      >Upload your file</label
    >
    <BaseUploadFile
      id="signed_exe"
      info-allowed-file="EXE, DLL"
    />
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Tokened whoami.exe on web server WEB01"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
