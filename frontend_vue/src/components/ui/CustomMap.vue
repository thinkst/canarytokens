<template>
  <div v-if="isLoading">Loading map...</div>
  <GMapMap
    v-bind="$attrs"
    ref="mapRef"
    :zoom="7"
    :center="center"
    map-type-id="terrain"
    class="grid-areas"
    :options="options"
    ><GMapCluster
      :renderer="{ render }"
      :zoom-on-click="true"
    >
      <GMapMarker
        v-for="(m, index) in markers"
        :key="index"
        :position="m.position"
        :clickable="true"
        :icon="{
          url: getImageUrl('icons/pin.png'),
          scaledSize: { width: 30, height: 30 },
          labelOrigin: { x: 16, y: -30 },
        }"
        @click="handleOpenMarker(m.id)"
      >
        <GMapInfoWindow
          :closeclick="true"
          :opened="openedMarkerID === m.id"
          class="px-8 py-8"
          @closeclick="handleOpenMarker(null)"
        >
          <ul>
            <li>
              From IP: <span class="font-medium">{{ m.ip }}</span>
            </li>
            <li class="pb-8">{{ m.hostname }}</li>
            <li class="font-medium">{{ m.date }}</li>
            <li class="pt-8">{{ m.city }}, {{ m.country }}</li>
            <li>
              Lat: {{ m.position?.lat || '' }}, Lng: {{ m.position?.lng || '' }}
            </li>
          </ul>
        </GMapInfoWindow>
      </GMapMarker>
    </GMapCluster>
  </GMapMap>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import type { ComputedRef } from 'vue';
import type { HitsType } from '@/components/tokens/types.ts';
import { convertUnixTimeStampToDate } from '@/utils/utils';
import getImageUrl from '@/utils/getImageUrl';

type MarkerType = {
  id: number;
  ip: string;
  hostname?: string;
  city?: string;
  country?: string;
  date: string;
  position: { lat: number; lng: number } | undefined;
};

const props = defineProps<{
  hitsList: HitsType[];
}>();

const isLoading = ref(true);
const openedMarkerID = ref();
const mapRef = ref();
const center = ref({ lat: 0, lng: 0 });

function parseGeoInfoLocation(info: string) {
  const locationArray = info.split(',');
  return {
    lat: parseFloat(locationArray[0]),
    lng: parseFloat(locationArray[1]),
  };
}

onMounted(() => {
  if (props.hitsList.length > 1) {
    return fitMarkerBounds();
  } else if (props.hitsList.length === 1) {
    center.value = parseGeoInfoLocation(
      props.hitsList[0].geo_info.loc as string
    );
  }
});

const markers: ComputedRef<MarkerType[]> = computed(() => {
  return props.hitsList.map((marker) => {
    return {
      id: marker.time_of_hit,
      ip: marker.geo_info.ip,
      hostname: marker.geo_info.hostname,
      city: marker.geo_info.city,
      country: marker.geo_info.country,
      date: convertUnixTimeStampToDate(marker.time_of_hit),
      position: marker.geo_info.loc
        ? parseGeoInfoLocation(marker.geo_info.loc)
        : undefined,
    };
  });
});

function handleOpenMarker(id: number | null) {
  openedMarkerID.value = id;
}

async function fitMarkerBounds() {
  const googleMapInstance = await mapRef.value.$mapPromise;
  // @ts-ignore
  const bounds = new window.google.maps.LatLngBounds();
  markers.value.forEach((marker) => {
    bounds.extend(marker.position);
  });
  googleMapInstance.fitBounds(bounds);
}

watch(mapRef, () => {
  mapRef.value.$mapPromise.then(() => {
    isLoading.value = false;
  });
});

// styles Cluster Marker
const render = ({ count, position }: { count: string; position: string[] }) => {
  // @ts-ignore
  return new window.google.maps.Marker({
    label: {
      text: `${count}`,
      color: 'white',
      fontWeight: '600',
    },
    position,
    zIndex: 1000 + count,
  });
};

const options = {
  zoomControl: true,
  mapTypeControl: false,
  streetViewControl: false,
  rotateControl: true,
  fullscreenControl: false,
  styles: [
    {
      featureType: 'all',
      elementType: 'geometry',
      stylers: [
        {
          color: '#202c3e',
        },
      ],
    },
    {
      featureType: 'all',
      elementType: 'labels.text.fill',
      stylers: [
        {
          gamma: 0.01,
        },
        {
          lightness: 20,
        },
        {
          weight: '1.39',
        },
        {
          color: '#ffffff',
        },
      ],
    },
    {
      featureType: 'all',
      elementType: 'labels.text.stroke',
      stylers: [
        {
          weight: '0.96',
        },
        {
          saturation: '9',
        },
        {
          visibility: 'on',
        },
        {
          color: '#000000',
        },
      ],
    },
    {
      featureType: 'all',
      elementType: 'labels.icon',
      stylers: [
        {
          visibility: 'off',
        },
      ],
    },
    {
      featureType: 'landscape',
      elementType: 'geometry',
      stylers: [
        {
          lightness: 30,
        },
        {
          saturation: '9',
        },
        {
          color: '#00a287',
        },
      ],
    },
    {
      featureType: 'poi',
      elementType: 'geometry',
      stylers: [
        {
          saturation: 20,
        },
      ],
    },
    {
      featureType: 'poi.park',
      elementType: 'all',
      stylers: [
        {
          saturation: '-16',
        },
        {
          lightness: '6',
        },
        {
          gamma: '1.00',
        },
        {
          color: '#00a287',
        },
      ],
    },
    {
      featureType: 'poi.park',
      elementType: 'geometry',
      stylers: [
        {
          lightness: 20,
        },
        {
          saturation: -20,
        },
        {
          visibility: 'simplified',
        },
      ],
    },
    {
      featureType: 'road',
      elementType: 'geometry',
      stylers: [
        {
          lightness: 10,
        },
        {
          saturation: -30,
        },
        {
          visibility: 'simplified',
        },
      ],
    },
    {
      featureType: 'road',
      elementType: 'geometry.fill',
      stylers: [
        {
          color: '#00846e',
        },
      ],
    },
    {
      featureType: 'road',
      elementType: 'geometry.stroke',
      stylers: [
        {
          saturation: 25,
        },
        {
          lightness: 25,
        },
        {
          weight: '0.01',
        },
      ],
    },
    {
      featureType: 'water',
      elementType: 'all',
      stylers: [
        {
          lightness: -20,
        },
        {
          color: '#041f20',
        },
      ],
    },
  ],
};
</script>
