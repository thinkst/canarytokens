<template>
  <div class="relative">
    <h1>Inyoni chirping</h1>
    <div class="w-[50vw] m-24">
      <BaseInyoniMessage
        v-model="showInyoni"
        text="Here's an example of the Inyoni component in action! You can close me by clicking the 'X' button."
      />
    </div>
  </div>
  <div>
    <hr class="my-24" />
    <h1>Bullet List</h1>
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <BaseBulletList
        :list="['element number 1', 'element number 2', 'element number 3']"
      />
    </div>
  </div>
  <div>
    <hr class="my-24" />
    <h1>Step State</h1>
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <p>Loading State</p>
      <StepState
        loading-message="Hold on, we are doing things"
        :is-loading="true"
      />
      <p>Error State</p>
      <StepState
        :is-error="true"
        error-message="Oh snap, an error :("
      />
    </div>
  </div>
  <div>
    <hr class="my-24" />
    <h1>Checkbox input</h1>
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <BaseInputCheckbox
        id="pizza"
        v-model="checkBoxValue"
        label="Confirming my love for pizza 🍕 "
        class="text-sm"
      />
      <div class="mt-8">Checkbox value: {{ checkBoxValue }}</div>
      <BaseInputCheckbox
        id="tooltip-checkbox"
        v-model="checkBoxTooltipValue"
        label="I have a tooltip "
        class="text-sm"
        tooltip-content="Boo!"
      />
      <BaseInputCheckbox
        id="disabled"
        v-model="checkBoxDisabledValue"
        :disabled="true"
        label="Disabled checkbox"
        class="text-sm"
      />
    </div>
  </div>
  <div>
    <hr class="my-24" />
    <h1>Step Counter</h1>
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <BaseStepCounter
        :steps="[
          { label: 'Very long name' },
          { label: 'Example 2' },
          { label: 'Example 3' },
          { label: 'Example long name' },
          { label: 'Example 5' },
        ]"
        :current-step="currentStep"
        @handle-step-click="(e) => (currentStep = e)"
      />
      <div class="flex gap-24 mt-16">
        Current step: {{ currentStep }}
        <button @click="currentStep--">Prev Step</button>
        <button @click="currentStep++">Next Step</button>
      </div>
    </div>
    <hr class="my-24" />
    <h1>Image Select</h1>
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <BaseFormImageSelect
        id="image-select"
        label="Select an image"
        :options="[
          { value: 'image1', url: `${getImageUrl('pwa_icons/pwa_fnb.png')}` },
          { value: 'image2', url: `${getImageUrl('pwa_icons/pwa_axis.png')}` },
          { value: 'image3', url: `${getImageUrl('pwa_icons/pwa_rbc.png')}` },
          {
            value: 'image4',
            url: `${getImageUrl('pwa_icons/pwa_tiktok.png')}`,
          },
        ]"
      />
      <BaseFormImageSelect
        id="image-select-big"
        label="Select an image"
        image-class="w-[100px] h-[100px]"
        :options="[
          {
            value: 'image5',
            url: `${getImageUrl('pwa_icons/pwa_snapchat.png')}`,
          },
          {
            value: 'image6',
            url: `${getImageUrl('pwa_icons/pwa_paypal.png')}`,
          },
          {
            value: 'image7',
            url: `${getImageUrl('pwa_icons/pwa_messenger.png')}`,
          },
          {
            value: 'image8',
            url: `${getImageUrl('pwa_icons/pwa_tiktok.png')}`,
          },
        ]"
      />
    </div>
  </div>
  <div>
    <hr class="my-24" />
    <h1>Search bar</h1>
    <div class="flex flex-col gap-16 mt-24 mb-32">
      <SearchBar
        label="Search"
        placeholder="A nice placeholder"
        value=""
      />
    </div>
  </div>
  <div class="flex flex-col max-w-[200px] gap-16">
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
  <div class="flex flex-col max-w-[200px] gap-16">
    <h1>Modal</h1>
    <BaseButton @click="() => open()">Check modal</BaseButton>
  </div>
  <hr class="my-24" />
  <div class="flex flex-col max-w-[200px] gap-16">
    <h1>Copy button</h1>
    <BaseCopyButton content="Content to copy is here" />
    <BaseCopyButton
      content="Content to copy is here"
      disabled
    />
  </div>
  <hr class="my-24" />
  <div class="flex flex-col max-w-[300px] gap-16">
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
  <div class="flex flex-col gap-16 max-w-[400px]">
    <h1>Card Incident</h1>
    <ul>
      <CardIncident
        :last-key="false"
        :incident-preview-info="{
          date: '2024-03-22 16:01:08.976860',
          IP: '84.138.198.174',
          Channel: 'HTTP',
        }"
        incident-id="12345"
        incident-status="alertable"
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
        >
        </BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Full width input"
          placeholder="This is a great input"
          full-width
        >
        </BaseFormTextField>
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
        >
        </BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Custom label required"
          required
          placeholder="This is a great input"
        >
        </BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Custom label required"
          required
          placeholder="This is a great input"
        >
        </BaseFormTextField>
        <BaseFormTextField
          id="test input"
          label="Error input"
          placeholder="This is a great input"
          :has-error="true"
          error-message="Error message here"
        ></BaseFormTextField>
        <BaseFormTextField
          id="email"
          type="text"
          required
          placeholder="your-email@example.com"
          label="Arrow in third position"
          full-width
          :has-arrow="true"
          arrow-variant="two"
          :arrow-word-position="3"
        />
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
      <IncidentDetails
        :hit-alert="alertSample"
        :showing-map="true"
        token-type="aws_keys"
      />
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
        is-single-line
        class="mb-16 max-w-[300px] sm:max-w-full"
        label="Single line"
        lang="javascript"
        code="http://canarytokens.com/traffic/ttg75cc1ah5ae4f24o6767csk/post.jsp"
      />

      <BaseCodeSnippet
        has-refresh
        is-single-line
        class="mb-16 max-w-[300px] sm:max-w-full"
        label="Single line"
        lang="javascript"
        code="http://canarytokens.com/traffic/ttg75cc1ah5ae4f24o6767csk/post.jsp"
      />

      <BaseCodeSnippet
        multiline
        class="max-w-[300px] sm:max-w-full"
        label="Multiline - Javascript"
        :code="codeSnippet"
        lang="javascript"
      />
    </div>
    <hr class="my-24" />
    <h1>Banner ADV</h1>
    <BannerDeviceCanarytools />
    <BannerBirdCanarytools />
    <div class="mt-24 mb-32">
      <BannerTextCanarytools />
    </div>
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
        class="max-w-[200px]"
        type="text"
      />
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
import BannerTextCanarytools from '@/components/ui/BannerTextCanarytools.vue';
import getImageUrl from '@/utils/getImageUrl';
import StepState from '@/components/tokens/aws_infra/StepState.vue';

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
const currentStep = ref(1);
const checkBoxValue = ref(false);
const checkBoxDisabledValue = ref(false);
const checkBoxTooltipValue = ref(false);
const showInyoni = ref(true);

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
  token_type: 'aws_keys',
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
    aws_key_log_data: {
      last_used: '2022-07-29T05:48:00+00:00',
      service_used: 'service test value',
      eventName: ['DescribeInstances'],
    },
    file_path: '/blah/foo/moo.txt',
  },
  location: null,
  alert_status: 'alertable',
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
