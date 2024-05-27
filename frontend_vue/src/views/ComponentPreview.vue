<template>
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Buttons</h1>
    <base-button>Primary</base-button>
    <base-button variant="secondary">Secondary</base-button>
    <base-button variant="text">Text!!</base-button>
    <base-button
      class="whitespace-nowrap"
      icon="arrow-right"
      icon-position="right"
      >Look mum, Icons!</base-button
    >
    <base-button :loading="true">Loading</base-button>

    <base-button
      :loading="true"
      icon="arrow-right"
      icon-position="right"
      variant="secondary"
      >Loading</base-button
    >
    <base-button :disabled="true">Disabled</base-button>
  </div>
  <hr class="my-24" />
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Modal</h1>
    <BaseButton @click="() => open()">Check modal</BaseButton>
  </div>
  <hr class="my-24" />
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Copy button</h1>
    <BaseCopyButton content="Content to copy is here" />
  </div>
  <hr class="my-24" />
  <div class="flex flex-col w-[300px] gap-16">
    <h1>Switch</h1>
    <BaseSwitch
      id="check"
      v-model="checked"
      :label="`Checked? ${checked}`"
    />
    <BaseSwitch
      id="check"
      v-model="checked"
      :label="`Checked? ${checked}`"
      helper-message="My custom helper message"
    />
    <BaseSwitch
      id="check"
      v-model="checked"
      :label="`Checked? ${checked}, With loading! `"
      :loading="true"
    />
    <BaseSwitch
      id="checkDisabled"
      v-model="checkedDisabled"
      label="Checked with error"
      error-message="Oh snap, something went wrong!"
    />
    <BaseSwitch
      id="checkDisabled"
      v-model="checkedDisabled"
      label="Checked disabled"
      disabled
    />
  </div>
  <hr class="my-24" />
  <div class="flex flex-col gap-16">
    <h1>Message Box</h1>
    <BaseMessageBox
      message="This is a danger message This is a danger message This is a danger message This is a danger message This is a danger message"
      text-link="Click here"
      variant="danger"
      @click="console.log('danger!')"
    />
    <BaseMessageBox
      message="This is a warning message This is a warning message This is a warning message"
      text-link="Link here"
      variant="warning"
      @click="console.log('warning!')"
    />
    <BaseMessageBox
      message="This is a info message This is a info message."
      text-link="Check here"
      variant="info"
      @click="console.log('info!')"
    />
    <BaseMessageBox
      message="This is a message without link "
      variant="info"
    />
  </div>
  <hr class="my-24" />
  <div class="flex flex-col gap-16 w-[400px]">
    <h1>Card Incident</h1>
    <ul>
      <CardIncident
        :incident-preview-info="{
          date: '2024-03-22 16:01:08.976860',
          IP: '84.138.198.174',
          Channel: 'HTTP',
        }"
        incident-id="12345"
      />
    </ul>
  </div>
  <hr class="my-24" />
  <div class="flex flex-col gap-16">
    <h1>Form Text Fields</h1>
    <div class="flex flex-col gap-16 pl-16 flex-nowrap">
      <h2>Input field</h2>
      <div class="flex flex-wrap items-center gap-16">
        <BaseFormTextField
          id="test input"
          label="Standalone input"
          placeholder="This is a great input"
        ></BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Full width input"
          placeholder="This is a great input"
          full-width
        ></BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Custom label very long"
          placeholder="This is a great input"
          helper-message="This is an helper for the user, so they know what to do"
        ></BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Disabled input"
          disabled
          placeholder="This is a great input"
        ></BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Custom label required"
          required
          placeholder="This is a great input"
        ></BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Custom label required"
          required
          placeholder="This is a great input"
        ></BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Error input"
          placeholder="This is a great input"
          :has-error="true"
          error-message="Error message here"
        ></BaseFormTextField>
      </div>
    </div>
    <div>
      <hr class="my-24" />
      <h1 class="pb-16">Custom Map</h1>
      <CustomMap
        :hits-list="[]"
        style="height: 30svh"
      />
    </div>
    <hr class="my-24" />
    <h1 class="pb-16">Incident details</h1>
    <div class="flex flex-col gap-16 px-16 py-16 mb-32 bg-grey-100">
      <IncidentDetails :hit-alert="alertSample" />
    </div>
    <div class="flex flex-col gap-16 mb-32">
      <h1>Upload File</h1>
      <BaseUploadFile
        id="upload"
        @file-selected="handleFileSelected"
      />
      Disabled
      <BaseUploadFile
        id="disabled-upload"
        disabled
      />
      File selected name: {{ fileSelected?.name }}
    </div>
    <div>
      <hr class="my-24" />
      <h1 class="pb-16">Code Snippet</h1>

      <BaseCodeSnippet
        has-refresh
        class="mb-16"
        label="Single line"
        lang="javascript"
        code="http://canarytokens.com/traffic/ttg75cc1ah5ae4f24o6767csk/post.jsp"
      />

      <BaseCodeSnippet
        multiline
        label="Multiline - Javascript"
        :code="codeSnippet"
        lang="javascript"
      />
    </div>
    <hr class="my-24" />
    <h1>Banner ADV</h1>
    <BannerDeviceCanarytools />
    <BannerBirdCanarytools />
    <div>
      <hr class="my-24" />
      <h1 class="mb-16">Select component</h1>
      <BaseFormSelect
        id="my-select"
        label="Label here"
        :options="['option1', 'option2', 'option3']"
        placeholder="Select an option"
      />
    </div>
  </div>
  <hr class="my-24" />

  <div class="flex flex-col gap-16">
    <h1>Spinner</h1>
    <BaseSpinner />
    <div class="p-16 bg-green-500">
      <BaseSpinner variant="secondary" />
    </div>
  </div>
  <hr class="my-24" />
  <div class="flex flex-col gap-16">
    <h1>Radio Button</h1>
    <BaseRadioInput
      id="pizza"
      label="Pizza"
      name="radio-group-name"
    />
    <BaseRadioInput
      id="pasta"
      label="Pasta"
      name="radio-group-name"
    />
    <BaseRadioInput
      id="carbonara"
      label="Carbonara"
      name="radio-group-name"
    />
  </div>
  <hr class="my-24" />
  <h1>Skeleton Loader</h1>
  <div class="flex flex-col gap-16 mt-24 mb-32">
    <BaseSkeletonLoader
      class="h-[100px] w-[300px]"
      type="rectangle"
    />
    <BaseSkeletonLoader
      class="h-[100px] w-[100px]"
      type="circle"
    />
    <div class="flex flex-col gap-8">
      <BaseSkeletonLoader
        class="w-[100px]"
        type="header"
      />
      <BaseSkeletonLoader
        class="w-[300px]"
        type="text"
      />
      <BaseSkeletonLoader
        class="w-[300px]"
        type="text"
      />
      <BaseSkeletonLoader
        class="w-[200px]"
        type="text"
      />
    </div>
    <div>
      <hr class="my-24" />
      <h1>Search bar</h1>
      <div class="flex flex-col gap-16 mt-24 mb-32">
        <SearchBar
          label="Search"
          placeholder="A nice placeholder"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// For internal use only
// TODO: show this component only for DEV env or behind VPN
import { useModal } from 'vue-final-modal';
import ModalToken from '@/components/ModalToken.vue';
import CardIncident from '@/components/ui/CardIncident.vue';
import CustomMap from '@/components/ui/CustomMap.vue';
import IncidentDetails from '@/components/ui/IncidentDetails.vue';
import SearchBar from '@/components/ui/SearchBar.vue';
import { ref } from 'vue';
import BannerDeviceCanarytools from '@/components/ui/BannerDeviceCanarytools.vue';
import BannerBirdCanarytools from '@/components/ui/BannerBirdCanarytools.vue';

const { open } = useModal({
  component: ModalToken,
  attrs: {
    selectedToken: 'web',
    closeModal: () => close(),
  },
});

const checked = ref(false);
const checkedDisabled = ref(false);
const fileSelected = ref();

function handleFileSelected(event: DragEvent) {
  fileSelected.value = event;
}

const codeSnippet = ref(`const tooltipText = ref('Copy to clipboard');
const isTriggered = ref(false);
const tooltipTriggers = ref(['hover', 'focus']);

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// 1. prevents UI from jumping when tooltip content changes
// 2. shows tooltip when content is copied
async function showTooltip() {
  if (!isSupported) return (tooltipText.value = 'Copy not supported');
  await delay(150);
  tooltipTriggers.value = [];
  isTriggered.value = true;
  tooltipText.value = 'Copied!';
  // vTooltip sets a default delay of 1.5s
  await delay(1500);
  isTriggered.value = false;
  tooltipTriggers.value = ['hover', 'focus'];
  await delay(150);
  tooltipText.value = 'Copy to clipboard';
}

function copyContent() {
  copy(props.content);
  showTooltip();
}`);

const alertSample = {
  time_of_hit: 1712839716.1747,
  src_ip: '13.245.103.199',
  geo_info: {
    loc: '-33.9258,18.4232',
    org: 'AS16509 Amazon.com, Inc.',
    city: 'Cape Town',
    country: 'ZA',
    region: 'Western Cape',
    hostname: 'ec2-13-245-103-199.af-south-1.compute.amazonaws.com',
    ip: '13.245.103.199',
    timezone: 'Africa/Johannesburg',
    postal: '7945',
    asn: null,
    readme: 'https://ipinfo.io/missingauth',
  },
  is_tor_relay: false,
  input_channel: 'HTTP',
  src_data: null,
  useragent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  token_type: 'web',
  request_headers: {
    Host: 'maxoooo.com',
    'X-Real-Ip': '13.245.103.199',
    'X-Forwarded-For': '13.245.103.199',
    'X-Forwarded-Host': 'maxoooo.com',
    Connection: 'close',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    Accept:
      'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language':
      'en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6,it;q=0.5',
  },
  request_args: {},
  additional_info: {
    javascript: null,
    browser: null,
    mysql_client: null,
    r: null,
    l: null,
  },
};
</script>

<style scoped>
h1 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
  text-transform: uppercase;
}

h2 {
  font-size: 0.8rem;
  font-weight: 600;
  color: #333;
  text-transform: uppercase;
}

hr {
  color: #e3e3e3;
}
</style>
```
