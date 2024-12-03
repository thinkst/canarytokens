<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="flex flex-col gap-8 mb-8">
      <BaseFormSelect
        id="app_type"
        label="Select App"
        placeholder="Select an app"
        :options="IDP_OPTIONS"
        @select-option="handleSelectedApp"
      >
        <template #option="{ option }">
          <div class="flex flex-row items-center gap-16">
            <div
              alt="icon"
              :style="{ backgroundImage: `url(${getImageUrl('idp_icons/'+option.value+'.png')})` }"
              class="bg-cover w-[2rem] h-[2rem] rounded-2xl duration-100"
            ></div>
            {{ option.label }}
          </div>
        </template>

        <template #selected-option="{ option }">
          <div class="flex flex-row items-center gap-16">
            <div
              alt="icon"
              :style="{ backgroundImage: `url(${getImageUrl('idp_icons/'+option.value+'.png')})` }"
              class="bg-cover w-[1.5rem] h-[1.5rem] rounded-2xl duration-100"
            ></div>
            {{ option.label }}
          </div>
        </template>
      </BaseFormSelect>
    </div>
    <BaseFormTextField
      id="redirect_url"
      type="text"
      placeholder="Redirect URL"
      label="Optional Redirect URL"
      full-width
    />
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
