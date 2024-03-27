<template>
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Buttons</h1>
    <base-button>Primary</base-button>
    <base-button variant="secondary">Secondary</base-button>
    <base-button variant="text">Text!!</base-button>
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
  <div class="flex flex-col w-[200px] gap-16">
    <h1>Switch</h1>
    <BaseSwitch
      id="check"
      v-model="checked"
      :label="`Checked? ${checked}`"
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
    <h1>Text Fields</h1>
    <div class="flex flex-col gap-16 pl-16 flex-nowrap">
      <h2>Input field</h2>
      <div class="flex flex-wrap items-center gap-16">
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Standalone input"
          placeholder="This is a great input"
        ></BaseTextField>
        vmodel output: {{ inputValue }}
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Full width input"
          placeholder="This is a great input"
          full-width
        ></BaseTextField>
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Custom label very long"
          placeholder="This is a great input"
          helper-message="This is an helper for the user, so they know what to do"
        ></BaseTextField>
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Disabled input"
          disabled
          placeholder="This is a great input"
        ></BaseTextField>
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Custom label required"
          required
          placeholder="This is a great input"
        ></BaseTextField>
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Custom label required"
          required
          placeholder="This is a great input"
        ></BaseTextField>
        <BaseTextField
          id="test input"
          v-model="inputValue"
          label="Error input"
          placeholder="This is a great input"
          :has-error="true"
          error-message="Error message here"
        ></BaseTextField>
      </div>
    </div>
    <div>
      <hr class="my-24" />
      <h1 class="pb-16">Custom Map</h1>
      <CustomMap />
    </div>
    <hr class="my-24" />
    <h1 class="pb-16">Incident details</h1>
    <div class="flex flex-col gap-16 px-16 py-16 mb-32 bg-grey-100">
      <IncidentDetails />
    </div>
    <div class="flex flex-col gap-16 mb-32">
      <h1>Upload File</h1>
      <BaseUploadFile
        allowed-files="image/png, image/svg+xml"
        info-allowed-file="SVG or PNG"
        :max-size="200000"
        @file-selected="handleFileSelected"
      />
      <BaseUploadFile
        allowed-files="image/png, image/svg+xml"
        info-allowed-file="SVG, PNG, JPG or GIF"
        :has-error="true"
        error-message="Custom error message!"
      />
      Disabled
      <BaseUploadFile
        allowed-files="image/png, image/svg+xml"
        info-allowed-file="SVG, PNG, JPG or GIF"
        disabled
      />
      File selected name: {{ fileSelected?.name }}
    </div>
  </div>
</template>

<script setup lang="ts">
// For internal use only
// TODO: show this component only for DEV env or behind VPN
import { useModal } from 'vue-final-modal';
import ModalAddToken from '@/components/ModalAddToken.vue';
import CardIncident from '@/components/CardIncident.vue';
import CustomMap from '@/components/CustomMap.vue';
import IncidentDetails from '@/components/IncidentDetails.vue';
import { ref, watch } from 'vue';

const { open } = useModal({
  component: ModalAddToken,
});

const checked = ref(false);
const checkedDisabled = ref(false);
const inputValue = ref('');
const fileSelected = ref();

function handleFileSelected(event: DragEvent) {
  fileSelected.value = event;
}

watch(checked, (newVal) => {
  console.log('checked', newVal);
});
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
