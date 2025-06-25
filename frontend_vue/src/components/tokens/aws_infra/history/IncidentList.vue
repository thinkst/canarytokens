<template>
  <IncidentSelectType @select-option="(value) => handleSelectOption(value)" />
  <section
    v-if="!selectedAssetName"
    ref="asset-section"
  >
    <h3 class="p-8">{{ selectedAssetType }} alerts list</h3>
    <ul class="flex flex-col h-full gap-16 pb-16">
      <IncidentCardAsset
        v-for="(group, index) in incidentsByTypeAndAssetName"
        :key="group[0].time_of_hit"
        :last-key="
          index === Object.values(incidentsByTypeAndAssetName).length - 1
        "
        :asset-preview-info="previewInfo(group[0])"
        :asset-type="selectedAssetType"
        @click="handleSelectAssetName(group[0])"
      />
    </ul>
  </section>
  <section
    v-else
    ref="incidents-section"
  >
    <BaseButton
      type="button"
      variant="text"
      icon="angle-left"
      @click="handleBackButton"
      >Back</BaseButton
    >
    <h3 class="p-8 text-ellipsis overflow-hidden whitespace-nowrap">
      <span class="text-grey">Alerts for:</span>
      {{ selectedAssetName }}
    </h3>
    <ul class="flex flex-col h-full gap-16 pb-16">
      <CardIncident
        v-for="(incident, index) in filteredIncidentsListByName"
        :key="index"
        :last-key="index === filteredIncidentsListByName.length - 1"
        :incident-id="incident.time_of_hit"
        :incident-preview-info="{
          Date: convertUnixTimeStampToDate(incident.time_of_hit),
          IP: incident.src_ip,
          Channel: incident.input_channel,
        }"
        @click="handleSelectAlert(incident)"
      ></CardIncident>
    </ul>
  </section>
</template>

<script lang="ts" setup>
import { ref, computed, useTemplateRef } from 'vue';
import IncidentSelectType from '@/components/tokens/aws_infra/history/IncidentSelectType.vue';
import type {
  HistoryTokenBackendType,
  HitsType,
  AdditionalInfoAWSInfraType,
} from '@/components/tokens/types.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';
import IncidentCardAsset from '@/components/tokens/aws_infra/history/IncidentCardAsset.vue';
import CardIncident from '@/components/ui/CardIncident.vue';

import { dummyData } from '@/components/tokens/aws_infra/history/dummyData.js';

// const props = defineProps<{
//     hitsList: HistoryTokenBackendType;
// }>();

type incidentsByTypeAndAssetNameType = {
  [key: string]: HitsType[];
};

const emits = defineEmits(['select-alert']);

const hitsList: HistoryTokenBackendType = dummyData; // props.hitsList;
const selectedAssetType = ref('');
const selectedAssetName = ref('');
const assetSection = useTemplateRef('asset-section');
const incidentsSection = useTemplateRef('incidents-section');

const incidentsByTypeAndAssetName = computed(() => {
  const filteredList = hitsList.history.hits.filter(
    (hit) =>
      (hit.additional_info as AdditionalInfoAWSInfraType).decoy_resource
        .asset_type === selectedAssetType.value
  );

  const groupedList = Object.groupBy(
    filteredList,
    (alert: HitsType) =>
      (alert.additional_info as AdditionalInfoAWSInfraType).decoy_resource[
        'Asset Name'
      ]
  );

  return groupedList as incidentsByTypeAndAssetNameType;
});

const filteredIncidentsListByName = computed(() => {
  return hitsList.history.hits.filter(
    (hit) =>
      (hit.additional_info as AdditionalInfoAWSInfraType).decoy_resource[
        'Asset Name'
      ] === selectedAssetName.value
  );
});

function previewInfo(hit: HitsType) {
  return {
    asset_name: (hit.additional_info as AdditionalInfoAWSInfraType)
      .decoy_resource['Asset Name'],
    time_of_hit: hit.time_of_hit
      ? convertUnixTimeStampToDate(hit.time_of_hit)
      : null,
  };
}

function handleSelectOption(value: string) {
  selectedAssetName.value = '';
  selectedAssetType.value = value;
}

function handleSelectAssetName(incident: HitsType) {
  (selectedAssetName.value = (
    incident.additional_info as AdditionalInfoAWSInfraType
  ).decoy_resource['Asset Name']),
    console.log('Selected Alert:', selectedAssetName.value);
}

function handleSelectAlert(incident: HitsType) {
  emits('select-alert', incident);
  console.log('Selected Alert:', incident);
}

function handleBackButton() {
  selectedAssetName.value = '';
}
</script>

<style lang="scss" scoped>
@keyframes leaveLeft {
  from {
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-100%);
  }
}

@keyframes leaveLeft {
  from {
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}

@keyframes enterLeft {
  from {
    opacity: 0;
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes enterRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.exit-left {
  animation: leaveLeft 0.3s ease-in-out forwards;
}

.exit-right {
  animation: leaveLeft 0.3s ease-in-out forwards;
}

.enter-left {
  animation: enterLeft 0.3s ease-in-out forwards;
}

.enter-right {
  animation: enterRight 0.3s ease-in-out forwards;
}
</style>
