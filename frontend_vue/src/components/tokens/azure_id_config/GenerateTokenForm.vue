<template>
  <!-- 
    hidden field for expected_referrer 
    doesn't require user input 
  -->
  <BaseFormTextField
    id="expected_referrer"
    class="hidden"
    label="hidden"
    value="microsoftonline.com"
  />
  <GenerateTokenSettingsNotifications
    memo-helper-example="Entra ID token for the Thinkst Azure tenant with ID:"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
