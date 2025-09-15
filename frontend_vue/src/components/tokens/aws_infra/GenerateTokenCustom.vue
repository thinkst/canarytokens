<template>
  <GenerateTokenIntro
    v-if="showIntro"
    @start-token-setup="showIntro = false"
  />
  <TokenSetupWizard v-else />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import GenerateTokenIntro from '@/components/tokens/aws_infra/GenerateTokenIntro.vue';
import TokenSetupWizard from '@/components/tokens/aws_infra/TokenSetupWizard.vue';

const showIntro = ref(true);
</script>

<style></style>
