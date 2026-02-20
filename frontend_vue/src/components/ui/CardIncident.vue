<template>
  <li class="w-full @container">
    <button
      v-bind="$attrs"
      class="relative w-full px-16 py-8 transition duration-100 bg-white border text-grey-700 grouped group rounded-2xl shadow-solid-shadow-grey border-grey-200"
      :class="{ 'mb-8': lastKey, 'error-card': incidentStatus === TOKEN_HIT_STATUS.ALERTABLE, 'info-card': incidentStatus !== TOKEN_HIT_STATUS.ALERTABLE }"
      @click.stop="handleClickError"
    >
      <span class="flex flex-row items-center flex-1 gap-16">
        <AlertShieldIcon
          v-if="incidentStatus === TOKEN_HIT_STATUS.ALERTABLE"
          class="hidden @xs:block min-w-[30px] group-hover:fill-red group-focus:fill-red group-active:fill-red fill-grey-700 group-hover:scale-95 transition duration-200"
          aria-hidden="true"
        />
        <IgnoredAlertShieldIcon
          v-if="incidentStatus === TOKEN_HIT_STATUS.IGNORED_IP"
          class="hidden @xs:block min-w-[30px] fill-grey-700 group-hover:scale-95 transition duration-200"
          aria-hidden="true"
        />
        <span class="text-left">
          <span
            v-for="(val, key) in incidentPreviewInfo"
            :key="key"
            class="block"
          >
            <span
              v-if="val !== null"
              class="capitalize text-grey-400"
              >{{ key }}:
            </span>
            <span
              v-if="val !== null"
              class="mr-8 font-semibold"
              >{{ val }}</span
            >
            <BasePill
              v-if="key === 'IP' && incidentStatus === TOKEN_HIT_STATUS.IGNORED_IP"
              class="ml-8"
              background-colour="grey-400"
            >
              Ignored IP
            </BasePill>
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
import { TOKEN_HIT_STATUS } from '@/components/constants';
import IgnoredAlertShieldIcon from '@/components/icons/IgnoredAlertShieldIcon.vue';

type incidentPreviewInfoType = {
  [key: string]: string | Date | null;
};

defineProps<{
  lastKey: boolean;
  incidentPreviewInfo: incidentPreviewInfoType;
  incidentId: number | string;
  incidentStatus: string;
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

.info-card:hover,
.info-card:focus,
.info-card:active {
  @apply border-grey-400 shadow-solid-shadow-grey-400;
}
</style>
