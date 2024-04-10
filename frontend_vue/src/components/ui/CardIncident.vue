<template>
  <li class="w-full">
    <button
      v-bind="$attrs"
      class="text-grey-700 flex flex-row gap-16 relative border grouped flex-1 group px-16 py-8 bg-white rounded-xl top-[0px] shadow-solid-shadow-grey border-grey-200 items-center duration-100 ease-in-out error-card w-full"
      @click.stop="handleClickError"
    >
      <AlertShieldIcon
        class="min-w-[40px] group-hover:fill-red group-focus:fill-red group-active:fill-red fill-grey-700"
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
.error-card:focus {
  @apply border-red top-[-0.45em] shadow-solid-shadow-red;
}

.error-card:active {
  @apply border-red top-[0em] shadow-none;
}
</style>
