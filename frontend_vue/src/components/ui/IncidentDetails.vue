<template>
  <div
    class="pb-32 bg-white rounded-3xl"
    :class="{ 'sm:m-8': props.showingMap, 'border shadow-solid-shadow-grey border-grey-100': !props.showingMap }">
    <div class="sticky top-[0px] bg-white h-[4rem] sm:h-40 flex justify-end">
      <button
        v-if="props.showingMap"
        type="button"
        class="px-16"
        @click="emit('close')"
      >
        <font-awesome-icon
          icon="xmark"
          class="w-24 h-24 sm:w-16 sm:h-16 text-grey-400 hover:text-grey-200"
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
                            !isObject(deepnested_val) && isNotEmpty(deepnested_val)
                          "
                          :label="deepnested_key"
                          :value="deepnested_val"
                          class="py-8 ml-24"
                        />
                         <template v-else>
                          <template
                            v-for="(deepestnested_val, deepernested_key) in deepnested_val"
                            :key="deepernested_key"
                          >
                            <IncidentDetailsListItem
                              v-if="
                                !isObject(deepestnested_val) &&
                                isNotEmpty(deepestnested_val)
                              "
                              :label="deepnested_key"
                              :value="deepestnested_val"
                              class="py-8 ml-24"
                            />
                            </template>
                         </template>
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
import { ref, onMounted, watch } from 'vue';
import type { Ref } from 'vue';
import type { HitsType, FormattedHitsType } from '@/components/tokens/types.ts';
import IncidentDetailsListItem from '@/components/ui/IncidentDetailsListItem.vue';
import IncidentDetailsSummary from '@/components/ui/IncidentDetailsSummary.vue';
import { isObject, isNotEmpty } from '@/utils/utils';
import incidentDetailsService from '@/utils/incidentDetailsService.ts'
import {
  formatLabels,
} from '@/utils/incidentUtils';

const props = withDefaults(
  defineProps<{
    hitAlert: HitsType;
    showingMap: boolean;
    tokenType: string;
  }>(), {
    showingMap: true,
  },
);

const emit = defineEmits(['close']);
const builtIncidentDetail: Ref<FormattedHitsType | HitsType | null> = ref(null);
const formattedIncidentDetail = ref({});

onMounted(() => {
  // Map & cleanup hitAlert
  builtIncidentDetail.value = incidentDetailsService(props.hitAlert, props.tokenType);

  // Make the list UI friendly
  formattedIncidentDetail.value = formatLabels(
    builtIncidentDetail.value as FormattedHitsType
  );
});

watch(
  () => props.hitAlert,
  () => {
    // Map & cleanup hitAlert
    builtIncidentDetail.value = incidentDetailsService(props.hitAlert, props.tokenType);
    // Make the list UI friendly
    formattedIncidentDetail.value = formatLabels(
      builtIncidentDetail.value as FormattedHitsType
    );
  }
);
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
