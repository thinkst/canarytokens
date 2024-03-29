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
import { useNewTokenForm } from '@/composables/useNewTokenForm';

type webFormType = {
  webhook_url: '';
  memo: '';
};

const { formData } = useNewTokenForm<webFormType>({
  webhook_url: '',
  memo: '',
});
</script>
