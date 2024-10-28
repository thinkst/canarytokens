<template>
  <TokenIcon
    :title="tokenServices[props.selectedToken].label"
    :logo-img-url="tokenServices[props.selectedToken].icon"
    class="sm:w-[5rem] sm:h-[5rem] w-[7rem] h-[7rem]"
    :is-animation="true"
    :has-shadow="true"
  />
  <div class="w-full md:w-[90%] lg:w-[70%] px-8 mt-32 mb-24">
    <Form
      ref="generateTokenFormRef"
      :validation-schema="schema"
      class="flex flex-col gap-32"
      @submit="onSubmit"
      @invalid-submit="onInvalidSubmit"
    >
      <component :is="dynamicForm" />
    </Form>
	  <vue-turnstile
      v-if="selectedToken == TOKENS_TYPE.CREDIT_CARD_V2"
      class="flex align-center justify-center mt-24"
      :site-key="cloudflareSiteKey"
      theme="light"
      v-model="cloudflareResponse"
    />
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
import { TOKENS_TYPE } from './constants';
import VueTurnstile from 'vue-turnstile';

const props = defineProps<{
  selectedToken: string;
  triggerSubmit: boolean;
}>();

const emits = defineEmits(['token-generated', 'invalid-submit', 'is-loading']);

const dynamicForm = shallowRef();
const generateTokenFormRef: Ref<HTMLFormElement | null> = ref(null);

const cloudflareResponse: Ref<string> = ref('');
const cloudflareSiteKey: string = import.meta.env.VITE_CLOUDFLARE_TURNSTILE_SITE_KEY;

const schema = formValidators[props.selectedToken].schema;

function onSubmit(values: GenericObject) {
  if (props.selectedToken == TOKENS_TYPE.CREDIT_CARD_V2) {
    values['cf_turnstile_response'] = cloudflareResponse.value;
  }

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
