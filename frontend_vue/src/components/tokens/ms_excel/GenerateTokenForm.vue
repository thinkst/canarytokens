<template>
  <BaseGenerateTokenSettings setting-type="Canarytoken">
    <div class="flex flex-col gap-16">
      <BaseSwitch
        id="include_text_snippet"
        v-model="includeTextSnippet"
        label="AI/Agent Guardrail Triggers"
        helper-message="Embed custom text to confound AI Agents"
      />
      <ButtonHowToDeploy
        token-name="MS Excel"
        :is-open="false"
        size="big"
        class="absolute bottom-8 right-8 z-10 top-[9px]"
        @click="handleHowToUseButton"
      />
      <template v-if="includeTextSnippet">
        <BaseFormTextField
          id="text_snippet"
          class="text_snippet_form"
          :value="textSnippet"
          label="Text to embed"
          placeholder="Paste or type the text to include in the document"
          multiline
          multiline-height="8rem"
          :maxLength="5000"
          full-width
          required
        />
        <BaseSwitch
          id="text_snippet_base64"
          :model-value="textSnippetBase64"
          label="Base64 encode text"
          helper-message="Humans may ignore Base64, AI agents usually won't."
          @update:model-value="setTextSnippetBase64"
        />
      </template>
    </div>
  </BaseGenerateTokenSettings>
  <BaseInyoniMessage
    v-if="includeTextSnippet"
    v-model="showInyoni"
    text="We'll embed your text into the document. Different AI agents may respond differently to the prompts, so don't be afraid to experiment."
    class="inyoni_modal"
  />
  <GenerateTokenSettingsNotifications
    memo-helper-example="Excel document placed at U:\Users\Max\feb.xlxs"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useField } from 'vee-validate';
import { prompts } from '@/utils/poisonPillPrompts';
import ButtonHowToDeploy from '@/components/ui/ButtonHowToDeploy.vue';
import GenerateTokenSettingsNotifications from '@/components/ui/GenerateTokenSettingsNotifications.vue';

const showInyoni = ref(false);
const textSnippetBase64 = ref(false);

const { value: includeTextSnippet } = useField<boolean>(
  'include_text_snippet',
  undefined,
  {
    initialValue: false,
  }
);

const { value: textSnippet } = useField<string | undefined>(
  'text_snippet',
  undefined,
  {
    initialValue: undefined,
  }
);

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
      ? encodeText(textSnippet.value || '')
      : decodeText(textSnippet.value || '');
    textSnippetBase64.value = enabled;
  } catch {
    textSnippetBase64.value = !enabled;
  }
}

function handleHowToUseButton() {
  window.open('https://docs.canarytokens.org', '_blank', 'noopener,noreferrer')
}

watch(includeTextSnippet, (enabled) => {
  showInyoni.value = enabled;
  if (!enabled) {
    textSnippetBase64.value = false;
    textSnippet.value = undefined;
    return;
  }
  textSnippet.value = textSnippet.value || prompts.join('\n');
});
</script>

<style scoped lang="scss">
.text_snippet_form {
  anchor-name: --text-snippet-anchor;
}
.inyoni_modal {
  --inyoni-left-position: 300px;
  --inyoni-top-position: 15vh;
  position: absolute;
  top: var(--inyoni-top-position);
  left: var(--inyoni-left-position);
  max-width: 400px;

  @supports (anchor-name: --value) {
    position-anchor: --text-snippet-anchor;
    left: calc(anchor(--text-snippet-anchor left) - 450px);
    top: calc(anchor(--text-snippet-anchor top) - 50px);
  }
}
</style>
