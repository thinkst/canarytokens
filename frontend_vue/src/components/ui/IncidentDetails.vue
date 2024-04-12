<template>
  <div class="pb-32 m-4 bg-white rounded-md">
    <div class="sticky top-[0px] bg-white h-[4vh] flex justify-end">
      <button
        type="button"
        class="px-16"
        @click="emit('close')"
      >
        <font-awesome-icon
          icon="xmark"
          class="w-6 h-6 text-grey-400 hover:text-grey-200"
        />
      </button>
    </div>
    <div class="px-16">
      <!-- Red box with basic info-->
      <section class="p-16 text-white rounded-md bg-red">
        <h2 class="font-semibold">Incident info</h2>
        <ul class="flex flex-col justify-between gap-24 mt-16 md:flex-row">
          <li class="flex flex-col gap-2">
            <span class="text-xs text-red-100">Date</span>
            <span class="font-semibold"
              >{{
                convertUnixTimeStampToDate(props.hitAlert.time_of_hit)
              }} </span
            >
          </li>
          <li class="flex flex-col gap-2">
            <span class="text-xs text-red-100">IP</span>
            <span class="font-semibold">{{ props.hitAlert.geo_info.ip }}</span>
          </li>
          <li class="flex flex-col gap-2">
            <span class="text-xs text-red-100">Channel</span>
            <span class="font-semibold">{{ props.hitAlert.src_ip }}</span>
          </li>
        </ul>
      </section>
      <!-- Details -->
      <section class="grid md:grid-cols-[auto_1fr] gap-32 mt-32 pl-8">
        <template
          v-for="(val, key) in formattedAlertObject"
          :key="key"
        >
          <h3 class="text-grey-500">
            {{ key }}
          </h3>
          <ul
            class="flex flex-col gap-16 pb-16 [&:not(:last-child)]:border-b md:ml-32 border-grey-100"
          >
            <template v-if="typeof val === 'object'">
              <li
                v-for="(subval, subkey) in val"
                :key="subkey"
                class="break-words"
              >
                <span class="block text-xs uppercase text-grey-500">{{
                  subkey
                }}</span>
                <span :class="highlightBoolean(val)">{{ subval }}</span>
              </li>
            </template>
            <template v-else>
              <li
                :key="key"
                :class="highlightBoolean(val)"
                class="break-words"
              >
                {{ val }}
              </li>
            </template>
          </ul>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { HitsType } from '@/components/tokens/types.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';

const props = defineProps<{
  hitAlert: HitsType;
}>();

const emit = defineEmits(['close']);

function highlightBoolean(val: boolean | HitsType | undefined) {
  if (typeof val === 'boolean') {
    return val ? 'text-green' : 'text-red';
  }
}

// Removes null and undefined key/val
function cleanupObject(obj: keyof HitsType) {
  return Object.entries(obj).reduce((acc, [key, value]) => {
    if (value !== null && value !== undefined) {
      //@ts-ignore
      acc[key as keyof HitsType] =
        typeof value === 'object' ? cleanupObject(value) : value;
    }
    return acc;
  }, {} as HitsType);
}

function isNotEmptyObject(
  val: boolean | string[] | undefined | HitsType
): boolean {
  return typeof val === 'object' && Object.keys(val)?.length > 0;
}

const formattedAlertObject = computed(() => {
  const geoInfo = cleanupObject(
    props.hitAlert.geo_info as unknown as keyof HitsType
  );
  const requestHeaders = cleanupObject(
    props.hitAlert.request_headers as unknown as keyof HitsType
  );
  const additionalInfo = cleanupObject(
    props.hitAlert.additional_info as unknown as keyof HitsType
  );
  const requestArgs = cleanupObject(
    props.hitAlert.request_args as unknown as keyof HitsType
  );

  return {
    ...(isNotEmptyObject(geoInfo) && { 'Geo Info': geoInfo }),
    'Is Tor Rely': props.hitAlert.is_tor_relay,
    ...(isNotEmptyObject(requestHeaders) && {
      'Request Headers': requestHeaders,
    }),
    ...(isNotEmptyObject(additionalInfo) && {
      'Additional Info': additionalInfo,
    }),
    ...(isNotEmptyObject(requestArgs) && {
      'Request Args': requestArgs,
    }),
  };
});
</script>

<style scoped>
ul {
  overflow: auto;
}

code {
  font-size: 0.8rem;
  line-height: 0.9rem;
  overflow-wrap: break-word;
}
</style>
