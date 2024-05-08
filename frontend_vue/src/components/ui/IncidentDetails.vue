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
        :input-channel="
          (builtIncidentDetail as FormattedHitsType).basic_info.input_channel
        "
      />
      <!-- Details -->
      <section class="grid md:grid-cols-[auto_1fr] gap-32 mt-32 pl-8">
        <template
          v-for="(val, key) in formattedIncidentDetail"
          :key="key"
        >
          <h3
            v-if="isNotEmpty(key) && isNotEmpty(val)"
            class="text-grey-500"
          >
            {{ key }}:
          </h3>
          <ul
            v-if="isNotEmpty(val)"
            class="flex flex-col gap-16 pb-16 [&:not(:last-child)]:border-b md:ml-32 border-grey-100"
          >
            <IncidentDetailsListItem
              v-if="!isObject(val)"
              :value="val"
            />
            <template v-else>
              <template
                v-for="(nested_val, nested_key) in val"
                :key="nested_key"
              >
                <ul
                  v-if="isNotEmpty(nested_val)"
                  class="break-words"
                >
                  <IncidentDetailsListItem
                    v-if="!isObject(nested_val)"
                    :label="nested_key"
                    :value="nested_val"
                  />
                  <template v-else>
                    <ul>
                      <h3 class="text-grey-500">{{ nested_key }}:</h3>
                      <template
                        v-for="(deepnested_val, deepnested_key) in nested_val"
                        :key="deepnested_key"
                      >
                        <IncidentDetailsListItem
                          v-if="
                            !isObject(nested_val) && isNotEmpty(deepnested_val)
                          "
                          :label="deepnested_key"
                          :value="deepnested_val"
                          class="py-8 ml-24"
                        />
                      </template>
                    </ul>
                    <div class="border-b border-grey-100"></div>
                  </template>
                </ul>
              </template>
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
  isNotEmpty,
  buildIncidentDetails,
} from '@/utils/incidentAlertService';

const props = defineProps<{
  hitAlert: HitsType;
}>();

const emit = defineEmits(['close']);
const builtIncidentDetail: Ref<FormattedHitsType | HitsType | null> = ref(null);
const formattedIncidentDetail = ref({});

onMounted(() => {
  // Map & cleanup hitAlert
  builtIncidentDetail.value = buildIncidentDetails(props.hitAlert);

  // Make the list UI friendly
  formattedIncidentDetail.value = formatLabels(
    builtIncidentDetail.value as FormattedHitsType
  );
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
