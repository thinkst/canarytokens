<template>
  <BaseInyoniMessage
    v-model="showInyoni"
    text="We aren’t logging into your account — we just need the info to prepare scripts for you."
    :class="isSmallScreen ? '' : 'inyoni_modal'"
    :hide-close-button="isSmallScreen"
  />
</template>

<script lang="ts" setup>
import { onMounted, onUnmounted, ref, toRef } from 'vue';
import { debounce } from '@/utils/utils';

const props = defineProps<{
  awsFormRef: any;
}>();

const showInyoni = ref(true);
const isSmallScreen = ref(false);
const awsFormRef = toRef(props, 'awsFormRef');

onMounted(() => {
  updateInyoniPosition();
  window.addEventListener('resize', updateInyoniPosition);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateInyoniPosition);
});

const updateInyoniPosition = debounce(() => {
  if (window.innerWidth <= 1024) {
    isSmallScreen.value = true;
  } else {
    isSmallScreen.value = false;
  }
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
}, 200);
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
