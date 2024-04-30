<template>
  <ul class="ml-24">
    <h3 class="text-grey-500">{{ formatKey(keyName) }}:</h3>
    <template
      v-for="(val, key) in data"
      :key="key"
    >
      <li class="pb-16 ml-16">
        <span class="block text-xs uppercase text-grey-500">{{
          formatKey(key)
        }}</span>
        <span :class="highlightBoolean(val as boolean)">{{ val }}</span>
      </li>
    </template>
  </ul>
  <div class="border-b border-grey-100"></div>
</template>

<script lang="ts" setup>
import { formatKey } from '@/utils/utils';

defineProps<{
  data: Record<string, unknown>;
  keyName: string;
}>();

function highlightBoolean(val: boolean | string | undefined) {
  if (typeof val === 'boolean') {
    return val ? 'text-green' : 'text-red';
  }
}
</script>
