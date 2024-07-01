<template>
  <BaseGenerateTokenSettings setting-type="Notifications">
    <div class="flex flex-col gap-8 mb-8">
      <BaseFormTextField
        id="email"
        type="text"
        required
        placeholder="your-email@email.com"
        label="Mail me here when the alert fires"
        full-width
      />
    </div>

    <BaseFormTextField
      id="memo"
      label="Remind me of this when the alert fires"
      :placeholder="`E.g: ${memoHelperExample}`"
      multiline
      required
      full-width
    ></BaseFormTextField>
    <button
      class="self-end px-8 py-4 mb-8 text-xs border rounded-full w-fit grow-0 text-grey-400 border-grey-200 hover:text-green-500 hover:border-green-500"
      @click.prevent="enableWebhook = !enableWebhook"
    >
      <font-awesome-icon
        :icon="!enableWebhook ? 'plus' : 'minus'"
      ></font-awesome-icon>
      Add Webhook Notification
    </button>
    <BaseFormTextField
      v-if="enableWebhook"
      id="webhook_url"
      type="text"
      placeholder="http://your-webhook-url.com"
      label="Notify me here when the alert fires"
      full-width
    />
  </BaseGenerateTokenSettings>
</template>

<script setup lang="ts">
import { ref } from 'vue';
defineProps<{
  memoHelperExample: string;
}>();

const enableWebhook = ref(false);
</script>
