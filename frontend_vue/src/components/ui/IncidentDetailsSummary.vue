<template>
  <section class="p-16 text-white rounded-md bg-red">
    <h2 class="font-semibold">Incident info</h2>
    <ul class="flex flex-col justify-between gap-24 mt-16 md:flex-row">
      <li class="flex flex-col gap-2">
        <span class="text-xs text-red-100">Date</span>
        <span class="font-semibold"
          >{{ convertUnixTimeStampToDate(hitAlert.time_of_hit) }} </span
        >
      </li>
      <li class="flex flex-col gap-2">
        <span class="text-xs text-red-100">IP</span>
        <span class="font-semibold">{{ hitAlert.src_ip }}</span>
      </li>
      <li class="flex flex-col gap-2">
        <span class="text-xs text-red-100">Channel</span>
        <span class="font-semibold">{{
          hasChannelCustomLabel(hitAlert.token_type)
        }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import type { HitsType } from '@/components/tokens/types.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';
import { INCIDENT_CHANNEL_TYPE_LABELS } from '@/components/constants';

defineProps<{
  hitAlert: HitsType;
}>();

// Some tokens have a custom Channel label
function hasChannelCustomLabel(type: string) {
  return INCIDENT_CHANNEL_TYPE_LABELS.hasOwnProperty(type)
    ? INCIDENT_CHANNEL_TYPE_LABELS[
        type as keyof typeof INCIDENT_CHANNEL_TYPE_LABELS
      ]
    : type;
}
</script>
