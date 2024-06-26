<template>
  <base-message-box
    :variant="'warning'"
    :message="`This token only works on Windows 10 systems and lower. It does
      not work on Windows 11 or higher. This is because a recent group policy update to
      some versions of Windows defaults to disabling functionality that this token
      relies on to fire.`"
  />
  <GenerateTokenSettingsNotifications
    memo-helper-example=" Directory token placed in U:\Users\Max\CrediCardsReports\"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
