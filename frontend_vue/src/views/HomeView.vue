<template>
  <AppLayoutGrid>
    <BaseCardToken
      title="Very long long title"
      description="Alert when a Kubeconfig Token is used"
    />
    <BaseCardToken
      title="Very short"
      description="A description for a token, it’s very long and goes on three lines!"
    />
    <BaseCardToken
      title="Very loooon title that might go 3 lines"
      description="Another description for this token"
    />
    <BaseCardToken
      title="Very short"
      description="Another description for this token"
    />
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
</script>
