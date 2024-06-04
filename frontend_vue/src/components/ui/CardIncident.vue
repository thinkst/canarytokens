<template>
  <li class="w-full">
    <button
      v-bind="$attrs"
      class="relative w-full px-16 py-8 transition duration-100 bg-white border text-grey-700 grouped group rounded-xl shadow-solid-shadow-grey border-grey-200 error-card"
      :class="{ 'mb-8': lastKey }"
      @click.stop="handleClickError"
    >
      <span class="flex flex-row items-center flex-1 gap-16">
        <AlertShieldIcon
          class="min-w-[30px] group-hover:fill-red group-focus:fill-red group-active:fill-red fill-grey-700 group-hover:scale-95 transition duration-200"
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
      </span>
      <span
        class="flex flex-row items-center justify-end gap-8 mt-8 font-semibold text-red sm:hidden"
        >Check Incident
        <font-awesome-icon
          icon="arrow-right"
          class="text-red"
          aria-hidden="true"
      /></span>
    </button>
  </li>
</template>

<script setup lang="ts">
import AlertShieldIcon from '@/components/icons/AlertShieldIcon.vue';

type incidentPreviewInfoType = {
  [key: string]: string | Date;
};

defineProps<{
  lastKey: boolean,
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
