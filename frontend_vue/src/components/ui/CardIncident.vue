<template>
  <li class="w-full">
    <button
      v-bind="$attrs"
      class="relative flex flex-row items-center flex-1 w-full gap-16 px-16 py-8 bg-white border text-grey-700 grouped group rounded-xl shadow-solid-shadow-grey border-grey-200 error-card"
      @click.stop="handleClickError"
    >
      <AlertShieldIcon
        class="min-w-[30px] group-hover:fill-red group-focus:fill-red group-active:fill-red fill-grey-700"
        aria-hidden="true"
      />
      <span class="text-left">
        <span
          v-for="(val, key) in incidentPreviewInfo"
          :key="key"
          class="block"
        >
          <span class="capitalize text-grey-400">{{ key }}: </span>
          <span class="mr-8 font-semibold">{{ val }}</span>
        </span>
      </span>
    </button>
  </li>
</template>

<script setup lang="ts">
import AlertShieldIcon from '@/components/icons/AlertShieldIcon.vue';

type incidentPreviewInfoType = {
  [key: string]: string | Date;
};

defineProps<{
  incidentPreviewInfo: incidentPreviewInfoType;
  incidentId: number | string;
}>();

const emits = defineEmits(['click']);

function handleClickError() {
  emits('click');
}
</script>

<style scoped>
.error-card:hover,
.error-card:focus,
.error-card:active {
  @apply border-red shadow-solid-shadow-red;
}
</style>
