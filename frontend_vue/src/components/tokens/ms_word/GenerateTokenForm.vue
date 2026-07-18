<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="flex flex-col gap-16">
      <BaseInputCheckbox
        id="include_text_snippet"
        v-model="includeTextSnippet"
        label="Include custom text in the document"
      />
      <BaseFormTextField
        v-if="includeTextSnippet"
        id="text_snippet"
        label="Document text"
        placeholder="Paste or type the text to include in the document"
        helper-message="Up to 1000 characters."
        :max-length="MAX_MSWORD_TEXT_SNIPPET_LENGTH"
        multiline
        multiline-height="8rem"
        full-width
        required
      />
      <BaseInputCheckbox
        v-if="includeTextSnippet"
        id="text_snippet_base64"
        v-model="textSnippetBase64"
        label="Base64 encode the document text"
      />
    </div>
  </BaseGenerateTokenSettings>
  <GenerateTokenSettingsNotifications
    memo-helper-example="Word document placed at U:\Users\Max\REPORTS\feb.docx"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useField } from 'vee-validate';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';
import { MAX_MSWORD_TEXT_SNIPPET_LENGTH } from '@/components/constants';

const includeTextSnippet = ref(false);
const { value: textSnippetBase64 } = useField<boolean>(
  'text_snippet_base64',
  undefined,
  {
    initialValue: false,
  }
);

watch(includeTextSnippet, (enabled) => {
  if (!enabled) {
    textSnippetBase64.value = false;
  }
});
</script>
