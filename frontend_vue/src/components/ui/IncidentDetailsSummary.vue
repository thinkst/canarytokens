<template>
  <section class="p-16 text-white rounded-md bg-red">
    <h2 class="font-semibold">Incident info</h2>
    <ul class="flex flex-col justify-between gap-24 mt-16 md:flex-row">
      <li class="flex flex-col gap-2">
        <span class="text-xs text-red-100">Date</span>
        <span class="font-semibold">{{ date }} </span>
      </li>
      <li v-if="ip" class="flex flex-col gap-2">
        <span class="text-xs text-red-100">IP</span>
        <span class="font-semibold">{{ ip }}</span>
      </li>
      <li class="flex flex-col gap-2">
        <span class="text-xs text-red-100">Channel</span>
        <span class="font-semibold">{{ inputChannel }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  date: string | number;
  ip: string;
  inputChannel: string;
}>();
</script>
