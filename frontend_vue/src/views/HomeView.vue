<template>
  <AppLayoutGrid>
    <CardToken
      title="Very long long title"
      description="Alert when a Kubeconfig Token is used"
      logoImgUrl="token_icons/s3_bucket.png"
      documentationLink="#"
    />
    <CardToken
      title="Very short"
      description="A description for a token, it’s very long and goes on three lines!"
      logoImgUrl="token_icons/s3_bucket.png"
      documentationLink="#"
    />
    <CardToken
      title="Very loooon title that might go 3 lines"
      description="Another description for this token"
      logoImgUrl="token_icons/s3_bucket.png"
      documentationLink="#"
    />
    <CardToken
      title="Very short"
      description="Another description for this token"
      logoImgUrl="token_icons/s3_bucket.png"
      documentationLink="123"
    />
  </AppLayoutGrid>
</template>

<script setup lang="ts">
import AppLayoutGrid from '@/layout/AppLayoutGrid.vue';
import CardToken from '@/components/CardToken.vue';
</script>
