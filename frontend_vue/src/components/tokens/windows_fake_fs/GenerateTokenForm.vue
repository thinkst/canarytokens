<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="windows_fake_fs_root"
      type="text"
      placeholder="Directory Path"
      label="The root directory for the fake file system"
      helper-message="C:\Secrets"
      full-width
      required
    />
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <BaseFormSelect
        id="windows_fake_fs_file_structure"
        label="Industry Generated File Tree"
        :options="['option1', 'option2', 'option3']"
        placeholder="Select an option"
        full-width
        required
      />
    </div>
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Fake file system token on off-site backup server"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
</script>
