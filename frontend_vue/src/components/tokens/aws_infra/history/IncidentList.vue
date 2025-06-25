<template>
  <IncidentSelectType
    :alerts-list="hitsList"
    @select-option="(value) => handleSelectOption(value)"
  />
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
        :asset-preview-info="assetPreviewInfo(group[0])"
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
        v-for="(incident, index) in filteredIncidentsListByAssetName"
        :key="index"
        :last-key="index === filteredIncidentsListByAssetName.length - 1"
        :incident-id="incident.time_of_hit"
        :incident-preview-info="incidentPreviewInfo(incident)"
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
  const filteredListByType = hitsList.history.hits.filter(
    (hit) =>
      (hit.additional_info as AdditionalInfoAWSInfraType).decoy_resource
        .asset_type === selectedAssetType.value
  );

  const groupedListByAssetName = Object.groupBy(
    filteredListByType,
    (incident: HitsType) =>
      (incident.additional_info as AdditionalInfoAWSInfraType).decoy_resource[
        'Asset Name'
      ]
  );

  return groupedListByAssetName as incidentsByTypeAndAssetNameType;
});

const filteredIncidentsListByAssetName = computed(() => {
  return hitsList.history.hits.filter(
    (hit) =>
      (hit.additional_info as AdditionalInfoAWSInfraType).decoy_resource[
        'Asset Name'
      ] === selectedAssetName.value
  );
});

function assetPreviewInfo(hit: HitsType) {
  return {
    asset_name: (hit.additional_info as AdditionalInfoAWSInfraType)
      .decoy_resource['Asset Name'],
    last_date_of_hit: hit.time_of_hit
      ? convertUnixTimeStampToDate(hit.time_of_hit)
      : null,
  };
}

function incidentPreviewInfo(hit: HitsType) {
  return {
    Date: convertUnixTimeStampToDate(hit.time_of_hit),
    IP: hit.src_ip,
    'Event Name': (hit.additional_info as AdditionalInfoAWSInfraType).event[
      'Event Name'
    ],
  };
}

function handleSelectOption(value: string) {
  selectedAssetName.value = '';
  selectedAssetType.value = value;
}

function handleSelectAssetName(incident: HitsType) {
  animateList('assetSection', () => {
    selectedAssetName.value = (
      incident.additional_info as AdditionalInfoAWSInfraType
    ).decoy_resource['Asset Name'];
  });
}

function handleSelectAlert(incident: HitsType) {
  emits('select-alert', incident);
}

function handleBackButton() {
  animateList('', () => {
    selectedAssetName.value = '';
  });
}

function animateList(exitList: string, callback: () => void) {
  if (exitList === 'assetSection') {
    assetSection.value?.classList.add('exit-right');
  } else {
    incidentsSection.value?.classList.add('exit-left');
  }
  setTimeout(() => {
    callback();
  }, 250);
}
</script>

<style lang="scss" scoped>
@keyframes exitRight {
  from {
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(-200px);
  }
}

@keyframes exitLeft {
  from {
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(200px);
  }
}

.exit-left {
  animation: exitLeft 0.25s ease-in-out forwards;
}

.exit-right {
  animation: exitRight 0.25s ease-in-out forwards;
}
</style>
