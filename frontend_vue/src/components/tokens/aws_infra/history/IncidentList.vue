<template>
  <SelectIncidentType
    :alerts-list="hitsList"
    @select-option="(value) => handleSelectOption(value)"
  />
  <section
    v-if="!selectedAssetName"
    ref="asset-section"
  >
    <h3 class="p-8">{{ labelSelectedAssetType }} alerts list</h3>
    <ul class="flex flex-col h-full gap-16 pb-16">
      <IncidentCardAsset
        v-for="(group, index) in groupedIncidentsList"
        :key="group[0].time_of_hit"
        :last-key="index === Object.values(groupedIncidentsList).length - 1"
        :asset-preview-info="getAssetPreviewInfo(group[0])"
        :asset-type="getAssetType(group[0])"
        @click="handleSelectAssetGroup(group[0])"
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
        :incident-preview-info="getIncidentPreviewInfo(incident)"
        @click="handleSelectAlert(incident)"
      ></CardIncident>
    </ul>
  </section>
</template>

<script lang="ts" setup>
import { ref, computed, useTemplateRef } from 'vue';
import SelectIncidentType from '@/components/tokens/aws_infra/history/SelectIncidentType.vue';
import type {
  HitsType,
  AdditionalInfoType,
} from '@/components/tokens/types.ts';
import { ASSET_LABEL } from '@/components/tokens/aws_infra/constants.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';
import IncidentCardAsset from '@/components/tokens/aws_infra/history/IncidentCardAsset.vue';
import CardIncident from '@/components/ui/CardIncident.vue';

const props = defineProps<{
  hitsList: HitsType[];
}>();

type groupedIncidentsListType = {
  [key: string]: HitsType[];
};

const ALL_DECOYS = 'all_decoys';

const emits = defineEmits(['select-alert']);

const hitsList: HitsType[] = props.hitsList;
const selectedAssetType = ref('');
const selectedAssetName = ref('');
const assetSection = useTemplateRef('asset-section');
const incidentsSection = useTemplateRef('incidents-section');

const getAssetName = (hit: HitsType) =>
  (hit.additional_info as AdditionalInfoType).decoy_resource?.['Asset Name'];

const getAssetType = (hit: HitsType) =>
  (hit.additional_info as AdditionalInfoType).decoy_resource?.asset_type ||
  'Unknown';

const labelSelectedAssetType = computed(() => {
  return Object.keys(ASSET_LABEL).includes(selectedAssetType.value)
    ? //@ts-ignore-error
      // TODO: we are refactoring the constants on another diff, so this will be fixed
      ASSET_LABEL[selectedAssetType.value]
    : 'All decoys';
});

const groupedIncidentsList = computed((): groupedIncidentsListType => {
  const listToProcess =
    selectedAssetType.value === ALL_DECOYS
      ? props.hitsList
      : props.hitsList.filter(
          (hit) => getAssetType(hit) === selectedAssetType.value
        );

  const groupedList = groupListByAssetName(listToProcess);
  const orderedTimeList = orderListByTimeStamp(groupedList);

  return orderedTimeList;
});

function groupListByAssetName(list: HitsType[]) {
  return list.reduce((acc: groupedIncidentsListType, incident) => {
    const assetName = getAssetName(incident);
    if (assetName) {
      acc[assetName] = acc[assetName] || [];
      acc[assetName].push(incident);
    }
    return acc;
  }, {} as groupedIncidentsListType);
}

function orderListByTimeStamp(list: groupedIncidentsListType) {
  return Object.fromEntries(
    // Sort incidents within group
    Object.entries(list)
      .map(([assetName, incidents]) => [
        assetName,
        incidents.sort((a, b) => b.time_of_hit - a.time_of_hit),
      ])
      // Sort groups by their most recent incident
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .sort(([_assetNameA, incidentsA], [_assetNameB, incidentsB]) => {
        const mostRecentA = (incidentsA as HitsType[])[0]?.time_of_hit || 0;
        const mostRecentB = (incidentsB as HitsType[])[0]?.time_of_hit || 0;
        return mostRecentB - mostRecentA;
      })
  );
}

const filteredIncidentsListByAssetName = computed(() => {
  return hitsList.filter(
    (hit) => getAssetName(hit) === selectedAssetName.value
  );
});

function getAssetPreviewInfo(hit: HitsType) {
  const assetName = getAssetName(hit) || '';
  const assetType = getAssetType(hit) || 'Unknown';

  //@ts-ignore-error
  const label = assetType && ASSET_LABEL[assetType];

  return {
    asset_type: label || assetType,
    asset_name: assetName,
    last_date_of_hit: hit.time_of_hit
      ? convertUnixTimeStampToDate(hit.time_of_hit)
      : null,
  };
}

function getIncidentPreviewInfo(hit: HitsType) {
  const eventName = (hit.additional_info as AdditionalInfoType)?.event?.[
    'Event Name'
  ];

  return {
    Date: convertUnixTimeStampToDate(hit.time_of_hit),
    IP: hit.src_ip,
    'Event Name': eventName || 'Unknown',
  };
}

const handleSelectOption = (value: string) => {
  selectedAssetName.value = '';
  selectedAssetType.value = value === ALL_DECOYS ? ALL_DECOYS : value;
};

function handleSelectAssetGroup(incident: HitsType) {
  const assetName = (incident.additional_info as AdditionalInfoType)
    ?.decoy_resource?.['Asset Name'];

  animateList('assetSection', () => {
    selectedAssetName.value = assetName || '';
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
