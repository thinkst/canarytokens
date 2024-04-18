<!-- TODO: the JavascriptObfuscator package is not working at the moment 
we need to fix this dependency to show the obfuscated code
-->
<template>
  <base-code-snippet
    lang="javascript"
    label="Your tokened Javascript"
    multiline
    custom-height="8rem"
    :code="codeClonedSite"
  >
  </base-code-snippet>
  <!-- <base-switch
    id="obfuscated_code"
    v-model="obfuscated_code"
    class="mt-16"
    label="Obfuscate this script"
    helper-message="Show Obfuscated JavaScript"
    @input.stop="handleEncodingChange()"
  ></base-switch> -->
</template>

<script setup lang="ts">
import { ref } from 'vue';
// import type { Ref } from 'vue';
// import obfuscateToken from './obfuscateToken';

const props = defineProps<{
  tokenSnippet: string;
}>();

const codeClonedSite = ref(props.tokenSnippet);
// const obfuscated_code: Ref<boolean> = ref(false);

// function handleEncodingChange() {
//   obfuscated_code.value = !obfuscated_code.value;
//   if (obfuscated_code.value === true)
//     codeClonedSite.value = obfuscateToken(props.tokenSnippet);
// }
</script>
