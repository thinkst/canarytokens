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
    <ul class="flex flex-col gap-16">
      <CardIncident
        v-for="(incident, index) in hitsList"
        :key="index"
        :incident-id="incident.time_of_hit"
        :incident-preview-info="{
          Date: convertUnixTimeStampToDate(incident.time_of_hit),
          IP: incident.src_ip,
          Channel: incident.input_channel,
        }"
        @click="selectedAlert.value = incident.time_of_hit"
      ></CardIncident>
    </ul>
    <div>
      <!-- TODO: add fake map/error handler when map is not loading -->
      <CustomMap :hits-list="hitsList"></CustomMap>
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
</script>
<style></style>
