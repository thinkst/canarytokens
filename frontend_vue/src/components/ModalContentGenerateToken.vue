<template>
  <div class="icon-shadow">
    <img
      :src="
        getImageUrl(`token_icons/${tokenServices[props.selectedToken].icon}`)
      "
      :alt="`${tokenServices[props.selectedToken].label}`"
      class="w-[5rem]"
    />
  </div>
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
import { defineAsyncComponent, ref, shallowRef, watch } from 'vue';
import type { Ref } from 'vue';
import getImageUrl from '@/utils/getImageUrl';
import { tokenServices } from '@/utils/tokenServices';
import { formValidators } from '@/utils/formValidators';
import { Form } from 'vee-validate';
import type { GenericObject } from 'vee-validate';

const props = defineProps<{
  selectedToken: string;
  triggerSubmit: boolean;
}>();

const emits = defineEmits(['token-generated', 'invalid-submit', 'is-loading']);

const dynamicForm = shallowRef();
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
  emits('is-loading', true);
  try {
    dynamicForm.value = defineAsyncComponent(
      () =>
        import(
          `@/components/tokens/${props.selectedToken}/GenerateTokenForm.vue`
        )
    );
    await dynamicForm.value.__asyncLoader();

    emits('is-loading', false);
  } catch (error) {
    emits('is-loading', false);
    console.error(error);
  }
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

<style scoped>
.icon-shadow::after {
  content: '';
  position: relative;
  display: inline-block;
  width: 5rem;
  height: 0.5rem;
  border-radius: 50%;
  @apply bg-grey-100;
  filter: blur(0.1rem);
  transform: scale(0.7);
}
</style>
