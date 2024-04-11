<template>
  <div
    v-if="isLoading"
    class="loading"
  >
    Loading...
  </div>

  <div
    v-if="error"
    class="error"
  >
    {{ error }}
  </div>
  <template v-if="hitsList">
    <div
      id="alerts-card-list"
      class="flex flex-col md:p-16 md:bg-grey-50 md:rounded-xl md:overflow-scroll md:max-h-[60svh]"
    >
      <h2 class="font-semibold leading-5 text-grey-800">Alerts list</h2>
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
          @click="selectedAlert = incident"
        ></CardIncident>
      </ul>
    </div>
    <div>
      <div class="md:relative md:h-[60svh] h-[30svh]">
        <!-- TODO: add fake map/error handler when map is not loading -->
        <CustomMap :hits-list="hitsList"></CustomMap>
        <IncidentDetails
          v-if="selectedAlert"
          :hit-alert="selectedAlert"
          class="absolute top-[80px] left-[0] md:top-[0px] md:h-[59svh] md:overflow-scroll"
          @close="selectedAlert = null"
        ></IncidentDetails>
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

onMounted(() => {
  fetchTokenHistoryData();
});

async function fetchTokenHistoryData() {
  isLoading.value = true;

  const params = {
    auth: route.params.auth as string,
    token: route.params.token as string,
  };

  historyToken(params)
    .then((res) => {
      const historyTokenData = res.data as HistoryTokenBackendType;
      hitsList.value = historyTokenData.hits;

      emits(
        'update-token-title',
        historyTokenData.token_type,
        route.params.token
      );
    })
    .catch((err) => {
      console.log(err, 'err!');
      isLoading.value = false;
      error.value = err.toString();
    })
    .finally(() => {
      isLoading.value = false;
    });
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
</script>
<style></style>
