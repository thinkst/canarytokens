<template>
  <base-code-snippet
    lang="text"
    label="CloudFormation Quick Create URL"
    :code="tokenData.quickcreate_url"
  ></base-code-snippet>
  <base-button
    class="mt-16"
    @click="handleOpenInAWS"
    >Open in AWS Console</base-button
  >
  <div class="mt-16">
    <p class="text-sm"><strong>Bucket Name:</strong> {{ tokenData.bucket_name }}</p>
    <p class="text-sm"><strong>Region:</strong> {{ tokenData.region }}</p>
  </div>
</template>

<script setup lang="ts">
type AWSS3BucketDataType = {
  quickcreate_url: string;
  bucket_name: string;
  region: string;
};

const props = defineProps<{
  tokenData: AWSS3BucketDataType;
}>();

function handleOpenInAWS() {
  window.open(props.tokenData.quickcreate_url, '_blank');
}
</script>
