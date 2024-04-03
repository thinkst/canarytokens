<template>
  <base-text-field
    id="urltoken"
    v-model="formData.webhook_url"
    type="text"
    placeholder="Url"
    label="Email or webhook URL"
    full-width
    helper-message="Provide an email address or webhook URL, or both space separated"
  />
  <base-text-field
    id="memo"
    v-model="formData.memo"
    label="Add Note"
    multiline
    full-width
  ></base-text-field>
</template>

<script setup lang="ts">
import { useGenerateTokenForm } from '@/composables/useGenerateTokenForm';

type mySQLFormType = {
  email: string;
  webhook_url: string;
  memo: string;
};

const { formData } = useGenerateTokenForm<mySQLFormType>({
  webhook_url: '',
  memo: '',
  email: '',
});
</script>
