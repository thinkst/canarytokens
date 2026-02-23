<template>
  <section class="p-16 rounded-md"
    :class="[sectionBackgroundClass, sectionTextClass]"
  >
  <div class="flex flex-row justify-between">
    <h2 class="font-semibold">Incident info</h2>
    <BasePill
      v-if="incidentStatus === TOKEN_HIT_STATUS.IGNORED_IP"
      colour="grey"
    >
    Ignored IP
    </BasePill>
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
import { computed } from 'vue';
import { TOKEN_HIT_STATUS } from '@/components/constants';
import BasePill from '../base/BasePill.vue';

const props = defineProps<{
  date: string | number;
  ip?: string | null;
  inputChannel: string;
  incidentStatus: string;
}>();

const sectionBackgroundClass = computed(() => {
  return props.incidentStatus === TOKEN_HIT_STATUS.ALERTABLE ? 'bg-red' : 'bg-grey-100';
});

const sectionTextClass = computed(() => {
  return props.incidentStatus === TOKEN_HIT_STATUS.ALERTABLE ? 'text-white' : 'text-grey-800';
});
</script>
