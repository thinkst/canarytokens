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
</template>

<script setup lang="ts">
// For internal use only
// TODO: show this component only for DEV env or behind VPN
import { useModal } from 'vue-final-modal';
import ModalAddToken from '@/components/ModalAddToken.vue';
import { ref, watch } from 'vue';

const { open } = useModal({
  component: ModalAddToken,
});

const checked = ref(false);
const checkedDisabled = ref(false);

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
</style>
```
