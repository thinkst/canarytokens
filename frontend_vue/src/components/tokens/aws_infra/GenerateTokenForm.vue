<template>
  <BaseInyoniMessage
    v-model="showInyoni"
    text="We aren’t logging into your account - we just need the info to prepare scripts for you."
    class="inyoni_modal hidden lg:flex"
  />
  <BaseGenerateTokenSettings
    ref="awsFormRef"
    setting-type="Canarytoken"
  >
    <BaseFormTextField
      id="aws_account_number"
      type="text"
      placeholder="e.g. 012345678901"
      label="AWS account ID"
      full-width
      required
    />
    <BaseFormSelect
      id="aws_region"
      label="AWS Region"
      :options="AWS_REGIONS"
      placeholder="Select AWS region"
      required
      searchable
    />
  </BaseGenerateTokenSettings>
  <BaseInyoniMessage
    v-model="showInyoni"
    text="We aren’t logging into your account - we just need the info to prepare scripts for you."
    class="sm:flex lg:hidden"
    :hide-close-button="true"
  />
  <GenerateTokenSettingsNotifications
    memo-helper-example="A memo placeholder"
  />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { AWS_REGIONS } from './constants';

const showInyoni = ref(true);
const awsFormRef = ref();

onMounted(() => {
  updateInyoniPosition();
  if (window.innerWidth >= 1024) {
    window.addEventListener('resize', updateInyoniPosition);
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', updateInyoniPosition);
});

function updateInyoniPosition() {
  const currentFormWidth = awsFormRef.value?.$el.offsetWidth;
  const currentFormTopDistance =
    awsFormRef.value?.$el.getBoundingClientRect().top + window.scrollY;
  const inyoniElement = document.querySelector('.inyoni_modal') as HTMLElement;

  inyoniElement.style.setProperty(
    '--inyoni-left-position',
    `calc(50% - ${currentFormWidth + 200}px)`
  );

  inyoniElement.style.setProperty(
    '--inyoni-top-position',
    `calc(${currentFormTopDistance}px - 120px)`
  );
}
</script>

<style scoped lang="scss">
.inyoni_modal {
  --inyoni-left-position: 300px;
  --inyoni-top-position: 15vh;
  position: absolute;
  top: var(--inyoni-top-position);
  left: var(--inyoni-left-position);
  width: 100%;
  max-width: 400px;
  z-index: 10;
}
</style>
