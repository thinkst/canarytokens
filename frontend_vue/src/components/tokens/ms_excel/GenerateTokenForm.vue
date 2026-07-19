<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="flex flex-col gap-16">
      <BaseSwitch
        id="include_text_snippet"
        v-model="includeTextSnippet"
        label="Embed custom text"
        helper-message="For experimenting with AI agent prompt injection."
      />
      <BaseFormTextField
        v-if="includeTextSnippet"
        id="text_snippet"
        :value="textSnippet"
        label="Text to embed"
        placeholder="Paste or type the text to include in the document"
        multiline
        multiline-height="8rem"
        full-width
        required
        @input="syncTextSnippet"
      />
      <BaseSwitch
        v-if="includeTextSnippet"
        id="text_snippet_base64"
        :model-value="textSnippetBase64"
        label="Base64 encode text"
        helper-message="Toggle between base64 encoded and plaintext text."
        @update:model-value="setTextSnippetBase64"
      />
      <div>
        <BaseFormSelect
          v-if="includeTextSnippet"
          id="text_snippet_placement"
          label="Document text placement"
          :options="textSnippetPlacementOptions"
          :value="textSnippetPlacementOptions[0]"
          :searchable="false"
        />
      </div>
    </div>
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Excel document placed at U:\Users\Max\feb.xlxs"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useField } from 'vee-validate';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import type { SelectOption } from '@/components/base/BaseFormSelect.vue';

const includeTextSnippet = ref(false);
const textSnippetBase64 = ref(false);
const textSnippetPlacementOptions: SelectOption[] = [
  { value: 'metadata', label: 'Hidden in document metadata' },
  { value: 'plaintext', label: 'Inserted as plaintext in the document' },
];
const { value: textSnippet } = useField<string>('text_snippet', undefined, {
  initialValue: '',
});

function syncTextSnippet(event: Event) {
  textSnippet.value = (event.target as HTMLTextAreaElement).value;
}

function encodeText(text: string) {
  const bytes = new TextEncoder().encode(text);
  let binary = '';
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function decodeText(text: string) {
  const binary = atob(text);
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

function setTextSnippetBase64(enabled: boolean) {
  if (enabled === textSnippetBase64.value) return;

  try {
    textSnippet.value = enabled
      ? encodeText(textSnippet.value)
      : decodeText(textSnippet.value);
    textSnippetBase64.value = enabled;
  } catch {
    textSnippetBase64.value = !enabled;
  }
}

watch(includeTextSnippet, (enabled) => {
  if (!enabled) {
    textSnippetBase64.value = false;
  }
});
</script>
