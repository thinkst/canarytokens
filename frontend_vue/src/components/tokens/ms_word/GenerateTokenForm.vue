<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="flex flex-col gap-16">
      <BaseInputCheckbox
        id="include_text_snippet"
        v-model="includeTextSnippet"
        label="Include custom text in the documents"
      />
      <BaseFormTextField
        v-if="includeTextSnippet"
        id="text_snippet"
        label="Document textes"
        placeholder="Paste or type the text to include in the document"
        helper-message="Up to 1000 characters."
        :max-length="MAX_MSWORD_TEXT_SNIPPET_LENGTH"
        multiline
        multiline-height="8rem"
        full-width
        required
      />
      <fieldset
        class="text-placement-options"
        :disabled="!includeTextSnippet"
      >
        <legend>Document text placement</legend>
        <label>
          <input
            id="text_snippet_placement_metadata"
            v-model="textSnippetPlacement"
            type="radio"
            name="text_snippet_placement"
            value="metadata"
            :disabled="!includeTextSnippet"
          />
          Hidden in document metadata
        </label>
        <label>
          <input
            id="text_snippet_placement_plaintext"
            v-model="textSnippetPlacement"
            type="radio"
            name="text_snippet_placement"
            value="plaintext"
            :disabled="!includeTextSnippet"
          />
          Inserted as plaintext in the document
        </label>
      </fieldset>
      <!-- <BaseInputCheckbox
        id="text_snippet_base64"
        v-model="textSnippetBase64"
        label="Base64 encode the document text"
        :disabled="!includeTextSnippet"
      /> -->
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
const { value: textSnippetPlacement } = useField<string>(
  'text_snippet_placement',
  undefined,
  {
    initialValue: 'metadata',
  }
);
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
    textSnippetPlacement.value = 'metadata';
  }
});
</script>

<style scoped lang="scss">
.text-placement-options {
  border: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0;

  legend {
    color: var(--color-grey-500);
    margin-bottom: 0.5rem;
  }

  label {
    align-items: center;
    color: var(--color-grey-500);
    display: flex;
    gap: 0.5rem;
  }

  &:disabled {
    label,
    legend {
      color: var(--color-grey-300);
    }
  }
}
</style>
