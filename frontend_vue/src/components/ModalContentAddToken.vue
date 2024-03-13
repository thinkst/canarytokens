<template>
    <img src="../assets/token_icons/s3_bucket.png" alt="Token logo" class="w-[6rem] pb-16" />
    <h2 class="text-xl font-semibold text-center">Name of the token</h2>
    <p class="text-center">Here’s a short description of this token. We can add some lines to give a
        hint and add the documentation link?
        <BaseLinkDocumentation link="#" />
    </p>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';

onMounted(() => {
    console.log('mounted Add token')
})

</script>
