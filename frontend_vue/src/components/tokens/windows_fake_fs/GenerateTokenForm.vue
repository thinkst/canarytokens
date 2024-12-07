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
        :options="options"
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
import type { SelectOption } from '@/components/base/BaseFormSelect.vue';
const options: SelectOption[] = [
          {value: 'personal_finances', label: 'Personal Finances'},
          {value: 'home_network', label: 'Home Network'},
          {value: 'personal_correspondence', label: 'Personal Correspondence'},
          {value: 'photo_archive', label: 'Photo Archive'},
          {value: 'security_admin', label: 'Cyber Security'},
          {value: 'defense', label: 'Defense'},
          {value: 'network_admin', label: 'IT'},
          {value: 'med_tech', label: 'Medical'},
          ];
</script>
