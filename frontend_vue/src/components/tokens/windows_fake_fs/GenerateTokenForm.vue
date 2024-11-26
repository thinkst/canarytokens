<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <BaseFormTextField
      id="windows_fake_fs_root"
      type="text"
      placeholder="C:\Secrets"
      label="Where will this directory be placed?"
      full-width
      required
    />
    <div class="flex flex-col gap-16">
      <BaseFormSelect
        id="windows_fake_fs_file_structure"
        label="Create (fake) files for the following Industry/Sector"
        :options="['option1', 'option2', 'option3']"
        placeholder="Choose an Industry/Sector"
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
