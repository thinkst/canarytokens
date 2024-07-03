<template>
  <TokenIcon
    :title="tokenServices[props.selectedToken].label"
    :logo-img-url="tokenServices[props.selectedToken].icon"
    class="sm:w-[5rem] sm:h-[5rem] w-[7rem] h-[7rem]"
    :is-animation="true"
    :has-shadow="true"
  />
  <div class="w-full md:w-[90%] lg:w-[70%] px-8 mt-32 mb-8">
    <Form
      ref="generateTokenFormRef"
      :validation-schema="schema"
      class="flex flex-col gap-32"
      @submit="onSubmit"
      @invalid-submit="onInvalidSubmit"
    >
      <component :is="dynamicForm" />
    </Form>
    <div class="w-full mt-16 text-left sm:pl-24">
      <p class="text-xs text-grey-400">
        <span class="text-green">*</span> Required field
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, shallowRef, watch } from 'vue';
import type { Ref } from 'vue';
import { tokenServices } from '@/utils/tokenServices';
import { formValidators } from '@/utils/formValidators';
import { Form } from 'vee-validate';
import type { GenericObject } from 'vee-validate';
import TokenIcon from '@/components/icons/TokenIcon.vue';

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
    // When defining an async component
    // Vue adds an __asyncLoader() method to the component instance.
    // This method returns a promise that resolves when the component finishes loading.
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
