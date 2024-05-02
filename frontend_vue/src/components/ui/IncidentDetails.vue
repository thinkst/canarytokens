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
      <!-- Red box with Summary -->
      <IncidentDetailsSummary
        v-if="builtIncidentDetail"
        :date="builtIncidentDetail?.time_of_hit"
        :ip="builtIncidentDetail.src_ip"
        :input-channel="builtIncidentDetail.basic_info.input_channel"
      />
      <!-- Details -->
      <section class="grid md:grid-cols-[auto_1fr] gap-32 mt-32 pl-8">
        <template
          v-for="(val, key) in formattedIncidentDetail"
          :key="key"
        >
          <h3 class="text-grey-500">
            {{ key }}
          </h3>
          <ul
            class="flex flex-col gap-16 pb-16 [&:not(:last-child)]:border-b md:ml-32 border-grey-100"
          >
            <IncidentDetailsListItem
              v-if="!isObject(val)"
              :value="val"
            />
            <template v-else>
              <ul
                v-for="(subval, subkey) in val"
                :key="subkey"
                class="break-words"
              >
                <IncidentDetailsListItem
                  v-if="!isObject(subval)"
                  :label="subkey"
                  :value="subval"
                />
                <template v-else>
                  <ul class="ml-24">
                    <h3 class="text-grey-500">{{ subkey }}:</h3>
                    <template
                      v-for="(subsubval, subsubkey) in subval"
                      :key="subsubkey"
                    >
                      <IncidentDetailsListItem
                        :label="subsubkey"
                        :value="subsubval"
                      />
                    </template>
                  </ul>
                  <div class="border-b border-grey-100"></div>
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
import { ref, onMounted } from 'vue';
import type { Ref } from 'vue';
import type { HitsType, FormattedHitsType } from '@/components/tokens/types.ts';
import IncidentDetailsListItem from '@/components/ui/IncidentDetailsListItem.vue';
import IncidentDetailsSummary from '@/components/ui/IncidentDetailsSummary.vue';
import { isObject } from '@/utils/utils';
import {
  formatLabels,
  removeNullEmptyObjectsAndArrays,
  buildIncidentDetails,
} from '@/utils/incidentAlertService';

const props = defineProps<{
  hitAlert: HitsType;
}>();

const emit = defineEmits(['close']);
const builtIncidentDetail: Ref<FormattedHitsType | null> = ref(null);
const formattedIncidentDetail = ref({});

onMounted(() => {
  // Map & cleanup hitAlert
  builtIncidentDetail.value = buildIncidentDetails(props.hitAlert);
  builtIncidentDetail.value = removeNullEmptyObjectsAndArrays(
    builtIncidentDetail.value as FormattedHitsType
  );

  // Make the list UI friendly
  formattedIncidentDetail.value = formatLabels(
    builtIncidentDetail.value as FormattedHitsType
  );
  console.log(formattedIncidentDetail.value, 'uiFriendlyIncidentDetail');
});

// const hitAlert = {
//   time_of_hit: 0,
//   src_ip: '123.123.123.123',
//   geo_info: {
//     loc: [],
//     org: 'string',
//     city: 'string',
//     country: 'string',
//     region: 'string',
//     hostname: 'string',
//     ip: 'string',
//     timezone: 'string',
//     postal: 'string',
//     asn: {
//       route: 'string',
//       type: 'string',
//       asn: 'string',
//       domain: 'string',
//       name: 'string',
//     },
//     readme: 'string',
//   },
//   is_tor_relay: true,
//   input_channel: 'HTML',
//   src_data: {},
//   useragent: 'string',
//   token_type: 'aws_keys',
// };
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
