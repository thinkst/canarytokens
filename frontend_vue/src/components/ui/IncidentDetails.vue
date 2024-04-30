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
      <IncidentDetailsSummary :hit-alert="hitAlert" />
      <!-- Details -->
      <section class="grid md:grid-cols-[auto_1fr] gap-32 mt-32 pl-8">
        <template
          v-for="(val, key) in hitAlert"
          :key="key"
        >
          <h3 class="text-grey-500">
            {{ formatKey(key) }}
          </h3>
          <ul
            class="flex flex-col gap-16 pb-16 [&:not(:last-child)]:border-b md:ml-32 border-grey-100"
          >
            <template v-if="!isObject(val)">
              <li
                :key="key"
                :class="highlightBoolean(val)"
                class="break-words"
              >
                {{ val }}
              </li>
            </template>

            <!-- first level nested object -->
            <template v-else>
              <ul
                v-for="(subval, subkey) in val"
                :key="subkey"
                class="break-words"
              >
                <li v-if="!isObject(subval)">
                  <span class="block text-xs uppercase text-grey-500">{{
                    formatKey(subkey)
                  }}</span>
                  <span :class="highlightBoolean(val)">{{ subval }}</span>
                </li>

                <!-- second level nested object -->
                <template v-else>
                  <IncidentDetailsDeepNestedList
                    :data="subval"
                    :key-name="subkey"
                  />
                </template>
              </ul>
            </template>
          </ul>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HitsType } from '@/components/tokens/types.ts';
// import { convertUnixTimeStampToDate } from '@/utils/utils';
import IncidentDetailsDeepNestedList from '@/components/ui/IncidentDetailsDeepNestedList.vue';
import IncidentDetailsSummary from '@/components/ui/IncidentDetailsSummary.vue';
import { isObject, formatKey } from '@/utils/utils';

// defineProps<{
//   hitAlert: HitsType;
// }>();

const emit = defineEmits(['close']);

function highlightBoolean(val: boolean | HitsType | undefined) {
  if (typeof val === 'boolean') {
    return val ? 'text-green' : 'text-red';
  }
}

const hitAlert = {
  time_of_hit: 0,
  src_ip: '123.123.123.123',
  geo_info: {
    loc: [],
    org: 'string',
    city: 'string',
    country: 'string',
    region: 'string',
    hostname: 'string',
    ip: 'string',
    timezone: 'string',
    postal: 'string',
    asn: {
      route: 'string',
      type: 'string',
      asn: 'string',
      domain: 'string',
      name: 'string',
    },
    readme: 'string',
  },
  is_tor_relay: true,
  input_channel: 'HTML',
  src_data: {},
  useragent: 'string',
  token_type: 'cc',
};
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
