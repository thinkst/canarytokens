<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="flex flex-col gap-8">
      <BaseFormSelect
        id="app_type"
        label="The App I want my Canarytoken to look like"
        placeholder="Select an app"
        required
        :options="IDP_OPTIONS"
        :searchable="true"
        height="220px"
        @select-option="handleSelectedApp"
      >
        <template #option="{ option }">
          <div class="flex flex-row items-center gap-16">
            <div
              alt="icon"
              :style="{ backgroundImage: `url(${getImageUrl('idp_icons/'+option.value+'.png')})` }"
              class="bg-cover w-[2rem] h-[2rem] duration-100"
            ></div>
            {{ option.label }}
          </div>
        </template>

        <template #selected-option="{ option }">
          <div class="flex flex-row items-center gap-16">
            <div
              alt="icon"
              :style="{ backgroundImage: `url(${getImageUrl('idp_icons/'+option.value+'.png')})` }"
              class="bg-cover w-[1.5rem] h-[1.5rem] duration-100"
            ></div>
            {{ option.label }}
          </div>
        </template>
      </BaseFormSelect>
      <BaseFormTextField
        id="redirect_url"
        type="text"
        label="Send the user to this URL on login (Optional)"
        placeholder="https://www.example.com"
        full-width
      />
    </div>
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Fake Salesforce app in Okta"
  />
</template>

<script setup lang="ts">
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import getImageUrl from '@/utils/getImageUrl';
import { IDP_OPTIONS } from '@/components/constants';
import { ref } from 'vue';

type SelectedAppType = {
  value: string;
  label: string;
};

const selectedApp = ref<SelectedAppType>();

function handleSelectedApp(selected: string) {
  selectedApp.value = IDP_OPTIONS.find(o => o.value === selected);
}
</script>
