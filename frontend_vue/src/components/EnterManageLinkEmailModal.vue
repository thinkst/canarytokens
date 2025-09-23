<template>
  <BaseButton
    class="mt-16 md:mt-0 uppercase my-token-btn text-sm"
    variant="primary"
    @click.stop="showModal = true"
  >
    My Tokens
  </BaseButton>

  <BaseModal
    v-model="showModal"
    title="Access Your Tokens"
    :has-close-button="true"
  >
    <div
      v-if="isSuccess"
      class="text-center my-32"
    >
      <h3 class="text-2xl font-semibold mb-16">Success!</h3>
      <p class="mb-16">
        If the email you provided is associated with any tokens, you will
        receive an email shortly with links to manage them.
      </p>
      <p class="text-sm text-blue-700">
        <strong>Don't see the email?</strong> Check your spam folder if you have many tokens.
      </p>
    </div>

    <template v-else>
      <Form
        ref="formRef"
        :validation-schema="{
          email: Yup.string()
            .email('Invalid email')
            .required('Email is required'),
        }"
        @submit="onSubmit"
      >
        <BaseFormTextField
          id="email"
          ref="emailInput"
          type="text"
          required
          placeholder="your-email@example.com"
          label="Email Address"
          helper-message="We'll send you links to manage all your tokens."
          full-width
          :disabled="disabled"
          @keydown.enter.prevent="handleEnterKey"
        />

        <vue-turnstile
          v-model="token"
          class="flex align-center justify-center mt-24"
          :site-key="cloudflareSiteKey"
          theme="light"
        />
      </Form>

      <BaseMessageBox
        v-if="errorMessage"
        class="mt-24"
        variant="danger"
        :message="errorMessage"
      />
    </template>

    <template #footer>
      <BaseButton
        v-if="isSuccess"
        variant="primary"
        @click="showModal = false"
      >
        Close
      </BaseButton>

      <BaseButton
        v-else
        variant="primary"
        :loading="loading"
        :disabled="disabled"
        @click.stop="programaticSubmit"
      >
        Submit
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { sendUserTokenFetchLinks } from '@/api/main';
import { computed, nextTick, ref, watch } from 'vue';
import VueTurnstile from 'vue-turnstile';
import { Form } from 'vee-validate';
import * as Yup from 'yup';
import type { GenericObject } from 'vee-validate';
import { launchConfetti } from '@/utils/confettiEffect';


const showModal = ref(false);
const cloudflareSiteKey: string = import.meta.env
  .VITE_CLOUDFLARE_TURNSTILE_SITE_KEY;
const token = ref('');
const emailInput = ref();
const formRef = ref();
const errorMessage = ref('');
const loading = ref(false);
const disabled = computed(() => loading.value || !token.value);
const isSuccess = ref(false);

watch(token, (newVal) => {
  if (newVal) {
    nextTick(() => {
      const inputElement = emailInput.value?.$el.querySelector('input');
      if (inputElement) {
        inputElement.focus();
      }
    });
  }
});

watch(showModal, (newValue) => {
  if (!newValue) {
    token.value = '';
    errorMessage.value = '';
    loading.value = false;
    isSuccess.value = false;
    if (formRef.value) {
      formRef.value.resetForm();
    }
  }
});

const handleEnterKey = (event: KeyboardEvent) => {
  // Force update the field value first
  const input = event.target as HTMLInputElement;
  if (formRef.value && input.value) {
    formRef.value.setFieldValue('email', input.value);
    // Then submit
    nextTick(() => {
      programaticSubmit();
    });
  }
};

const programaticSubmit = () => {
  if (formRef.value) {
    formRef.value.$el.requestSubmit();
  }
};

const onSubmit = async (values: GenericObject) => {
  errorMessage.value = '';
  const email = values.email;

  if (!token.value || !email || loading.value) {
    return;
  }

  try {
    loading.value = true;
    await sendUserTokenFetchLinks(token.value, email);
    isSuccess.value = true;
    nextTick(() => {
      launchConfetti('')
    });
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.message || 'An error occurred.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.my-token-btn {
  font-weight: normal;
  color: #0D7764;
  @apply bg-white hover:bg-white active:bg-white focus:bg-white;
}
</style>