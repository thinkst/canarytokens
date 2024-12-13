<template>
  <div v-if="isLoading">
    <BaseSkeletonLoader
      type="rectangle"
      class="md:h-[40svh] h-[30svh]"
    />
  </div>
  <div
    v-if="!isLoading && hitsList.length === 0"
    class="placeholder-map"
  ></div>
  <GMapMap
    v-else
    v-bind="$attrs"
    ref="mapRef"
    :zoom="6"
    :center="center"
    map-type-id="terrain"
    class="grid-areas rounded-2xl"
    :options="options"
  >
    <GMapCluster
      :renderer="{ render }"
      :zoom-on-click="true"
    >
      <GMapMarker
        v-for="(m, index) in markers"
        :key="index"
        :position="m.position"
        :clickable="true"
        :icon="{
          url: getImageUrl('icons/map-pin.png'),
          scaledSize: { width: 60, height: 60 },
          labelOrigin: { x: 16, y: -60 },
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
              Lat: {{ m.position?.lat || '' }}, Lng:
              {{ m.position?.lng || '' }}
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
  ip?: string;
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
const center = ref({ lat: -33.9221, lng: 18.4231 }); // Default to Cape Town

function parseGeoInfoLocation(info: string) {
  const locationArray = info.split(',');
  return {
    lat: parseFloat(locationArray[0]),
    lng: parseFloat(locationArray[1]),
  };
}

const markers: ComputedRef<MarkerType[]> = computed(() => {
  return props.hitsList.filter(function(marker) {
    return (marker.geo_info != null);
  }).map((marker) => {
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

onMounted(() => {
  if (markers.value.length === 0) {
    return;
  }
  if (markers.value.length > 1) {
    return fitMarkerBounds();
  } else if (markers.value.length === 1) {
    if (markers.value[0].position != null) center.value = markers.value[0].position
  }
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
  if (!mapRef.value) {
    return;
  }
  mapRef.value.$mapPromise.then(() => {
    isLoading.value = false;
  });
});

// styles Cluster Marker
const render = ({ count, position }: { count: number; position: string[] }) => {
  // @ts-ignore
  return new window.google.maps.Marker({
    label: {
      text: `${count}`,
      color: 'white',
      fontWeight: '600',
    },
    icon: {
      url: getImageUrl('icons/map-cluster-pin.png'),
      scaledSize: { width: 40, height: 40 },
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
      featureType: 'administrative.country',
      elementType: 'geometry.stroke',
      stylers: [
        {
          lightness: '52',
        },
      ],
    },
    {
      featureType: 'administrative.country',
      elementType: 'labels.text.fill',
      stylers: [
        {
          lightness: '60',
        },
      ],
    },
    {
      featureType: 'administrative.province',
      elementType: 'labels.text.fill',
      stylers: [
        {
          lightness: '24',
        },
      ],
    },
    {
      featureType: 'administrative.locality',
      elementType: 'labels.text.fill',
      stylers: [
        {
          lightness: '29',
        },
      ],
    },
    {
      featureType: 'administrative.locality',
      elementType: 'labels.icon',
      stylers: [
        {
          lightness: '47',
        },
        {
          hue: '#ff0000',
        },
      ],
    },
    {
      featureType: 'landscape',
      elementType: 'all',
      stylers: [
        {
          saturation: 13.400000000000006,
        },
        {
          lightness: 57.599999999999994,
        },
        {
          gamma: 1,
        },
      ],
    },
    {
      featureType: 'poi',
      elementType: 'all',
      stylers: [
        {
          saturation: -1.0989010989011234,
        },
        {
          lightness: 11.200000000000017,
        },
        {
          gamma: 1,
        },
      ],
    },
    {
      featureType: 'road.highway',
      elementType: 'all',
      stylers: [
        {
          saturation: -61.8,
        },
        {
          lightness: 45.599999999999994,
        },
        {
          gamma: 1,
        },
      ],
    },
    {
      featureType: 'road.arterial',
      elementType: 'all',
      stylers: [
        {
          saturation: -100,
        },
        {
          lightness: 51.19999999999999,
        },
        {
          gamma: 1,
        },
      ],
    },
    {
      featureType: 'road.local',
      elementType: 'all',
      stylers: [
        {
          saturation: -100,
        },
        {
          lightness: 52,
        },
        {
          gamma: 1,
        },
      ],
    },
    {
      featureType: 'water',
      elementType: 'all',
      stylers: [
        {
          saturation: -13.200000000000003,
        },
        {
          lightness: 2.4000000000000057,
        },
        {
          gamma: 1,
        },
      ],
    },
    {
      featureType: 'water',
      elementType: 'geometry.fill',
      stylers: [
        {
          lightness: '38',
        },
        {
          saturation: '-55',
        },
      ],
    },
    {
      featureType: 'water',
      elementType: 'labels.text.fill',
      stylers: [
        {
          lightness: '65',
        },
        {
          saturation: '52',
        },
      ],
    },
  ],
};
</script>

<style>
.placeholder-map {
  background-image: url('@/assets/map_placeholder.png');
  background-size: cover;
  background-position: center;
  border-radius: 1.5rem;
  filter: grayscale(1) opacity(0.3);
}

.gm-style-iw-chr > button {
  transform: scale(0.8);
  height: 24px !important;
}

.vue-map {
  @apply rounded-3xl;
}
</style>
