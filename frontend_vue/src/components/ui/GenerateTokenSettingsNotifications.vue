<template>
  <BaseGenerateTokenSettings setting-type="Notifications">
    <div class="flex flex-col gap-8 mb-24 sm:mb-8">
      <BaseFormTextField
        id="email"
        type="text"
        required
        placeholder="your-email@email.com"
        label="I'd like to be notified via Email"
        full-width
      />
      <BaseFormTextField
        v-if="enableWebhook"
        id="webhook_url"
        type="text"
        placeholder="http://your-webhook-url.com"
        label="I'd like to be notified via Webhook"
        full-width
      />
      <button
        class="self-end px-8 py-4 text-xs border rounded-full w-fit grow-0 text-grey-400 border-grey-200 hover:text-green-500 hover:border-green-500"
        @click.prevent="enableWebhook = !enableWebhook"
      >
        <font-awesome-icon
          :icon="!enableWebhook ? 'plus' : 'minus'"
        ></font-awesome-icon>
        Notify via Webhook
      </button>
    </div>

    <BaseFormTextField
      id="memo"
      label="Reminder for this Canarytoken"
      :placeholder="`E.g: ${memoHelperExample}`"
      multiline
      required
      full-width
      helper-message="Reminder note when this token is triggered."
    ></BaseFormTextField>
  </BaseGenerateTokenSettings>
</template>

<script setup lang="ts">
import { ref } from 'vue';
defineProps<{
  memoHelperExample: string;
}>();

const enableWebhook = ref(false);
</script>
