<template>
    <div class="modal-content">
        <img src="../assets/token_icons/s3_bucket_active.png" alt="Token logo" class="w-[8rem]" />
        <h2 class="text-xl font-semibold text-center">Your S3 bucket Token is active!</h2>
        <p class="text-sm text-center">Copy this URL to your clipboard and use as you wish</p>
    </div>

    <div class="copy-token">
        <!-- add here token url, code and whatever else -->
    </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';

onMounted(() => {
    console.log('Token is active')
})
</script>
