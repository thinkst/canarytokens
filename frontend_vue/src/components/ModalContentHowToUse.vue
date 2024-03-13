<template>
    <div class="modal-content">
        <ul class="flex flex-col gap-16 fa-ul items-left intro text-grey-800">
            <li>
                In an email with a juicy subject line.
            </li>
            <li>
                Embedded in documents.
            </li>
            <li>
                In an email with a juicy subject line.
            </li>
            <li>
                This URL is just an example. Apart from the hostname and the actual token (the random string), you
                can change all other parts of the URL.
            </li>
        </ul>
    </div>

</template>

<script setup lang="ts">
import { onMounted } from 'vue';

onMounted(() => {
    console.log('How to use?')
})

</script>

<style>
.fa-ul>li::before {
    content: "\f059";
    font-family: "Font Awesome 6 Free";
    color: hsl(36, 100%, 50%);
    display: inline-block;
    width: 1.5em;
    margin-left: -1.5em;
}
</style>
