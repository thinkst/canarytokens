<template>
  <div
    class="flex flex-col gap-16 p-16 mt-24 mb-32 border border-grey-200 rounded-xl"
  >
    <h3 class="flex flex-row text-sm font-semibold text-left text-grey-400">
      App appareance
    </h3>
    <base-form-select
      id="idp-app-look"
      label="Select App"
      :options="idpOptions"
      placeholder="Select an option"
      @select-option="handleSelectedApp"
    >
      <template #option="{ option }">
        <div class="flex flex-row items-center gap-16">
          <div
            alt="icon"
            :style="{ backgroundImage: `url(${getImageUrl(option.iconUrl)})` }"
            class="bg-cover w-[2rem] h-[2rem] rounded-2xl duration-100"
          ></div>
          {{ option.value }}
        </div>
      </template>

      <template #selected-option="{ option }">
        <div class="flex flex-row items-center gap-16">
          <div
            alt="icon"
            :style="{ backgroundImage: `url(${getImageUrl(option.iconUrl)})` }"
            class="bg-cover w-[1.5rem] h-[1.5rem] rounded-2xl duration-100"
          ></div>
          {{ option.value }}
        </div>
      </template>
    </base-form-select>

    <div class="flex flex-col w-full gap-24 p-16 bg-white rounded-xl">
      <div class="flex flex-col items-center justify-center gap-8">
        <BaseLabelArrow
          id="idp-app-img"
          :arrow-word-position="3"
          label="Download App Icon"
          arrow-variant="one"
          class="text-center"
        />
        <BaseDownloadIconButtom
          :url="selectedApp?.iconUrl && getImageUrl(`${selectedApp?.iconUrl}`)"
          :disabled="!selectedApp?.iconUrl"
        />
      </div>
      <div
        class="flex flex-col items-center justify-center bg-white rounded-2xl"
      >
        <BaseLabelArrow
          id="idp-app-name"
          :arrow-word-position="3"
          label="Copy App name"
          arrow-variant="two"
          class="z-10 text-center"
        />
        <!-- Copy Name Input Readonly -->
        <div
          class="relative flex flex-col w-full max-w-[40ch] items-center gap-8"
        >
          <label
            for="text-input"
            class="sr-only"
            >App name</label
          >
          <input
            id="text-input"
            type="text"
            placeholder="App name"
            :value="selectedApp?.value"
            readonly
            class="h-[3rem] w-full px-16 py-8 border resize-none shadow-inner-shadow-grey rounded-3xl border-grey-400 focus:ring-green-600 focus-visible:ring-1"
          />
          <BaseCopyButton
            :content="selectedApp?.value ? selectedApp?.value : ''"
            :disabled="!selectedApp?.value"
            class="absolute top-8 right-16"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import getImageUrl from '@/utils/getImageUrl';
import { ref } from 'vue';

type SelectedAppType = {
  value: string;
  iconUrl: string;
};

const selectedApp = ref<SelectedAppType>();

const idpOptions = [
  {
    value: 'Custom app',
    iconUrl: 'pwa_icons/pwa_facebook.png',
  },
  {
    value: 'Gmail app',
    iconUrl: 'pwa_icons/pwa_rbc.png',
  },
  {
    value: 'Outlook app',
    iconUrl: 'pwa_icons/pwa_snapchat.png',
  },
];

function handleSelectedApp(selected: { value: string; iconUrl: string }) {
  console.log('Selected app:', selected);
  selectedApp.value = selected;
}
</script>
