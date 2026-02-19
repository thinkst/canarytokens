<template>
  <section class="p-16 rounded-md"
    :class="{'bg-red': incidentStatus === TOKEN_HIT_STATUS.ALERTABLE, 'bg-grey-100': incidentStatus !== TOKEN_HIT_STATUS.ALERTABLE, 'text-white': incidentStatus === TOKEN_HIT_STATUS.ALERTABLE, 'text-grey-800': incidentStatus !== TOKEN_HIT_STATUS.ALERTABLE}"
  >
  <div class="flex flex-row justify-between">
    <h2 class="font-semibold">Incident info</h2>
    <span
      v-if="incidentStatus === TOKEN_HIT_STATUS.IGNORED_IP"
      class="text-xs text-white bg-grey rounded-lg px-4 py-[2px]"
    >
    Ignored IP
    </span>
    </div>
    <ul class="flex flex-col justify-between gap-24 mt-16 md:flex-row">
      <li class="flex flex-col gap-2">
        <span class="text-xs text-red-100">Date</span>
        <span class="font-semibold">{{ date }} </span>
      </li>
      <li
        v-if="ip"
        class="flex flex-col gap-2"
      >
        <span class="text-xs text-red-100">IP</span>
        <span class="font-semibold">{{ ip }}</span>
      </li>
      <li
        v-if="inputChannel"
        class="flex flex-col gap-2"
      >
        <span class="text-xs text-red-100">Channel</span>
        <span class="font-semibold">{{ inputChannel }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { TOKEN_HIT_STATUS } from '@/components/constants';

defineProps<{
  date: string | number;
  ip?: string | null;
  inputChannel: string;
  incidentStatus: string;
}>();
</script>
