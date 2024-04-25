<template>
  <template v-if="isLoading">
    <div class="flex flex-col gap-16 mx-16">
      <BaseSkeletonLoader class="flex-col h-[10vh]" />
      <BaseSkeletonLoader class="flex-col h-[10vh]" />
      <BaseSkeletonLoader class="flex-col h-[10vh]" />
    </div>
    <div class="flex flex-col gap-16">
      <BaseSkeletonLoader class="h-[50svh] w-full" />
      <BaseSkeletonLoader class="h-[20svh] w-full" />
    </div>
  </template>

  <BaseMessageBox
    v-if="error"
    variant="danger"
    message="Oh no! Something went wrong. Please refresh the page or try again later."
  >
  </BaseMessageBox>
  <template v-if="hitsList">
    <!-- conditional { 'hidden md:block': selectedAlert } is a trick for mobile
    to show incident info all screen height -->
    <div
      id="alerts-card-list"
      class="flex-col md:p-16 md:bg-grey-50 md:rounded-xl md:overflow-scroll md:max-h-[60svh]"
      :class="{ 'hidden md:block': selectedAlert }"
    >
      <h2 class="font-semibold leading-5 text-grey-800">Alerts list</h2>
      <!-- TODO: add number of alerts? -->
      <ul class="flex flex-col gap-16">
        <li class="flex items-center justify-between">
          <p class="text-sm text-grey-500">Download:</p>
          <div>
            <BaseButton
              variant="text"
              @click="handleDownloadList(INCIDENT_LIST_EXPORT.CSV)"
              >CSV</BaseButton
            >
            <BaseButton
              variant="text"
              @click="handleDownloadList(INCIDENT_LIST_EXPORT.JSON)"
              >JSON</BaseButton
            >
          </div>
        </li>
        <CardIncident
          v-for="(incident, index) in hitsList"
          :key="index"
          :incident-id="incident.time_of_hit"
          :incident-preview-info="{
            Date: convertUnixTimeStampToDate(incident.time_of_hit),
            IP: incident.src_ip,
            Channel: incident.input_channel,
          }"
          @click="handleSelectAlert(incident)"
        ></CardIncident>
      </ul>
    </div>
    <div>
      <div class="@md:relative grid md:h-[45svh] h-[30svh]">
        <IncidentDetails
          v-if="selectedAlert"
          id="incident_detail"
          :hit-alert="selectedAlert"
          class="absolute top-[80px] left-[0] md:top-[0px] md:relative grid-areas z-10 md:overflow-scroll"
          @close="selectedAlert = null"
        ></IncidentDetails>
        <CustomMap :hits-list="hitsList"></CustomMap>
      </div>
      <BannerCanarytools></BannerCanarytools>
    </div>
  </template>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Ref } from 'vue';
import { useRoute } from 'vue-router';
import { historyToken } from '@/api/main.ts';
import type {
  HistoryTokenBackendType,
  HitsType,
} from '@/components/tokens/types.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';
import CardIncident from '@/components/ui/CardIncident.vue';
import CustomMap from '@/components/ui/CustomMap.vue';
import BannerCanarytools from '@/components/ui/BannerCanarytools.vue';
import IncidentDetails from '@/components/ui/IncidentDetails.vue';
import { downloadAsset } from '@/api/main';
import { INCIDENT_LIST_EXPORT } from '@/components/constants';

const emits = defineEmits(['update-token-title']);

const route = useRoute();

const isLoading = ref(false);
const error = ref(null);
const hitsList: Ref<HitsType[] | undefined> = ref();
const selectedAlert = ref();

onMounted(async () => {
  await fetchTokenHistoryData();
});

async function fetchTokenHistoryData() {
  isLoading.value = true;

  const params = {
    auth: route.params.auth as string,
    token: route.params.token as string,
  };

  try {
    const res = await historyToken(params);
    const historyTokenData = (await res.data) as HistoryTokenBackendType;
    hitsList.value = historyTokenData.hits;
    emits(
      'update-token-title',
      historyTokenData.token_type,
      route.params.token
    );
  } catch (err: any) {
    console.log(err, 'err!');
    error.value = err.toString();
  } finally {
    isLoading.value = false;
  }
}

function handleDownloadList(type: string) {
  const params = {
    fmt: type,
    auth: route.params.auth as string,
    token: route.params.token as string,
  };
  downloadAsset(params)
    .then((res) => {
      window.location.href = res.request.responseURL;
    })
    .catch((err) => {
      console.log(err, 'err');
    })
    .finally(() => {
      console.log('You downloaded the file, yay!');
    });
}

function handleSelectAlert(incident: HitsType) {
  selectedAlert.value = incident;
  const container = document.getElementById('incident_detail');
  container
    ? container.scrollTo({ top: 0, behavior: 'smooth' })
    : window.scrollTo({ top: 0, behavior: 'smooth' });
}
</script>

<style>
.grid-areas {
  grid-area: 1 / 1 / 2 / 2;
}
</style>
