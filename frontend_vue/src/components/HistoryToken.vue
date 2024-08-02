<template>
  <template v-if="isLoading">
    <div class="flex flex-col gap-16 mx-16 mt-[60px]">
      <BaseSkeletonLoader
        type="header"
        class="w-[200px]"
      />
      <BaseSkeletonLoader class="h-[10vh]" />
      <BaseSkeletonLoader class="h-[10vh]" />
      <BaseSkeletonLoader class="h-[10vh]" />
    </div>
    <div class="flex flex-col gap-16 mt-[60px]">
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
      class="flex-col md:p-16 md:bg-grey-50 md:rounded-3xl md:overflow-scroll md:max-h-[70svh]"
      :class="{ 'hidden md:block': selectedAlert }"
    >
      <!-- TODO: add number of alerts? -->
      <ul class="flex flex-col h-full gap-16 pb-16">
        <h2 class="font-semibold leading-5 text-grey-800">Alerts list</h2>
        <li
          v-if="hitsList.length === 0"
          class="flex flex-col items-center justify-center flex-grow px-16 py-16 align-middle"
        >
          <p class="text-xl text-center text-grey-400">
            There are no alerts for this Canarytoken.
          </p>
          <img
            :src="getImageUrl(`token_icons/default.png`)"
            alt="No alerts"
            class="grayscale opacity-50 w-[50%] not-sr-only group-hover:opacity-100 sm:block mt-16"
          />
        </li>
        <AlertsListDownload v-else />

        <CardIncident
          v-for="(incident, index) in hitsList"
          :key="index"
          :last-key="index === hitsList.length - 1"
          :incident-id="incident.time_of_hit"
          :incident-preview-info="{
            Date: convertUnixTimeStampToDate(incident.time_of_hit),
            IP: incident.src_ip,
            Channel: incident.input_channel,
          }"
          @click="handleSelectAlert(incident)"
        ></CardIncident>
        <!-- Benner for small screens -->
        <BannerDeviceCanarytools class="flex sm:hidden" />
      </ul>
    </div>
    <div>
      <div
        class="@md:relative md:h-[45svh] h-[30svh]"
        :class="hitsList.length === 0 ? 'hidden sm:grid' : 'grid'"
      >
        <transition name="slide-fade">
          <IncidentDetails
            v-if="selectedAlert"
            id="incident_detail"
            :hit-alert="selectedAlert"
            class="absolute top-[120px] left-[0] md:top-[0px] md:relative grid-areas z-10 md:overflow-scroll w-full sm:w-auto"
            @close="selectedAlert = null"
          ></IncidentDetails>
        </transition>
        <CustomMap :hits-list="hitsList"></CustomMap>
      </div>
      <!-- Benner for larger screens -->
      <BannerDeviceCanarytools class="hidden sm:flex" />
    </div>
  </template>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { historyToken } from '@/api/main.ts';
import getImageUrl from '@/utils/getImageUrl';
import type {
  HistoryTokenBackendType,
  HitsType,
} from '@/components/tokens/types.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';
import CardIncident from '@/components/ui/CardIncident.vue';
import CustomMap from '@/components/ui/CustomMap.vue';
import BannerDeviceCanarytools from '@/components/ui/BannerDeviceCanarytools.vue';
import IncidentDetails from '@/components/ui/IncidentDetails.vue';
import AlertsListDownload from '@/components/ui/AlertsListDownload.vue';
import { addViewTransition } from '@/utils/utils';

const emits = defineEmits(['update-token-title']);

const route = useRoute();
const router = useRouter();

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
    hitsList.value = historyTokenData.history.hits.sort((a, b) => b.time_of_hit - a.time_of_hit);
    
    emits(
      'update-token-title',
      historyTokenData.history.token_type,
      route.params.token
    );
  } catch (err: any) {
    console.log(err, 'err!');
    error.value = err.toString();
    router.push({ name: 'error' });
  } finally {
    isLoading.value = false;
  }
}

async function handleSelectAlert(incident: HitsType) {
  await addViewTransition(() => {
    selectedAlert.value = incident
    const container = document.getElementById('incident_detail');
  container
    ? container.scrollTo({ top: 0, behavior: 'smooth' })
    : window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}
</script>

<style>
.grid-areas {
  grid-area: 1 / 1 / 2 / 2;
}

.slide-fade-enter-active {
  transition: all 0.25s ease;
}
.slide-fade-leave-active {
  transition: all 0.25s ease;
}
.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
</style>
