<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseLabel
      id="signed_exe"
      class="text-center"
      >Upload your file</BaseLabel
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
