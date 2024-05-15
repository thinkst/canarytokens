<template>
  <img
    :src="getImageUrl(`token_icons/${tokenServices[props.selectedToken].icon}`)"
    :alt="`${tokenServices[props.selectedToken].label}`"
    class="w-[6rem] pb-16"
  />
  <h2 class="mb-16 text-xl font-semibold leading-tight text-center">
    {{ tokenServices[props.selectedToken].label }}
  </h2>
  <component
    :is="dynamicCarousel"
    v-bind="{ selectedToken }"
  />
  <Form
    ref="generateTokenFormRef"
    :validation-schema="schema"
    class="flex flex-col w-full md:w-[90%] lg:w-[70%] gap-32 px-8 mt-32 mb-16"
    @submit="onSubmit"
    @invalid-submit="onInvalidSubmit"
  >
    <component :is="dynamicForm" />
  </Form>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, watch } from 'vue';
import type { Ref } from 'vue';
import { tokenServices } from '@/utils/tokenServices';
import { formValidators } from '@/utils/formValidators';
import getImageUrl from '@/utils/getImageUrl';
import { Form } from 'vee-validate';
import type { GenericObject } from 'vee-validate';

const props = defineProps<{
  selectedToken: string;
  triggerSubmit: boolean;
}>();

const emits = defineEmits(['token-generated', 'invalid-submit']);

const dynamicForm = ref();
const dynamicCarousel = ref();
const generateTokenFormRef: Ref<HTMLFormElement | null> = ref(null);

const schema = formValidators[props.selectedToken].schema;

function onSubmit(values: GenericObject) {
  emits('token-generated', values);
}

function onInvalidSubmit(values: GenericObject) {
  emits('invalid-submit', values);
}

function programaticSubmit() {
  if (generateTokenFormRef.value) {
    generateTokenFormRef.value.$el.requestSubmit();
  }
}

const loadComponent = async () => {
  dynamicForm.value = defineAsyncComponent(
    () =>
      import(`@/components/tokens/${props.selectedToken}/GenerateTokenForm.vue`)
  );
  dynamicCarousel.value = defineAsyncComponent(
    () => import('@/components/ui/CarouselInfoToken.vue')
  );
};

loadComponent();

watch(
  props,
  () => {
    if (props.triggerSubmit === true) return programaticSubmit();
  },
  {
    immediate: true,
    deep: true,
  }
);
</script>
