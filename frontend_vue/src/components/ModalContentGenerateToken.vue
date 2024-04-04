<template>
  <img
    :src="
      getImgUrl(`token_icons/${tokensOperations[props.selectedToken].icon}`)
    "
    :alt="`${tokensOperations[props.selectedToken].label}`"
    class="w-[6rem] pb-16"
  />
  <h2 class="text-xl font-semibold leading-4 text-center">
    {{ tokensOperations[props.selectedToken].label }}
  </h2>
  <p class="text-center">
    {{ tokensOperations[props.selectedToken].description }}
    <BaseLinkDocumentation
      :link="tokensOperations[props.selectedToken].documentationLink"
    />
  </p>
  <Form
    ref="myForm"
    :validation-schema="schema"
    class="flex flex-col gap-16 px-32 mt-32"
    @submit="onSubmit"
    @invalid-submit="onInvalidSubmit"
  >
    <component :is="dynamicComponent" />
  </Form>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, watch } from 'vue';
import * as Yup from 'yup';
import { useTokens } from '@/composables/useTokens';
import useImage from '@/composables/useImage';
import { Form } from 'vee-validate';
import type { GenericObject } from 'vee-validate';

const props = defineProps<{
  selectedToken: string;
  clickSubmit: boolean;
}>();

const emits = defineEmits(['token-generated', 'invalid-submit']);

const { tokensOperations } = useTokens();
const { getImgUrl } = useImage();

const dynamicComponent = ref(null);
const myForm = ref(null);

const schema = Yup.object().shape({
  email: Yup.string().email().required(),
  memo: Yup.string().required(),
});

function onSubmit(values: GenericObject) {
  console.log(values, 'submit!');
  emits('token-generated', { values });
}

function onInvalidSubmit(values: GenericObject) {
  console.log('onInvalidSubmit', values);
  emits('invalid-submit', values);
}

function programaticSubmit() {
  if (myForm.value) {
    myForm.value.$el.requestSubmit();
  }
}

watch(
  props,
  () => {
    if (props.clickSubmit === true) return programaticSubmit();
  },
  {
    immediate: true,
    deep: true,
  }
);

const loadComponent = async () => {
  dynamicComponent.value = defineAsyncComponent(
    () =>
      import(`@/components/tokens/${props.selectedToken}/GenerateTokenForm.vue`)
  );
};

loadComponent();
</script>
