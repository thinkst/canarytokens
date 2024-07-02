<template>
  <TokenDisplay :token-snippet="tokenSnippet" />
  <p class="mt-16 text-sm">
    Use this CSS to detect when someone has cloned a webpage.
  </p>
  <BaseMessageBox
    class="mt-24"
    variant="info"
    message="    When someone clones your site, they'll load the token, which will check
    whether the referrer domain is expected. If not, it fires the token and you
    get an alert."
    text-link="More tips?"
    @click="() => $emit('howToUse')"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TokenDisplay from './TokenDisplay.vue';
import type { NewTokenBackendType } from '@/components/tokens/types';

const props = defineProps<{
  tokenData: NewTokenBackendType;
}>();

defineEmits(['howToUse']);

const tokenSnippet = ref(props.tokenData.css || '');
</script>
