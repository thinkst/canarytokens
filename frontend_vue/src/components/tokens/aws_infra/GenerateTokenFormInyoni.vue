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
const supportsAnchorPositioning = CSS.supports('anchor-name', '--value');

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

  if (!supportsAnchorPositioning) {
    setStyleForInyoni();
  }
}, 200);

const setStyleForInyoni = () => {
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
};
</script>

<style scoped lang="scss">
.inyoni_modal {
  --inyoni-left-position: 300px;
  --inyoni-top-position: 15vh;
  position: absolute;
  top: var(--inyoni-top-position);
  left: var(--inyoni-left-position);
  max-width: 400px;

  @supports (anchor-name: --value) {
    position-anchor: --aws-form;
    left: calc(anchor(--aws-form left) - 400px);
    top: calc(anchor(--aws-form top) - 110px);
  }
}
</style>
